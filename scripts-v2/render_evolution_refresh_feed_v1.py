#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


INPUT = Path('test-output/evolution-refresh-feed-v1.json')
OUTPUT = Path('outputs/evolution-refresh-feed-v1.md')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default=str(INPUT))
    parser.add_argument('--output', default=str(OUTPUT))
    return parser.parse_args()


def render_report(feed: dict) -> str:
    summary = feed.get('summary') or {}
    lines = [
        f"# 🔄 Evolution Refresh Feed｜{feed.get('generated_at', '')}",
        '',
        f"> 当前 surface：{feed.get('surface', 'refresh')}｜选出 {summary.get('selected_count', 0)} 条｜抑制 {summary.get('suppressed_count', 0)} 条｜候选 {summary.get('candidate_count', 0)} 条",
        f"> anti-repeat：{' / '.join((feed.get('policy') or {}).get('anti_repeat', []))}",
        f"> sort key：{(feed.get('policy') or {}).get('sort_key', 'effective_serve_score')}",
        '',
    ]

    if feed.get('items'):
        lines.extend(['## 本轮上屏', ''])
        for item in feed['items']:
            lines.append(f"### {item['rank']}｜{item['name']}")
            lines.append(
                f"- 对象：{item.get('target_audience_label', item.get('target_audience', ''))}｜动作：{item.get('recommended_action_label', item.get('recommended_action', ''))}｜队列：{item.get('queue', '')}"
            )
            lines.append(
                f"- 分数：base {item.get('base_serve_score', 0)} → effective {item.get('effective_serve_score', 0)}｜repeat penalty {item.get('repeat_penalty', 0)}"
            )
            lines.append(
                f"- anti-repeat：cooldown={item.get('cooldown_active', False)}｜same_event={item.get('same_event', False)}｜same_angle={item.get('same_angle', False)}｜fresh_override={item.get('fresh_override', False)}"
            )
            lines.append(f"- Why-now：{item.get('why_now', '')}")
            lines.append(f"- 动作理由：{item.get('recommended_action_reason', '')}")
            evidence = item.get('evidence_summary') or {}
            lines.append(
                f"- 证据层：stable {evidence.get('stable_count', 0)}｜signal {evidence.get('signal_count', 0)}｜verify {evidence.get('verification_count', 0)}"
            )
            if item.get('links'):
                lines.append(f"- 主链接：<{item['links'][0]}>")
            if item.get('suppressed_until'):
                lines.append(f"- 下次冷却：{item['suppressed_until']}")
            lines.append('')

    if feed.get('suppressed_items'):
        lines.extend(['## 本轮被 anti-repeat 压下', ''])
        for item in feed['suppressed_items']:
            lines.append(
                f"- **{item['name']}**：{item.get('suppression_reason', 'suppressed')}｜base {item.get('base_serve_score', 0)} → effective {item.get('effective_serve_score', 0)}｜repeat penalty {item.get('repeat_penalty', 0)}｜same_event={item.get('same_event', False)}｜same_angle={item.get('same_angle', False)}｜until={item.get('suppressed_until') or 'n/a'}"
            )
        lines.append('')

    lines.append('<!-- refresh-feed-output: scripts-v2/render_evolution_refresh_feed_v1.py -->')
    return '\n'.join(lines).strip() + '\n'


def main():
    args = parse_args()
    feed = json.loads(Path(args.input).read_text(encoding='utf-8'))
    Path(args.output).write_text(render_report(feed), encoding='utf-8')
    print(args.output)


if __name__ == '__main__':
    main()
