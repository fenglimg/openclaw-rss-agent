#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict


def trim(text, n=220):
    text = ' '.join((text or '').split())
    if len(text) <= n:
        return text
    return text[: n - 1] + '…'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--title', default='📡 RSS Digest')
    ap.add_argument('--max-items', type=int, default=10)
    args = ap.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    items = data.get('new_items', [])[: args.max_items]

    by_feed = defaultdict(list)
    for item in items:
        by_feed[item.get('feed_name') or item.get('feed_id')].append(item)

    lines = [args.title, '']
    if not items:
        lines.append('今天没有筛到新的高价值 RSS 条目。')
    else:
        lines.append(f'本次共筛到 {len(items)} 条新内容：')
        lines.append('')
        idx = 1
        for feed_name, group in by_feed.items():
            lines.append(f'**{feed_name}**')
            for item in group:
                lines.append(f'{idx}. {item.get("title") or "(untitled)"}')
                if item.get('summary'):
                    lines.append(f'- {trim(item.get("summary"), 180)}')
                if item.get('link'):
                    lines.append(f'<{item.get("link")}>')
                lines.append('')
                idx += 1

    print('\n'.join(lines).strip())


if __name__ == '__main__':
    main()
