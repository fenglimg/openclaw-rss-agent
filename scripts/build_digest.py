#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict


def trim(text, n=220):
    text = ' '.join((text or '').split())
    if len(text) <= n:
        return text
    return text[: n - 1] + '…'


def final_decision(item):
    triage = item.get('triage', {})
    return triage.get('final_decision', triage.get('decision'))


def shown_score(item):
    triage = item.get('triage', {})
    return triage.get('enriched_score', triage.get('score'))


def bucket_for(item):
    text = ((item.get('title') or '') + ' ' + (item.get('summary') or '')).lower()
    link = (item.get('link') or '').lower()
    feed_name = (item.get('feed_name') or '').lower()
    source_role = item.get('source_role') or ''

    if source_role in ('official_release', 'official_blog') or 'release' in text or 'changelog' in text:
        return 'important_updates'
    if 'github.com/' in link or 'github blog' in feed_name or any(x in text for x in ['repo', 'template', 'scaffold', 'mcp server', 'skill repo']):
        return 'github_radar'
    if any(x in text for x in ['workflow', 'integration', 'setup', 'how-to', 'recipe', 'template', 'scaffold', '修复', '配置', '接入', '用法', '工作流']):
        return 'applied_workflows'
    if source_role == 'community_forum' or any(x in feed_name for x in ['linux.do', 'v2ex', 'hacker news', 'simon willison']):
        return 'community_practice'
    return 'community_practice'


def one_liner(item):
    title = (item.get('title') or '').lower()
    link = (item.get('link') or '').lower()
    if 'release' in title or 'releases' in link:
        return '这是一条官方更新，优先看 release note / changelog。'
    if any(x in title for x in ['修复', 'fix', 'workaround', '临时修复']):
        return '这是一条偏实操的修复/绕坑内容。'
    if any(x in title for x in ['workflow', '集成', 'integration', 'template', 'scaffold', 'recipe']):
        return '这是一条偏应用层 workflow / 集成玩法内容。'
    if 'github.com/' in link:
        return '这是一个值得看实现方式的 GitHub 项目/仓库。'
    return '这是一条和当前核心生态相关的候选内容。'


def why_it_matters(item):
    triage = item.get('triage', {})
    enrichment = triage.get('enrichment') or {}
    text = ((item.get('title') or '') + ' ' + (item.get('summary') or '')).lower()
    reasons = []

    if any(x in text for x in ['openclaw', 'claude code', 'codex', 'gemini', 'mcp', 'skill']):
        reasons.append('直接命中当前核心生态')
    if any(x in text for x in ['workflow', 'integration', 'setup', 'recipe', 'template', 'scaffold', '修复', '配置', '接入', '用法']):
        reasons.append('偏应用层，可直接迁移到日常工作流')
    if enrichment.get('validated'):
        if enrichment.get('officialHit'):
            reasons.append('已被官方或工程来源进一步确认')
        else:
            reasons.append(f'已做多源验证（{enrichment.get("crossSourceCount", 0)} 个来源）')
    if item.get('feed_id') == 'linux_do_latest':
        reasons.append('来自中文社区实战讨论，通常更贴近真实用法')
    if not reasons:
        reasons.append('这条内容在本轮评分中具备较高保留价值')
    return reasons[:3]


def suggested_action(item):
    title = (item.get('title') or '').lower()
    link = (item.get('link') or '').lower()
    if 'github.com/' in link:
        return '建议点进去看 README、最近提交和是否值得纳入参考项目池。'
    if 'release' in title or 'releases' in link:
        return '建议重点看 changelog，判断是否会影响现有 workflow / skill / MCP 用法。'
    if any(x in title for x in ['修复', 'fix', 'workaround', '临时修复']):
        return '建议收藏这条，后续遇到同类问题时可以直接复用。'
    return '建议快速浏览原文，确认是否值得试一下或继续跟踪。'


def render_item(idx, item):
    triage = item.get('triage', {})
    decision = final_decision(item)
    badge = '🔥' if decision == 'send' else '•'
    enrichment = triage.get('enrichment') or {}
    lines = []
    lines.append(f'{idx}. {badge} {item.get("title") or "(untitled)"}')
    lines.append(f'- 一句话：{one_liner(item)}')
    lines.append('- 为什么值得看：')
    for reason in why_it_matters(item):
        lines.append(f'  - {trim(reason, 120)}')
    lines.append(f'- 建议：{suggested_action(item)}')
    lines.append(f'- 补充：来源 {item.get("feed_name") or item.get("feed_id")}｜评分 {shown_score(item)}')
    if enrichment.get('validated'):
        label = '已多源验证'
        if enrichment.get('officialHit'):
            label = '已官方确认'
        lines.append(f'- 验证：{label}（sources {enrichment.get("crossSourceCount", 0)}, Δ+{enrichment.get("confidenceDelta", 0)})')
    if item.get('link'):
        lines.append(f'- 链接：<{item.get("link")}>')
    return lines


def split_chunks(lines, max_chars=1700):
    chunks = []
    current = []
    current_len = 0
    for line in lines:
        add_len = len(line) + 1
        if current and current_len + add_len > max_chars:
            chunks.append('\n'.join(current).strip())
            current = [line]
            current_len = add_len
        else:
            current.append(line)
            current_len += add_len
    if current:
        chunks.append('\n'.join(current).strip())
    return chunks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--title', default='📡 RSS 日报')
    ap.add_argument('--max-items', type=int, default=8)
    ap.add_argument('--format', choices=['text', 'discord'], default='discord')
    args = ap.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    items = [x for x in data.get('items', []) if final_decision(x) in ('send', 'digest')]
    items = sorted(items, key=lambda x: shown_score(x), reverse=True)[: args.max_items]

    buckets = defaultdict(list)
    for item in items:
        buckets[bucket_for(item)].append(item)

    lines = [args.title, '']
    if not items:
        lines.append('今天暂时没有筛到值得推送的新内容。')
    else:
        lines.append('今日结构：重点更新 / 应用层新玩法 / GitHub 项目雷达 / 社区实战')
        lines.append('')

        top_picks = items[:3]
        lines.append('## 今日重点')
        for idx, item in enumerate(top_picks, start=1):
            lines.extend(render_item(idx, item))
            lines.append('')

        sections = [
            ('important_updates', '## 重要更新'),
            ('applied_workflows', '## 应用层新玩法'),
            ('github_radar', '## GitHub 项目雷达'),
            ('community_practice', '## 社区实战 / 修复 / 技巧'),
        ]
        seen_titles = set(x.get('title') for x in top_picks)
        running_idx = len(top_picks) + 1
        for key, header in sections:
            section_items = [x for x in buckets.get(key, []) if x.get('title') not in seen_titles]
            if not section_items and key == 'github_radar':
                lines.append(header)
                lines.append('- 暂无单独 GitHub 项目雷达条目；下一步会接入 star 基数 / 最近 star 增长。')
                lines.append('')
                continue
            if not section_items:
                continue
            lines.append(header)
            for item in section_items[:3]:
                lines.extend(render_item(running_idx, item))
                lines.append('')
                running_idx += 1

    chunks = split_chunks(lines, max_chars=1700 if args.format == 'discord' else 100000)
    if len(chunks) == 1:
        print(chunks[0])
    else:
        print('\n\n---CHUNK---\n\n'.join(chunks))


if __name__ == '__main__':
    main()
