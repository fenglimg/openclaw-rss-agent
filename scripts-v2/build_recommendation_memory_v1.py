#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import recommendation_serving_v1 as serving


INPUT = Path('test-output/daily-payload-v2.json')
OUTPUT = Path('test-output/evolution-recommendation-memory-v1.json')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default=str(INPUT))
    parser.add_argument('--output', default=str(OUTPUT))
    parser.add_argument('--surface', default='daily-digest')
    return parser.parse_args()


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return {}


def build_memory(payload: dict, previous: dict, surface: str = 'daily-digest') -> dict:
    return serving.build_memory_snapshot(payload, previous, surface=surface)


def main():
    args = parse_args()
    payload = load_json(Path(args.input))
    previous = load_json(Path(args.output))
    memory = build_memory(payload, previous, surface=args.surface)
    Path(args.output).write_text(json.dumps(memory, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'ok': True, 'output': args.output, 'record_count': memory['record_count']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
