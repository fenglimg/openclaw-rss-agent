#!/usr/bin/env python3
import json
import os
from pathlib import Path

import requests

INPUT = Path('test-output/discord-chunked-delivery-v1.json')
OUTPUT = Path('test-output/discord-delivery-result-v1.json')
CHANNEL_ID = '1484951098660753558'


def resolve_token():
    for key in ('DISCORD_BOT_TOKEN_SILIJIAN', 'DISCORD_BOT_TOKEN_MAIN', 'DISCORD_BOT_TOKEN'):
        val = os.environ.get(key)
        if val:
            return val, f'env.{key}'

    cfg_path = Path('/root/.openclaw/config.json')
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text(encoding='utf-8'))
            accounts = (((cfg.get('channels') or {}).get('discord') or {}).get('accounts') or {})
            for key in ('silijian', 'main'):
                acc = accounts.get(key)
                if acc and acc.get('token'):
                    return acc['token'], f'config.channels.discord.accounts.{key}'
            for key, acc in accounts.items():
                if acc and acc.get('token'):
                    return acc['token'], f'config.channels.discord.accounts.{key}'
        except Exception:
            pass
    return None, None


def send_chunk(token, channel_id, content):
    r = requests.post(
        f'https://discord.com/api/v10/channels/{channel_id}/messages',
        headers={
            'Authorization': f'Bot {token}',
            'Content-Type': 'application/json',
        },
        json={'content': content},
        timeout=60,
    )
    return r


def main():
    if not INPUT.exists():
        raise SystemExit('missing chunk input')
    data = json.loads(INPUT.read_text(encoding='utf-8'))
    chunks = data.get('chunks', [])
    token, source = resolve_token()
    if not token:
        result = {
            'ok': False,
            'status': 'no-token',
            'input': str(INPUT),
            'chunk_count': len(chunks),
            'token_source': None,
        }
        OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    sent = []
    failed = []
    for idx, chunk in enumerate(chunks, start=1):
        r = send_chunk(token, CHANNEL_ID, chunk)
        if r.ok:
            body = r.json()
            sent.append({
                'index': idx,
                'length': len(chunk),
                'status': 'sent',
                'message_id': body.get('id'),
                'channel_id': body.get('channel_id'),
            })
        else:
            failed.append({
                'index': idx,
                'length': len(chunk),
                'status': 'failed',
                'http_status': r.status_code,
                'body': r.text[:1000],
            })
            break

    result = {
        'ok': len(failed) == 0,
        'status': 'sent' if len(failed) == 0 else 'partial-failure',
        'input': str(INPUT),
        'chunk_count': len(chunks),
        'chunks_sent': len(sent),
        'token_source': source,
        'message_ids': [x['message_id'] for x in sent],
        'sent': sent,
        'failed_chunks': failed,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
