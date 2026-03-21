#!/usr/bin/env python3
import argparse
import json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    args = ap.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = []
    for entry in data.get('candidates', []):
        item = entry.get('item', {})
        results.append({
            'id': item.get('id'),
            'validated': False,
            'crossSourceCount': 0,
            'officialHit': False,
            'confidenceDelta': 0.0,
            'reason': 'stub_only_no_search_layer_call_yet',
        })

    print(json.dumps({
        'ok': True,
        'results': results,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
