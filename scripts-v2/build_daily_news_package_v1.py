#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

INPUT = Path('test-output/daily-payload-v2.json')
OUTPUT = Path('test-output/daily-news-package-v1.json')

JUDGMENT_WEIGHT = {
    'adopt': 100,
    'adopt-candidate': 95,
    'follow': 70,
    'official-anchor': 35,
    'deep-dive': 20,
}

TRACK_LABEL = {
    'applied-ai-evolution': '工具/工作流线',
    'openclaw-evolution': '能力/产品线',
}

BASELINE_ROLE = {
    'anthropics/claude-code': '官方代码代理基线',
    'openai/codex': '官方代码工作流基线',
    'google-gemini/gemini-cli': '官方多模型 CLI 基线',
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default=str(INPUT))
    parser.add_argument('--output', default=str(OUTPUT))
    return parser.parse_args()


def load_payload(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def normalize_space(text: str) -> str:
    return re.sub(r'\s+', ' ', text or '').strip()


def clean_reason(text: str) -> str:
    cleaned = normalize_space(text).replace('`', '')
    replacements = [
        (r'upgraded via calibration rule tooling_surface_upgrade; direct tooling surface with clear practical utility\.?', '工具表面已经成形，而且具备直接上手的实用价值。'),
        (r'upgraded via calibration rule behavior_layer_upgrade; strategically relevant behavior-layer capability\.?', '它影响的是助手行为层，不只是补一个小功能。'),
        (r'remains follow via calibration rule framework_to_study; treat as methodology/framework-to-study\.?', '更适合作为方法论样本继续观察，今天不必立刻上手。'),
        (r'remains follow via calibration rule strong_support_weak_lesson; strong support, but reusable lesson still unclear\.?', '支持信号不弱，但可复用经验还没有完全浮出水面。'),
    ]
    for pattern, replacement in replacements:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.I)
    if cleaned and cleaned[-1] not in '。！？':
        cleaned += '。'
    return cleaned


def judgment_rank(item: dict) -> int:
    return JUDGMENT_WEIGHT.get(item.get('judgment', ''), 50)


def track_label(item: dict) -> str:
    return item.get('track_label') or TRACK_LABEL.get(item.get('track', ''), '观察线')


def brief_tag(item: dict) -> str:
    if item.get('changed_today'):
        return '今日升级'
    judgment = item.get('judgment')
    if judgment == 'adopt':
        return '今日前排'
    if judgment == 'adopt-candidate':
        return '靠前观察'
    if judgment == 'follow':
        return '继续发酵'
    return '观察'


def build_headline(item: dict) -> str:
    name = item['name']
    x_signal = item.get('x_signal') or {}
    if item.get('changed_today') and x_signal.get('repeat_convergence'):
        return f'{name} 升到今天前台，且出现 X 圈内冒头'
    if item.get('changed_today'):
        return f'{name} 升到今天前台'
    if x_signal.get('repeat_convergence'):
        return f'{name} 留在版面前排，且被 X 圈内重复点名'
    if item.get('track') == 'applied-ai-evolution':
        return f'{name} 留在工具/工作流线前排'
    if item.get('track') == 'openclaw-evolution':
        return f'{name} 留在能力/产品线前排'
    return f'{name} 进入今天版面'


def build_link_cards(item: dict):
    cards = []
    for index, link in enumerate(item.get('links', []), start=1):
        label = '主链接' if index == 1 else f'延伸 {index - 1}'
        cards.append({'label': label, 'url': link})
    return cards


def build_freshness_line(item: dict) -> str:
    freshness = item.get('freshness', {})
    label = freshness.get('label', '持续跟进')
    summary = clean_reason(freshness.get('summary', ''))
    changed = '有明确升档' if item.get('changed_today') else '无明确升档'
    return f'{label}｜今日变化：{changed}｜{summary}'.strip('｜')


def build_x_signal_line(item: dict) -> str:
    x_signal = item.get('x_signal') or {}
    if not x_signal.get('matched'):
        return ''
    note = clean_reason(x_signal.get('circle_note', ''))
    boost_strength = x_signal.get('boost_strength')
    if boost_strength:
        note = f"{note} Boost {boost_strength:.2f}。".strip()
    return note


def build_x_contract_line(item: dict) -> str:
    x_signal = item.get('x_signal') or {}
    if not x_signal.get('matched'):
        return ''
    roles = '/'.join(x_signal.get('signal_roles', [])) or 'author-signal'
    return clean_reason(
        f"{x_signal.get('mode_label', 'x-signal')}；角色：{roles}；只作信号层，不作 stable ingest"
    )


def build_author_signal_line(item: dict) -> str:
    x_signal = item.get('x_signal') or {}
    return clean_reason(x_signal.get('author_signal_line', ''))


def build_risk_line(item: dict) -> str:
    x_signal = item.get('x_signal') or {}
    risk_note = x_signal.get('risk_note') or ''
    if risk_note:
        return clean_reason(risk_note)
    return ''


def build_worth_today_line(item: dict) -> str:
    x_signal = item.get('x_signal') or {}
    if x_signal.get('why_now'):
        return clean_reason(x_signal.get('why_now'))
    return ''


def build_lead_item(item: dict, rank: int):
    return {
        'rank': rank,
        'name': item['name'],
        'repo': item.get('repo', item['name']),
        'track': item.get('track'),
        'track_label': track_label(item),
        'headline': build_headline(item),
        'strapline': f"{track_label(item)} · {brief_tag(item)}",
        'today_signal': clean_reason(item.get('today_signal', '今天进入头版。')),
        'why_today': clean_reason(item.get('why_today', '今天值得先看。')),
        'freshness_line': build_freshness_line(item),
        'change_note': clean_reason(item.get('change_note', '今天仍在版面内。')),
        'action': clean_reason(item.get('action', '今天先读主链接。')),
        'x_signal_line': build_x_signal_line(item),
        'x_contract_line': build_x_contract_line(item),
        'author_signal_line': build_author_signal_line(item),
        'risk_note': build_risk_line(item),
        'worth_today_line': build_worth_today_line(item),
        'links': build_link_cards(item),
    }


def build_brief_item(item: dict):
    x_signal = item.get('x_signal') or {}
    return {
        'tag': brief_tag(item),
        'name': item['name'],
        'repo': item.get('repo', item['name']),
        'track': item.get('track'),
        'track_label': track_label(item),
        'today_signal': clean_reason(item.get('today_signal', '')),
        'why_today': clean_reason(item.get('why_today', '')),
        'freshness': item.get('freshness', {}).get('label', '持续发酵'),
        'action': clean_reason(item.get('action', '继续观察。')),
        'primary_link': (item.get('links') or [''])[0],
        'x_signal_line': build_x_signal_line(item),
        'author_signal_line': build_author_signal_line(item),
        'risk_note': build_risk_line(item),
        'worth_today_line': build_worth_today_line(item),
        'x_matched': x_signal.get('matched', False),
    }


def build_official_item(item: dict):
    name = item['name']
    return {
        'name': name,
        'repo': item.get('repo', name),
        'role': BASELINE_ROLE.get(name, '官方基线'),
        'summary': '今天继续挂在基线位，用来校准头版项目与主流官方能力的距离。',
        'primary_link': (item.get('links') or [''])[0],
    }


def build_backlog_item(item: dict):
    return {
        'name': item['name'],
        'reason': clean_reason(item.get('why_today', '今天先放在后排观察。')),
        'return_trigger': clean_reason(item.get('return_trigger', '等出现更强信号再回看。')),
    }


def build_editor_line(priority: list, x_lane: dict) -> str:
    changed = [item for item in priority if item.get('changed_today')]
    x_hits = [item for item in priority if (item.get('x_signal') or {}).get('matched')]
    tracks = {item.get('track') for item in priority}
    if changed and x_hits and 'applied-ai-evolution' in tracks and 'openclaw-evolution' in tracks:
        return '今天版面同时出现两种更像“新闻”的变化：校准升档把项目顶上来，X 信号层再补上圈内为什么突然提它。'
    if changed and x_hits:
        return '今天真正值得看的，不只是被升档的项目，还有 X watchlist 给出的圈内冒头解释。'
    if changed:
        return '今天真正值得看的，是被明确升级的项目，而不是所有仍在名单里的名字。'
    if 'applied-ai-evolution' in tracks and 'openclaw-evolution' in tracks:
        return '今天版面继续维持工具线和能力线对开，让读者同时看到“能马上用什么”和“方向正在往哪走”。'
    return clean_reason(x_lane.get('lane_note', '今天的重点是把真正该先看的对象排到前面，而不是把所有信号平铺出来。'))


def choose_lead_items(priority: list) -> list:
    selected = []
    seen = set()
    for track in ('applied-ai-evolution', 'openclaw-evolution'):
        candidates = [item for item in priority if item.get('track') == track]
        candidates.sort(key=lambda item: (not item.get('changed_today'), -item.get('signal_score', judgment_rank(item))))
        if candidates:
            picked = candidates[0]
            key = (picked.get('name'), picked.get('track'))
            selected.append(picked)
            seen.add(key)
    for item in priority:
        key = (item.get('name'), item.get('track'))
        if key in seen:
            continue
        selected.append(item)
        seen.add(key)
        if len(selected) >= 2:
            break
    return selected[:2]


def interleave_by_track(items: list) -> list:
    buckets = {
        'applied-ai-evolution': [item for item in items if item.get('track') == 'applied-ai-evolution'],
        'openclaw-evolution': [item for item in items if item.get('track') == 'openclaw-evolution'],
    }
    for key in buckets:
        buckets[key].sort(key=lambda item: (not item.get('changed_today'), -item.get('signal_score', judgment_rank(item))))
    ordered = []
    turn = 'applied-ai-evolution'
    while buckets['applied-ai-evolution'] or buckets['openclaw-evolution']:
        if buckets[turn]:
            ordered.append(buckets[turn].pop(0))
        other = 'openclaw-evolution' if turn == 'applied-ai-evolution' else 'applied-ai-evolution'
        if buckets[other]:
            ordered.append(buckets[other].pop(0))
        turn = 'applied-ai-evolution'
    remaining = [item for item in items if item.get('track') not in buckets]
    return ordered + remaining


def build_quick_alerts(lead_items: list, brief_items: list, official_items: list, x_lane: dict) -> list:
    alerts = []
    for lead in lead_items:
        alert = f"{lead['name']}：{lead['today_signal']}"
        if lead.get('x_signal_line'):
            alert += f" X：{lead['x_signal_line']}"
        alerts.append(alert)
    if x_lane.get('matched_item_count'):
        alerts.append(
            f"X 信号层：命中 {x_lane['matched_item_count']} 个版面对象，只作 why-now / weak-risk 旁证，不作 stable ingest。"
        )
    elif official_items:
        alerts.append('官方基线：今天继续挂表，不和头版抢注意力。')
    if brief_items:
        first = brief_items[0]
        alerts.append(f"快讯补位：{first['name']} 仍在雷达里，适合补看。")
    return alerts[:4]


def build_reading_agenda(lead_items: list, brief_items: list) -> list:
    picks = []
    if lead_items:
        picks.append(f"先看 {lead_items[0]['name']}，它代表今天最前面的版面变化。")
    if len(lead_items) > 1:
        picks.append(f"再看 {lead_items[1]['name']}，补足另一条主线。")
    x_briefs = [item for item in brief_items if item.get('x_matched')]
    if x_briefs:
        picks.append(f"最后扫一眼 {x_briefs[0]['name']}，看 X 信号层给出的作者视角或风险备注。")
    elif brief_items:
        picks.append(f"最后扫一眼 {brief_items[0]['name']}，补完雷达层。")
    return picks[:3]


def build_x_desk(payload: dict, visible_items: list) -> dict:
    x_lane = payload.get('x_signal_lane', {})
    matched_items = [item for item in visible_items if (item.get('x_signal') or {}).get('matched')]
    risk_items = [item['name'] for item in visible_items if (item.get('x_signal') or {}).get('risk_note')]
    counts = x_lane.get('artifact_counts', {})
    matched_names = [item['name'] for item in matched_items]
    summary_parts = [
        f"当前模式：{x_lane.get('mode_label', 'x-signal')}",
        'X 只作 signal layer，不作 stable ingest',
        f"author signals {counts.get('author_signals', 0)} 条",
        f"linked objects {counts.get('linked_objects', 0)} 个",
        f"boosts {counts.get('candidate_boosts', 0)} 条",
    ]
    return {
        'mode': x_lane.get('mode'),
        'mode_label': x_lane.get('mode_label'),
        'collector_status': x_lane.get('collector_status'),
        'roles': x_lane.get('roles', []),
        'summary_line': '｜'.join(summary_parts),
        'artifact_counts': counts,
        'matched_item_count': len(matched_items),
        'matched_items': matched_names,
        'risk_items': risk_items,
        'lane_note': clean_reason(x_lane.get('lane_note', '')),
        'summary_highlights': [clean_reason(line) for line in x_lane.get('summary_highlights', [])],
    }


def build_news_package(payload: dict):
    summary = payload.get('summary', {})
    priority = sorted(summary.get('priority', []), key=lambda item: (-item.get('signal_score', judgment_rank(item)), -judgment_rank(item)))
    follow = sorted(summary.get('follow', []), key=lambda item: (-item.get('signal_score', judgment_rank(item)), -judgment_rank(item)))
    official = summary.get('official_anchors', [])
    backlog = summary.get('deprioritized', [])
    x_lane = payload.get('x_signal_lane', {})
    now = datetime.now(timezone.utc)

    lead_source = choose_lead_items(priority)
    lead_keys = {(item.get('name'), item.get('track')) for item in lead_source}
    brief_source = interleave_by_track([
        item for item in priority + follow
        if (item.get('name'), item.get('track')) not in lead_keys
    ])

    lead_items = [build_lead_item(item, index) for index, item in enumerate(lead_source, start=1)]
    brief_items = [build_brief_item(item) for item in brief_source]
    official_items = [build_official_item(item) for item in official]
    backlog_items = [build_backlog_item(item) for item in backlog]

    front_page_counts = {label: 0 for label in TRACK_LABEL.values()}
    for item in lead_items:
        front_page_counts[item['track_label']] = front_page_counts.get(item['track_label'], 0) + 1

    visible_items = priority + follow
    x_desk = build_x_desk(payload, visible_items)
    desk = {
        'front_page_balance': {
            'counts': front_page_counts,
            'balanced': sum(1 for count in front_page_counts.values() if count > 0) >= 2,
        },
        'quick_alerts': build_quick_alerts(lead_items, brief_items, official_items, x_desk),
        'official_baseline_line': '官方项目今天主要承担校准背景的角色，不主动挤占头版。',
        'hold_line': '先放后看区只保留今天不该抢版面的题材。',
        'x_signal_lane': x_desk,
    }

    return {
        'title': 'daily-news-package-v1',
        'source_payload': payload.get('title'),
        'meta': {
            'date': now.strftime('%Y-%m-%d'),
            'weekday': now.strftime('%a'),
            'timezone': 'UTC',
            'edition_label': 'news-style-v3+x-signal',
        },
        'editor_line': build_editor_line(priority, x_lane),
        'deck': f"今日版面：{len(lead_items)} 条头条｜{len(brief_items)} 条快讯雷达｜{len(official_items)} 个官方基线｜{len(backlog_items)} 条先放后看｜X 命中 {x_desk['matched_item_count']} 项",
        'desk': desk,
        'sections': {
            'lead': lead_items,
            'briefs': brief_items,
            'official_watch': official_items,
            'backlog': backlog_items,
            'reading_agenda': build_reading_agenda(lead_items, brief_items),
        },
    }


def main():
    args = parse_args()
    payload = load_payload(Path(args.input))
    news_package = build_news_package(payload)
    Path(args.output).write_text(json.dumps(news_package, ensure_ascii=False, indent=2), encoding='utf-8')
    print(args.output)


if __name__ == '__main__':
    main()
