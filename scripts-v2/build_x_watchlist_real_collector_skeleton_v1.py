#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone

WATCHLIST = Path('references/x-watchlist-seeds-v0.md')
OUT_SIGNALS = Path('test-output/x-author-signals-v1.json')
OUT_LINKED = Path('test-output/x-linked-objects-v1.json')
OUT_BOOSTS = Path('test-output/x-candidate-boosts-v1.json')
OUT_SUMMARY = Path('outputs/x-watchlist-summary-v1.md')


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def load_watchlist_seed_text():
    if WATCHLIST.exists():
        return WATCHLIST.read_text(encoding='utf-8')
    return ''


def build_empty_outputs():
    return {
        'signals': {
            'version': 'v1',
            'generated_at': utc_now(),
            'collector': 'x-watchlist-real-collector-skeleton-v1',
            'status': 'skeleton-no-backend',
            'items': []
        },
        'linked': {
            'version': 'v1',
            'generated_at': utc_now(),
            'collector': 'x-watchlist-real-collector-skeleton-v1',
            'status': 'skeleton-no-backend',
            'items': []
        },
        'boosts': {
            'version': 'v1',
            'generated_at': utc_now(),
            'collector': 'x-watchlist-real-collector-skeleton-v1',
            'status': 'skeleton-no-backend',
            'items': []
        }
    }


def build_summary(seed_text: str) -> str:
    return f'''# X Watchlist Summary v1

Real collector skeleton run.

## Status
- Collector: `x-watchlist-real-collector-skeleton-v1`
- Run mode: skeleton only
- Backend: not connected yet
- Generated at: `{utc_now()}`

## What this run proves
- The repository now has a concrete execution path for a real X watchlist collector.
- Downstream outputs are fixed to the agreed contract files.
- The next step is to connect one backend (for example `twitter-cli`, `twscrape`, or browser/session-based collection) without changing downstream file shapes.

## Current outputs
- `test-output/x-author-signals-v1.json`
- `test-output/x-linked-objects-v1.json`
- `test-output/x-candidate-boosts-v1.json`
- `outputs/x-watchlist-summary-v1.md`

## Watchlist seed source
- Loaded from: `references/x-watchlist-seeds-v0.md`
- Seed file present: `{str(bool(seed_text)).lower()}`

## Next implementation point
Wire one minimal acquisition backend that:
1. reads a small manually reviewed watchlist
2. fetches recent posts
3. extracts outbound links
4. canonicalizes links
5. writes into the existing output contract
'''


def main():
    seed_text = load_watchlist_seed_text()
    outputs = build_empty_outputs()
    OUT_SIGNALS.write_text(json.dumps(outputs['signals'], ensure_ascii=False, indent=2), encoding='utf-8')
    OUT_LINKED.write_text(json.dumps(outputs['linked'], ensure_ascii=False, indent=2), encoding='utf-8')
    OUT_BOOSTS.write_text(json.dumps(outputs['boosts'], ensure_ascii=False, indent=2), encoding='utf-8')
    OUT_SUMMARY.write_text(build_summary(seed_text), encoding='utf-8')
    print(json.dumps({
        'ok': True,
        'signals': str(OUT_SIGNALS),
        'linked': str(OUT_LINKED),
        'boosts': str(OUT_BOOSTS),
        'summary': str(OUT_SUMMARY),
        'status': 'skeleton-no-backend'
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
