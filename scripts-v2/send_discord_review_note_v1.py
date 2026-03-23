#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path

import requests


OUTPUT = Path('test-output/discord-review-note-v1.json')
CHANNEL_ID = '1484951098660753558'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--channel-id', default=CHANNEL_ID)
    parser.add_argument('--task', required=True)
    parser.add_argument('--status', choices=['review-ready', 'blocked', 'failed'], required=True)
    parser.add_argument('--tests', required=True)
    parser.add_argument('--artifacts', required=True)
    parser.add_argument('--recommend-review', choices=['yes', 'no'], required=True)
    parser.add_argument('--output', default=str(OUTPUT))
    return parser.parse_args()


def resolve_token():
    for key in ('DISCORD_BOT_TOKEN_SILIJIAN', 'DISCORD_BOT_TOKEN_MAIN', 'DISCORD_BOT_TOKEN'):
        value = os.environ.get(key)
        if value:
            return value, f'env.{key}'

    cfg_path = Path('/root/.openclaw/config.json')
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text(encoding='utf-8'))
            accounts = (((cfg.get('channels') or {}).get('discord') or {}).get('accounts') or {})
            for key in ('silijian', 'main'):
                account = accounts.get(key)
                if account and account.get('token'):
                    return account['token'], f'config.channels.discord.accounts.{key}'
        except Exception:
            pass
    return None, None


def build_message(task: str, status: str, tests: str, artifacts: str, recommend_review: str) -> str:
    return (
        f'[ACP] {task}\n'
        f'status={status} | tests={tests} | artifacts={artifacts} | recommend_review={recommend_review}'
    )


def main():
    args = parse_args()
    token, source = resolve_token()
    message = build_message(args.task, args.status, args.tests, args.artifacts, args.recommend_review)
    if not token:
        result = {
            'ok': False,
            'status': 'no-token',
            'channel_id': args.channel_id,
            'message': message,
            'token_source': None,
        }
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    response = requests.post(
        f'https://discord.com/api/v10/channels/{args.channel_id}/messages',
        headers={'Authorization': f'Bot {token}', 'Content-Type': 'application/json'},
        json={'content': message},
        timeout=60,
    )
    result = {
        'ok': response.ok,
        'status': 'sent' if response.ok else 'failed',
        'channel_id': args.channel_id,
        'message': message,
        'token_source': source,
        'http_status': response.status_code,
        'response_excerpt': response.text[:1000],
    }
    if response.ok:
        body = response.json()
        result['message_id'] = body.get('id')
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
