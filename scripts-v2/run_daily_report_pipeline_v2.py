#!/usr/bin/env python3
import json
import os
import subprocess
from pathlib import Path

import requests

ROOT = Path('.')
REPORT = ROOT / 'outputs/daily-report-zh-from-payload-v2.md'
CHUNKS = ROOT / 'test-output/discord-chunked-delivery-zh-v2.json'
DELIVERY = ROOT / 'test-output/discord-delivery-zh-result-v2.json'
CHANNEL_ID = '1484951098660753558'


def resolve_token():
    for key in ('DISCORD_BOT_TOKEN_SILIJIAN', 'DISCORD_BOT_TOKEN_MAIN', 'DISCORD_BOT_TOKEN'):
        v = os.environ.get(key)
        if v:
            return v, f'env.{key}'
    return None, None


def main():
    subprocess.run(['python3', 'scripts-v2/build_daily_payload_v1.py'], check=True)
    subprocess.run(['python3', 'scripts-v2/transform_daily_payload_to_zh_v2.py'], check=True)
    with CHUNKS.open('w', encoding='utf-8') as f:
        subprocess.run(
            ['python3', 'scripts-v2/discord_chunked_delivery_v1.py', str(REPORT)],
            check=True,
            text=True,
            stdout=f,
        )

    data = json.loads(CHUNKS.read_text(encoding='utf-8'))
    chunks = data.get('chunks', [])
    token, source = resolve_token()
    if not token:
        result = {'ok': False, 'status': 'no-token', 'chunk_count': len(chunks), 'token_source': None}
        DELIVERY.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    sent = []
    failed = []
    for idx, chunk in enumerate(chunks, start=1):
        r = requests.post(
            f'https://discord.com/api/v10/channels/{CHANNEL_ID}/messages',
            headers={'Authorization': f'Bot {token}', 'Content-Type': 'application/json'},
            json={'content': chunk},
            timeout=60,
        )
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
        'report': str(REPORT),
        'chunks_file': str(CHUNKS),
        'delivery_file': str(DELIVERY),
        'chunk_count': len(chunks),
        'chunks_sent': len(sent),
        'token_source': source,
        'message_ids': [x['message_id'] for x in sent],
        'sent': sent,
        'failed_chunks': failed,
    }
    DELIVERY.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
