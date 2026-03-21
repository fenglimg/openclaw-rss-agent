#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent


def run_json(cmd):
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)


def run_text(cmd):
    return subprocess.check_output(cmd, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    ap.add_argument('--state', required=True)
    ap.add_argument('--window-hours', type=int, default=24)
    ap.add_argument('--limit-per-feed', type=int, default=10)
    ap.add_argument('--digest-title', default='📡 RSS Digest')
    ap.add_argument('--max-items', type=int, default=10)
    ap.add_argument('--write-state', action='store_true')
    ap.add_argument('--output-json')
    args = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix='rss-agent-') as tmp:
        fetched = os.path.join(tmp, 'fetched.json')
        deduped = os.path.join(tmp, 'deduped.json')
        triaged = os.path.join(tmp, 'triaged.json')

        data = run_json([
            sys.executable, str(BASE / 'fetch_feeds.py'),
            '--config', args.config,
            '--limit-per-feed', str(args.limit_per_feed),
        ])
        with open(fetched, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        cmd = [
            sys.executable, str(BASE / 'dedupe.py'),
            '--items', fetched,
            '--state', args.state,
            '--window-hours', str(args.window_hours),
        ]
        if args.write_state:
            cmd.append('--write-state')
        deduped_data = run_json(cmd)
        with open(deduped, 'w', encoding='utf-8') as f:
            json.dump(deduped_data, f, ensure_ascii=False, indent=2)

        triaged_data = run_json([
            sys.executable, str(BASE / 'triage_items.py'),
            '--input', deduped,
        ])
        with open(triaged, 'w', encoding='utf-8') as f:
            json.dump(triaged_data, f, ensure_ascii=False, indent=2)

        digest = run_text([
            sys.executable, str(BASE / 'build_digest.py'),
            '--input', triaged,
            '--title', args.digest_title,
            '--max-items', str(args.max_items),
        ])

        result = {
            'ok': True,
            'fetched_count': data.get('count', 0),
            'new_count': deduped_data.get('counts', {}).get('new', 0),
            'counts': deduped_data.get('counts', {}),
            'triage_counts': triaged_data.get('counts', {}),
            'feed_health': data.get('feed_health', []),
            'digest': digest,
            'items': triaged_data.get('items', []),
            'send_items': [x for x in triaged_data.get('items', []) if x.get('triage', {}).get('decision') == 'send'],
            'digest_items': [x for x in triaged_data.get('items', []) if x.get('triage', {}).get('decision') == 'digest'],
            'drop_items': [x for x in triaged_data.get('items', []) if x.get('triage', {}).get('decision') == 'drop'],
        }
        if args.output_json:
            with open(args.output_json, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
