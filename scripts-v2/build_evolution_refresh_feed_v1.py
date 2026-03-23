#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import recommendation_serving_v1 as serving


PAYLOAD = Path('test-output/daily-payload-v2.json')
MEMORY = Path('test-output/evolution-recommendation-memory-v1.json')
OUTPUT = Path('test-output/evolution-refresh-feed-v1.json')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--payload', default=str(PAYLOAD))
    parser.add_argument('--memory', default=str(MEMORY))
    parser.add_argument('--output', default=str(OUTPUT))
    parser.add_argument('--item-limit', type=int, default=serving.REFRESH_ITEM_LIMIT)
    parser.add_argument('--write-memory', action='store_true')
    return parser.parse_args()


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return {}


def main():
    args = parse_args()
    payload = load_json(Path(args.payload))
    memory = load_json(Path(args.memory))
    if not memory:
        memory = serving.build_memory_snapshot(payload)

    refresh_feed, updated_memory = serving.build_refresh_feed(payload, memory, item_limit=args.item_limit)
    Path(args.output).write_text(serving.dumps_json(refresh_feed), encoding='utf-8')
    if args.write_memory:
        Path(args.memory).write_text(serving.dumps_json(updated_memory), encoding='utf-8')
    print(
        json.dumps(
            {
                'ok': True,
                'output': args.output,
                'item_count': len(refresh_feed.get('items', [])),
                'suppressed_count': len(refresh_feed.get('suppressed_items', [])),
                'memory_written': args.write_memory,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == '__main__':
    main()
