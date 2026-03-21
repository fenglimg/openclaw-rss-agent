#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict


def trim(text, n=220):
    text = ' '.join((text or '').split())
    if len(text) <= n:
        return text
    return text[: n - 1] + '…'


def what_it_is(item):
    title = (item.get('title') or '').lower()
    link = (item.get('link') or '').lower()
    if 'releases' in link or 'release' in title:
        return '这更像一条版本 / 发布更新。'
    if 'github.com' in link and ('template' in title or 'scaffold' in title):
        return '这是一个偏工程模板 / 脚手架方向的项目。'
    if 'show hn:' in title:
        return '这是一个偏工具发现类的 Show HN 项目。'
    if item.get('source_role') == 'official_release':
        return '这是一个官方发布源里的更新。'
    if item.get('source_role') == 'official_blog':
        return '这是一个官方博客里的技术更新。'
    return '这是一条和当前关注主题相关的候选内容。'


def why_it_matters(item):
    triage = item.get('triage', {})
    reasons = []
    text = ((item.get('title') or '') + ' ' + (item.get('summary') or '')).lower()
    if any(x in text for x in ['openclaw', 'claude code', 'codex', 'gemini', 'mcp']):
        reasons.append('和当前关注的 AI agent / tooling 主题直接相关')
    if any(x in text for x in ['workflow', 'template', 'scaffold', 'tooling', 'agent']):
        reasons.append('偏 workflow / tooling / 工程模板方向')
    enrichment = triage.get('enrichment') or {}
    if enrichment.get('validated'):
        if enrichment.get('officialHit'):
            reasons.append('已被官方或工程来源进一步确认')
        else:
            reasons.append(f'已做多源验证（{enrichment.get("crossSourceCount", 0)} 个来源）')
    if not reasons:
        reasons.append('当前评分模型认为它值得进入本次摘要')
    return reasons[:3]


def suggested_action(item):
    title = (item.get('title') or '').lower()
    link = (item.get('link') or '').lower()
    if 'github.com' in link:
        return '建议点进去看仓库结构、README 和是否值得纳入参考实现。'
    if 'release' in title or 'releases' in link:
        return '建议重点看 release note / changelog，判断是否值得同步到工作流。'
    if 'show hn:' in title:
        return '建议先判断它是一次性展示，还是值得跟踪的工程工具。'
    return '建议快速浏览原文，确认是否值得继续跟进。'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--title', default='📡 RSS 摘要')
    ap.add_argument('--max-items', type=int, default=5)
    ap.add_argument('--format', choices=['text', 'discord'], default='discord')
    args = ap.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    items = data.get('items', [])
    selected = [x for x in items if x.get('triage', {}).get('final_decision', x.get('triage', {}).get('decision')) in ('send', 'digest')]
    selected = selected[: args.max_items]

    lines = [args.title, '']
    if not selected:
        lines.append('今天暂时没有筛到值得推送的新内容。')
    else:
        send_count = sum(1 for x in selected if x.get('triage', {}).get('final_decision', x.get('triage', {}).get('decision')) == 'send')
        digest_count = sum(1 for x in selected if x.get('triage', {}).get('final_decision', x.get('triage', {}).get('decision')) == 'digest')
        lines.append(f'今天这轮共筛到 {len(selected)} 条值得看的内容（send: {send_count}, digest: {digest_count}）：')
        lines.append('')
        for idx, item in enumerate(selected, start=1):
            triage = item.get('triage', {})
            decision = triage.get('final_decision', triage.get('decision'))
            badge = '🔥' if decision == 'send' else '•'
            enrichment = triage.get('enrichment') or {}
            shown_score = triage.get('enriched_score', triage.get('score'))

            lines.append(f'{idx}. {badge} {item.get("title") or "(untitled)"}')
            lines.append('一句话：')
            lines.append(f'- {what_it_is(item)}')
            lines.append('为什么值得看：')
            for reason in why_it_matters(item):
                lines.append(f'- {trim(reason, 120)}')
            lines.append('建议：')
            lines.append(f'- {suggested_action(item)}')
            lines.append('补充：')
            lines.append(f'- 来源：{item.get("feed_name") or item.get("feed_id")}｜评分：{shown_score}')
            if enrichment.get('validated'):
                label = '已多源验证'
                if enrichment.get('officialHit'):
                    label = '已官方确认'
                lines.append(f'- 验证：{label}（sources {enrichment.get("crossSourceCount", 0)}, Δ+{enrichment.get("confidenceDelta", 0)})')
            lines.append('链接：')
            if item.get('link'):
                lines.append(f'<{item.get("link")}>')
            lines.append('')

    print('\n'.join(lines).strip())


if __name__ == '__main__':
    main()
