#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

INPUT = Path('test-output/daily-news-package-v1.json')
OUTPUT = Path('outputs/daily-report-zh-news-v3.md')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default=str(INPUT))
    parser.add_argument('--output', default=str(OUTPUT))
    return parser.parse_args()


def render_link_cards(cards: list) -> list:
    return [f"- {card['label']}：<{card['url']}>" for card in cards]


def render_report(package: dict) -> str:
    meta = package['meta']
    sections = package['sections']
    desk = package.get('desk', {})
    balance = (desk.get('front_page_balance') or {}).get('counts', {})
    balance_line = '｜'.join(f'{name} {count}' for name, count in balance.items() if count)

    lines = [
        f"# 🗞️ AI 资讯日报｜{meta['date']} {meta['weekday']} ({meta['timezone']})",
        '',
        f"> {package['deck']}",
        f"> 头版配比：{balance_line or '待生成'}",
        '',
        '## 今晨导语',
        package['editor_line'],
        '',
    ]

    if desk.get('quick_alerts'):
        lines.extend(['## 一眼看完今天', ''])
        for alert in desk['quick_alerts']:
            lines.append(f'- {alert}')
        lines.append('')

    lines.extend(['## 今日头条', ''])
    for lead in sections['lead']:
        lines.append(f"### 头条 {lead['rank']}｜{lead['headline']}")
        lines.append(f"- 版面位置：{lead['strapline']}")
        lines.append(f"- 今天发生了什么：{lead['today_signal']}")
        lines.append(f"- 为什么是今天：{lead['why_today']}")
        lines.append(f"- 新鲜度：{lead['freshness_line']}")
        lines.append(f"- 先怎么看：{lead['action']}")
        lines.append('- 相关链接：')
        lines.extend(render_link_cards(lead['links']))
        lines.append('')

    if sections['briefs']:
        lines.extend(['## 快讯雷达', ''])
        for item in sections['briefs']:
            tail = f"｜<{item['primary_link']}>" if item['primary_link'] else ''
            lines.append(
                f"- [{item['track_label']}·{item['freshness']}] **{item['name']}**：{item['today_signal']} 为什么看：{item['why_today']} 先看法：{item['action']}{tail}"
            )
        lines.append('')

    if sections['official_watch']:
        lines.extend(['## 官方基线', ''])
        for item in sections['official_watch']:
            tail = f" <{item['primary_link']}>" if item['primary_link'] else ''
            lines.append(f"- **{item['name']}**（{item['role']}）：{item['summary']}{tail}")
        if desk.get('official_baseline_line'):
            lines.append(f"- 值班台说明：{desk['official_baseline_line']}")
        lines.append('')

    if sections['backlog']:
        lines.extend(['## 先放后看', ''])
        for item in sections['backlog']:
            lines.append(f"- **{item['name']}**：{item['reason']} 回看触发：{item['return_trigger']}")
        if desk.get('hold_line'):
            lines.append(f"- 值班台说明：{desk['hold_line']}")
        lines.append('')

    if sections['reading_agenda']:
        lines.extend(['## 3 分钟看完顺序', ''])
        for item in sections['reading_agenda']:
            lines.append(f'- {item}')
        lines.append('')

    lines.append('<!-- news-style-output: scripts-v2/render_daily_report_news_zh_v3.py -->')
    return '\n'.join(lines).strip() + '\n'


def main():
    args = parse_args()
    package = json.loads(Path(args.input).read_text(encoding='utf-8'))
    report = render_report(package)
    Path(args.output).write_text(report, encoding='utf-8')
    print(args.output)


if __name__ == '__main__':
    main()
