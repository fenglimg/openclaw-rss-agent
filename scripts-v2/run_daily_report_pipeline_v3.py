#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
from pathlib import Path

import requests

ROOT = Path('.')
PAYLOAD = ROOT / 'test-output/daily-payload-v2.json'
PACKAGE = ROOT / 'test-output/daily-news-package-v1.json'
REPORT = ROOT / 'outputs/daily-report-zh-news-v3.md'
CHUNKS = ROOT / 'test-output/discord-chunked-delivery-zh-news-v3.json'
DELIVERY = ROOT / 'test-output/discord-delivery-zh-news-v3.json'
X_AUTHOR_SIGNALS = ROOT / 'test-output/x-author-signals-v1.json'
X_LINKED_OBJECTS = ROOT / 'test-output/x-linked-objects-v1.json'
X_CANDIDATE_BOOSTS = ROOT / 'test-output/x-candidate-boosts-v1.json'
CHANNEL_ID = '1484951098660753558'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--payload', default=str(PAYLOAD))
    parser.add_argument('--package', default=str(PACKAGE))
    parser.add_argument('--report', default=str(REPORT))
    parser.add_argument('--chunks', default=str(CHUNKS))
    parser.add_argument('--delivery', default=str(DELIVERY))
    parser.add_argument('--channel-id', default=CHANNEL_ID)
    parser.add_argument('--x-mode', choices=['auto', 'mock', 'contract', 'off'], default='auto')
    parser.add_argument('--skip-payload-build', action='store_true')
    parser.add_argument('--skip-send', action='store_true')
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


def run_step(command: list):
    subprocess.run(command, check=True)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return {}


def refresh_x_contracts(mode: str) -> dict:
    if mode == 'off':
        return {'mode': 'off', 'refreshed': False, 'reason': 'x disabled by flag'}
    if mode == 'mock':
        run_step(['python3', 'scripts-v2/build_x_mock_collector_v1.py'])
        return {'mode': 'mock', 'refreshed': True, 'reason': 'forced mock rebuild'}
    if mode == 'contract':
        return {'mode': 'contract', 'refreshed': False, 'reason': 'use existing contract outputs as-is'}

    author_data = load_json(X_AUTHOR_SIGNALS)
    linked_data = load_json(X_LINKED_OBJECTS)
    boost_data = load_json(X_CANDIDATE_BOOSTS)
    statuses = {
        author_data.get('status'),
        linked_data.get('status'),
        boost_data.get('status'),
    }
    item_count = sum(len(data.get('items', [])) for data in (author_data, linked_data, boost_data))
    if item_count == 0 or 'skeleton-no-backend' in statuses:
        run_step(['python3', 'scripts-v2/build_x_mock_collector_v1.py'])
        return {'mode': 'auto', 'refreshed': True, 'reason': 'empty or skeleton X contract files replaced with mock signals'}
    return {'mode': 'auto', 'refreshed': False, 'reason': 'existing X contract outputs already populated'}


def send_chunks(chunks: list, channel_id: str):
    token, source = resolve_token()
    if not token:
        return {
            'ok': False,
            'status': 'no-token',
            'chunk_count': len(chunks),
            'token_source': None,
            'sent': [],
            'failed_chunks': [],
        }

    sent = []
    failed = []
    for index, chunk in enumerate(chunks, start=1):
        response = requests.post(
            f'https://discord.com/api/v10/channels/{channel_id}/messages',
            headers={'Authorization': f'Bot {token}', 'Content-Type': 'application/json'},
            json={'content': chunk},
            timeout=60,
        )
        if response.ok:
            body = response.json()
            sent.append({
                'index': index,
                'length': len(chunk),
                'status': 'sent',
                'message_id': body.get('id'),
                'channel_id': body.get('channel_id'),
            })
            continue
        failed.append({
            'index': index,
            'length': len(chunk),
            'status': 'failed',
            'http_status': response.status_code,
            'body': response.text[:1000],
        })
        break

    return {
        'ok': len(failed) == 0,
        'status': 'sent' if len(failed) == 0 else 'partial-failure',
        'chunk_count': len(chunks),
        'chunks_sent': len(sent),
        'token_source': source,
        'message_ids': [item['message_id'] for item in sent],
        'sent': sent,
        'failed_chunks': failed,
    }


def summarize_package(path: str) -> dict:
    package = json.loads(Path(path).read_text(encoding='utf-8'))
    sections = package.get('sections', {})
    lead = sections.get('lead', [])
    x_lane = ((package.get('desk') or {}).get('x_signal_lane') or {})
    return {
        'package_file': path,
        'edition': (package.get('meta') or {}).get('edition_label'),
        'lead_names': [item.get('name') for item in lead],
        'lead_count': len(lead),
        'brief_count': len(sections.get('briefs', [])),
        'official_count': len(sections.get('official_watch', [])),
        'hold_count': len(sections.get('backlog', [])),
        'front_page_balanced': ((package.get('desk') or {}).get('front_page_balance') or {}).get('balanced'),
        'x_mode': x_lane.get('mode_label'),
        'x_matched_item_count': x_lane.get('matched_item_count', 0),
        'x_matched_items': x_lane.get('matched_items', []),
        'x_risk_items': x_lane.get('risk_items', []),
    }


def main():
    args = parse_args()
    x_refresh = refresh_x_contracts(args.x_mode)

    if not args.skip_payload_build:
        run_step(['python3', 'scripts-v2/build_daily_payload_v2.py'])

    run_step([
        'python3',
        'scripts-v2/build_daily_news_package_v1.py',
        '--input',
        args.payload,
        '--output',
        args.package,
    ])
    run_step([
        'python3',
        'scripts-v2/render_daily_report_news_zh_v3.py',
        '--input',
        args.package,
        '--output',
        args.report,
    ])

    with Path(args.chunks).open('w', encoding='utf-8') as handle:
        subprocess.run(
            ['python3', 'scripts-v2/discord_chunked_delivery_v1.py', args.report],
            check=True,
            text=True,
            stdout=handle,
        )

    chunk_data = json.loads(Path(args.chunks).read_text(encoding='utf-8'))
    chunks = chunk_data.get('chunks', [])
    package_summary = summarize_package(args.package)

    if args.skip_send:
        result = {
            'ok': True,
            'status': 'prepared',
            'report': args.report,
            'chunks_file': args.chunks,
            'delivery_file': args.delivery,
            'chunk_count': len(chunks),
            'chunks_sent': 0,
            'token_source': None,
            'message_ids': [],
            'sent': [],
            'failed_chunks': [],
        }
    else:
        result = send_chunks(chunks, args.channel_id)
        result.update({
            'report': args.report,
            'chunks_file': args.chunks,
            'delivery_file': args.delivery,
        })

    result.update(package_summary)
    result['x_refresh'] = x_refresh
    Path(args.delivery).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
