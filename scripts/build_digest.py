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
    ap.add_argument('--format', choices=['text', 'discord'], default='discord')
    args = ap.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    items = data.get('items', [])
    selected = [x for x in items if x.get('triage', {}).get('final_decision', x.get('triage', {}).get('decision')) in ('send', 'digest')]
    selected = selected[: args.max_items]

    by_feed = defaultdict(list)
    for item in selected:
        by_feed[item.get('feed_name') or item.get('feed_id')].append(item)

    lines = [args.title, '']
    if not selected:
        lines.append('今天没有筛到新的高价值 RSS 条目。')
    else:
        send_count = sum(1 for x in selected if x.get('triage', {}).get('final_decision', x.get('triage', {}).get('decision')) == 'send')
        digest_count = sum(1 for x in selected if x.get('triage', {}).get('final_decision', x.get('triage', {}).get('decision')) == 'digest')
        lines.append(f'本次共筛到 {len(selected)} 条值得关注的内容（send: {send_count}, digest: {digest_count}）：')
        lines.append('')
        idx = 1
        for feed_name, group in by_feed.items():
            lines.append(f'**{feed_name}**')
            for item in group:
                triage = item.get('triage', {})
                decision = triage.get('final_decision', triage.get('decision'))
                badge = '🔥' if decision == 'send' else '•'
                lines.append(f'{idx}. {badge} {item.get("title") or "(untitled)"}')
                if item.get('summary'):
                    lines.append(f'- {trim(item.get("summary"), 180)}')
                shown_score = triage.get('enriched_score', triage.get('score'))
                if triage.get('reason'):
                    lines.append(f'- 判断：{trim(triage.get("reason"), 120)}（score {shown_score})')
                enrichment = triage.get('enrichment') or {}
                if enrichment.get('validated'):
                    label = '已多源验证'
                    if enrichment.get('officialHit'):
                        label = '已官方确认'
                    lines.append(f'- 验证：{label}（sources {enrichment.get("crossSourceCount", 0)}, Δ+{enrichment.get("confidenceDelta", 0)})')
                elif enrichment:
                    lines.append(f'- 验证：未确认（{trim(enrichment.get("reason", "no result"), 80)}）')
                if item.get('link'):
                    lines.append(f'<{item.get("link")}>')
                lines.append('')
                idx += 1

    # text and discord are currently rendered the same, but keep the flag for future formatting divergence
    print('\n'.join(lines).strip())


if __name__ == '__main__':
    main()
