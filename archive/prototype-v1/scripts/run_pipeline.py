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
    ap.add_argument('--digest-title', default='📡 AI Coding / Agent 工具日报')
    ap.add_argument('--max-items', type=int, default=10)
    ap.add_argument('--output-format', choices=['json', 'text', 'discord'], default='json')
    ap.add_argument('--triage-mode', choices=['general-tech', 'agentic'], default='general-tech')
    ap.add_argument('--ignore-feed-mode', action='store_true')
    ap.add_argument('--write-state', action='store_true')
    ap.add_argument('--output-json')
    args = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix='rss-agent-') as tmp:
        fetched = os.path.join(tmp, 'fetched.json')
        deduped = os.path.join(tmp, 'deduped.json')
        triaged = os.path.join(tmp, 'triaged.json')
        enrichment_candidates = os.path.join(tmp, 'enrichment_candidates.json')
        enrichment_results = os.path.join(tmp, 'enrichment_results.json')
        merged = os.path.join(tmp, 'merged.json')
        github_radar = os.path.join(tmp, 'github_radar.json')

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

        triage_cmd = [
            sys.executable, str(BASE / 'triage_items.py'),
            '--input', deduped,
            '--mode', args.triage_mode,
        ]
        if args.ignore_feed_mode:
            triage_cmd.append('--ignore-feed-mode')
        triaged_data = run_json(triage_cmd)
        with open(triaged, 'w', encoding='utf-8') as f:
            json.dump(triaged_data, f, ensure_ascii=False, indent=2)

        enrichment_candidate_data = run_json([
            sys.executable, str(BASE / 'select_enrichment_candidates.py'),
            '--input', triaged,
        ])
        with open(enrichment_candidates, 'w', encoding='utf-8') as f:
            json.dump(enrichment_candidate_data, f, ensure_ascii=False, indent=2)

        enrichment_result_data = run_json([
            sys.executable, str(BASE / 'enrichment_stub.py'),
            '--input', enrichment_candidates,
        ])
        with open(enrichment_results, 'w', encoding='utf-8') as f:
            json.dump(enrichment_result_data, f, ensure_ascii=False, indent=2)

        merged_data = run_json([
            sys.executable, str(BASE / 'merge_enrichment.py'),
            '--triaged', triaged,
            '--enrichment', enrichment_results,
        ])
        with open(merged, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)

        github_radar_data = run_json([
            sys.executable, str(BASE / 'github_radar.py'),
            '--input', merged,
        ])
        with open(github_radar, 'w', encoding='utf-8') as f:
            json.dump(github_radar_data, f, ensure_ascii=False, indent=2)

        merged_data['github_radar'] = github_radar_data.get('repos', [])
        with open(merged, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)

        digest = run_text([
            sys.executable, str(BASE / 'build_digest.py'),
            '--input', merged,
            '--title', args.digest_title,
            '--max-items', str(args.max_items),
            '--format', 'discord' if args.output_format == 'discord' else 'text',
        ])

        result = {
            'ok': True,
            'triage_mode': args.triage_mode,
            'ignore_feed_mode': args.ignore_feed_mode,
            'fetched_count': data.get('count', 0),
            'new_count': deduped_data.get('counts', {}).get('new', 0),
            'counts': deduped_data.get('counts', {}),
            'triage_counts': triaged_data.get('counts', {}),
            'final_counts': merged_data.get('counts', {}),
            'feed_health': data.get('feed_health', []),
            'enrichment_candidates': enrichment_candidate_data.get('candidates', []),
            'enrichment_results': enrichment_result_data.get('results', []),
            'github_radar': github_radar_data.get('repos', []),
            'digest': digest,
            'items': merged_data.get('items', []),
            'send_items': [x for x in merged_data.get('items', []) if x.get('triage', {}).get('final_decision', x.get('triage', {}).get('decision')) == 'send'],
            'digest_items': [x for x in merged_data.get('items', []) if x.get('triage', {}).get('final_decision', x.get('triage', {}).get('decision')) == 'digest'],
            'drop_items': [x for x in merged_data.get('items', []) if x.get('triage', {}).get('final_decision', x.get('triage', {}).get('decision')) == 'drop'],
        }
        if args.output_json:
            with open(args.output_json, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        if args.output_format == 'json':
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(digest.strip())


if __name__ == '__main__':
    main()
