#!/usr/bin/env python3
import json
import re
from datetime import datetime, timezone
from pathlib import Path

APPLIED = Path('outputs/applied-ai-evolution-brief-v5.md')
OPENCLAW = Path('outputs/openclaw-evolution-brief-v15.md')
OUT = Path('test-output/daily-payload-v2.json')

X_AUTHOR_SIGNALS = Path('test-output/x-author-signals-v1.json')
X_LINKED_OBJECTS = Path('test-output/x-linked-objects-v1.json')
X_CANDIDATE_BOOSTS = Path('test-output/x-candidate-boosts-v1.json')
X_WATCHLIST_SUMMARY = Path('outputs/x-watchlist-summary-v1.md')

X_REFERENCE_DOCS = [
    'references/x-signal-research.md',
    'references/x-source-spec-v0.md',
    'references/x-watchlist-v0.md',
    'references/x-watchlist-seeds-v0.md',
    'references/x-collector-contract-v1.md',
    'references/x-integration-flow-v1.md',
]

TRACK_LABEL = {
    'applied-ai-evolution': '工具/工作流线',
    'openclaw-evolution': '能力/产品线',
}

TRACK_SORT_WEIGHT = {
    'applied-ai-evolution': 0,
    'openclaw-evolution': 1,
}

BASE_SCORE = {
    'adopt': 90,
    'adopt-candidate': 85,
    'follow': 60,
    'official-anchor': 35,
    'deep-dive': 20,
}


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8') if path.exists() else ''


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return {}


def bullets_under(text: str, heading: str):
    match = re.search(rf'^## {re.escape(heading)}\n\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    if not match:
        return []
    block = match.group(1)
    return [line.strip() for line in block.splitlines() if line.strip().startswith('- **')]


def extract_name_repo(line: str):
    match = re.match(r'- \*\*(.+?)\*\*(.*)$', line)
    if not match:
        return line, line, ''
    name = match.group(1).strip()
    rest = match.group(2).strip()
    reason = rest.lstrip('—').strip() if rest.startswith('—') else ''
    return name, name, reason


def repo_links(name: str):
    key = name.lower()
    mapping = {
        'obra/superpowers': ['https://github.com/obra/superpowers'],
        'mindfold-ai/trellis': ['https://github.com/mindfold-ai/Trellis'],
        'davila7/claude-code-templates': ['https://github.com/davila7/claude-code-templates'],
        'jarrodwatts/claude-hud': ['https://github.com/jarrodwatts/claude-hud', 'https://github.com/jarrodwatts/claude-delegator'],
        'gsd-build/get-shit-done': ['https://github.com/gsd-build/get-shit-done'],
        'anthropics/claude-code': ['https://github.com/anthropics/claude-code'],
        'openai/codex': ['https://github.com/openai/codex'],
        'google-gemini/gemini-cli': ['https://github.com/google-gemini/gemini-cli'],
        'agent browser': ['https://github.com/openclaw/skills'],
        'summarize': ['https://github.com/openclaw/skills'],
        'github': ['https://github.com/openclaw/skills'],
        'self-improving-agent': ['https://github.com/openclaw/skills'],
        'proactive agent': ['https://github.com/openclaw/skills', 'https://github.com/VoltAgent/awesome-openclaw-skills'],
        'gog': ['https://github.com/openclaw/skills'],
        'polymarket': ['https://github.com/openclaw/skills'],
        'weather': ['https://github.com/openclaw/skills'],
    }
    return mapping.get(key, [])


def track_label(track: str) -> str:
    return TRACK_LABEL.get(track, '观察线')


def normalize_sentence(text: str) -> str:
    cleaned = re.sub(r'\s+', ' ', text or '').strip().replace('`', '')
    cleaned = re.sub(r'[.。！？]+$', '', cleaned)
    if cleaned and cleaned[-1] not in '。！？':
        cleaned += '。'
    return cleaned


def merge_sentences(*parts: str) -> str:
    normalized = []
    seen = set()
    for part in parts:
        sentence = normalize_sentence(part)
        if sentence and sentence not in seen:
            normalized.append(sentence)
            seen.add(sentence)
    return ' '.join(normalized)


def normalize_url(url: str) -> str:
    cleaned = (url or '').strip()
    if not cleaned:
        return ''
    cleaned = re.sub(r'[?#].*$', '', cleaned)
    if cleaned.endswith('/'):
        cleaned = cleaned[:-1]
    if cleaned.startswith('https://github.com/'):
        owner_repo = cleaned[len('https://github.com/'):]
        parts = [part for part in owner_repo.split('/') if part]
        if len(parts) >= 2:
            cleaned = f'https://github.com/{parts[0].lower()}/{parts[1].lower()}'
    return cleaned


def compact_excerpt(text: str) -> str:
    cleaned = re.sub(r'\s+', ' ', text or '').strip().replace('"', '”')
    if len(cleaned) > 110:
        cleaned = cleaned[:107].rstrip() + '...'
    return cleaned


def item_aliases(name: str, repo: str, links: list) -> set:
    aliases = set()
    for raw in (name, repo):
        lowered = (raw or '').lower().strip()
        if not lowered:
            continue
        aliases.add(lowered)
        aliases.add(lowered.replace('-', ' '))
        aliases.add(lowered.replace('/', ' '))
        aliases.add(lowered.replace('_', ' '))
        aliases.add(lowered.replace(' ', '-'))
        if '/' in lowered:
            aliases.add(lowered.split('/')[-1])
    for link in links or []:
        normalized = normalize_url(link)
        if normalized.startswith('https://github.com/'):
            slug = normalized[len('https://github.com/'):]
            aliases.add(slug)
            tail = slug.split('/')[-1]
            aliases.add(tail)
            aliases.add(tail.replace('-', ' '))
            aliases.add(slug.replace('-', ' '))
    return {alias for alias in aliases if len(alias) >= 3}


def excerpt_mentions_item(text: str, aliases: set) -> bool:
    lowered = (text or '').lower()
    return any(alias in lowered for alias in aliases)


def score_reason(reason: str, judgment: str) -> int:
    lowered = reason.lower()
    score = BASE_SCORE[judgment]
    if 'upgraded via calibration rule' in lowered:
        score += 30
    if 'tooling_surface_upgrade' in lowered:
        score += 10
    if 'behavior_layer_upgrade' in lowered:
        score += 12
    if 'remains adopt' in lowered:
        score -= 4
    if 'remains `follow`' in lowered or 'remains follow' in lowered:
        score -= 8
    if 'known risk' in lowered or 'caution' in lowered:
        score -= 8
    if judgment in ('adopt', 'adopt-candidate') and not reason:
        score += 3
    return score


def build_freshness(judgment: str, reason: str) -> dict:
    lowered = reason.lower()
    if 'upgraded via calibration rule' in lowered:
        return {
            'label': '今日升级',
            'score': 95,
            'status': 'changed-today',
            'summary': '源 brief 明确给出升级动作，属于今天最该前置的信号。',
        }
    if judgment in ('adopt', 'adopt-candidate'):
        return {
            'label': '今日前排',
            'score': 82,
            'status': 'front-page-today',
            'summary': '没有明确升档语句，但今天继续占据前排版面。',
        }
    if judgment == 'follow':
        return {
            'label': '持续发酵',
            'score': 60,
            'status': 'watch-today',
            'summary': '仍在雷达内发酵，但今天还不到抢头版的时候。',
        }
    if judgment == 'official-anchor':
        return {
            'label': '基线续看',
            'score': 38,
            'status': 'baseline-carry',
            'summary': '今天继续提供官方基线，不以爆点身份出现。',
        }
    return {
        'label': '先放后看',
        'score': 22,
        'status': 'hold-for-later',
        'summary': '保留题材，但不进入今天的主版面。',
    }


def build_today_signal(track: str, judgment: str, reason: str) -> str:
    lowered = reason.lower()
    if 'tooling_surface_upgrade' in lowered:
        return '工具面出现明确升级，今天从候选项抬升到前台。'
    if 'behavior_layer_upgrade' in lowered:
        return '能力层出现明确升档，今天不只是看功能，而是看助手行为变化。'
    if 'upgraded via calibration rule' in lowered:
        return f'{track_label(track)}出现明确升档，今天需要前置阅读。'
    if judgment in ('adopt', 'adopt-candidate'):
        return f'{track_label(track)}继续占据今日前排，属于今天先看的对象。'
    if judgment == 'follow':
        return f'{track_label(track)}继续挂在快讯雷达，信号还在累积。'
    if judgment == 'official-anchor':
        return '官方项目继续作为今日基线，不主动抢占头版。'
    return '题材仍在，但今天先放后看。'


def build_why_today(track: str, judgment: str, reason: str) -> str:
    lowered = reason.lower()
    if 'tooling_surface_upgrade' in lowered:
        return '因为它已经从“可关注”走到“可直接上手”的工具面升级，今天更像一条实用新闻。'
    if 'behavior_layer_upgrade' in lowered:
        return '因为它代表助手行为层的变化，这类变化通常比单个技能点更值得今天优先看。'
    if 'framework_to_study' in lowered:
        return '因为方法论价值在，但今天更适合记进雷达，不必挤进主版。'
    if 'strong_support_weak_lesson' in lowered:
        return '因为支持信号还在，但可复用 lesson 还没强到足以拿下今天头版。'
    if judgment in ('adopt', 'adopt-candidate'):
        return '因为它今天仍在高优先级队列里，值得先占掉读者的第一轮注意力。'
    if judgment == 'official-anchor':
        return '因为需要用官方项目校准当天版面，不是因为它们今天一定出现了最大增量。'
    return '因为它目前更像储备题材，等出现新触发点再回到前台。'


def build_action(track: str, judgment: str, reason: str) -> str:
    lowered = reason.lower()
    if 'tooling_surface_upgrade' in lowered:
        return '今天先把它放进优先体验名单。'
    if 'behavior_layer_upgrade' in lowered:
        return '今天先按能力层方向重点看一遍。'
    if judgment in ('adopt', 'adopt-candidate'):
        return '今天先读主链接，再决定要不要进入体验名单。'
    if judgment == 'follow':
        return '先放在快讯雷达里持续跟进。'
    if judgment == 'official-anchor':
        return '继续挂表，用来和新项目对照。'
    return '暂不分配主版面注意力。'


def build_change_note(reason: str) -> str:
    lowered = reason.lower()
    if 'upgraded via calibration rule' in lowered:
        return '今天有明确升档。'
    if 'remains' in lowered:
        return '今天没有新升档，属于位置延续。'
    return '今天没有显式变化说明，但仍被编入当前版面。'


def build_item(line: str, track: str, section: str, judgment: str) -> dict:
    name, repo, reason = extract_name_repo(line)
    freshness = build_freshness(judgment, reason)
    return {
        'name': name,
        'repo': repo,
        'track': track,
        'track_label': track_label(track),
        'source_section': section,
        'judgment': judgment,
        'raw_reason': normalize_sentence(reason),
        'why': [normalize_sentence(reason)] if reason else [],
        'today_signal': build_today_signal(track, judgment, reason),
        'why_today': build_why_today(track, judgment, reason),
        'freshness': freshness,
        'changed_today': freshness['status'] == 'changed-today',
        'change_note': build_change_note(reason),
        'action': build_action(track, judgment, reason),
        'links': repo_links(name),
        'signal_score': score_reason(reason, judgment),
    }


def build_official_item(line: str) -> dict:
    name, repo, _ = extract_name_repo(line)
    freshness = build_freshness('official-anchor', '')
    return {
        'name': name,
        'repo': repo,
        'track': 'official-baseline',
        'track_label': '官方基线',
        'source_section': 'Official anchors',
        'judgment': 'official-anchor',
        'raw_reason': '',
        'why': [],
        'today_signal': '官方项目继续作为今日基线，不主动抢占头版。',
        'why_today': '因为今天需要一个稳定参照系，来判断头版项目到底离主流工具面有多远。',
        'freshness': freshness,
        'changed_today': False,
        'change_note': '今天主要承担校准作用。',
        'action': '继续挂表，用来和新项目对照。',
        'links': repo_links(name),
        'signal_score': BASE_SCORE['official-anchor'],
    }


def build_hold_item(line: str, track: str) -> dict:
    name, repo, reason = extract_name_repo(line)
    freshness = build_freshness('deep-dive', reason)
    return {
        'name': name,
        'repo': repo,
        'track': track,
        'track_label': track_label(track),
        'source_section': 'Deep-dive',
        'judgment': 'deep-dive',
        'raw_reason': normalize_sentence(reason),
        'why': [normalize_sentence(reason)] if reason else [],
        'today_signal': '题材仍在，但今天先放后看。',
        'why_today': '因为它还没有给到足够的新信息，值得保留但不该稀释今天头版。',
        'freshness': freshness,
        'changed_today': False,
        'change_note': '今天不进入主版。',
        'action': '暂不分配主版面注意力。',
        'links': repo_links(name),
        'signal_score': BASE_SCORE['deep-dive'],
        'return_trigger': '等出现可复用的新做法或更强外部佐证时再回看。',
    }


def collect_summary_highlights(text: str) -> list:
    highlights = []
    capture = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith('## What this mock demonstrates') or line.startswith('## What this run proves'):
            capture = True
            continue
        if capture and line.startswith('## '):
            break
        if capture and line.startswith('- '):
            highlights.append(normalize_sentence(line[2:]))
    return highlights[:3]


def build_x_signal_lane() -> dict:
    author_data = read_json(X_AUTHOR_SIGNALS)
    linked_data = read_json(X_LINKED_OBJECTS)
    boost_data = read_json(X_CANDIDATE_BOOSTS)
    summary_text = read(X_WATCHLIST_SUMMARY)

    collector = (
        author_data.get('collector')
        or linked_data.get('collector')
        or boost_data.get('collector')
        or 'x-watchlist-contract'
    )
    raw_status = (
        author_data.get('status')
        or linked_data.get('status')
        or boost_data.get('status')
        or ('mock-watchlist-ready' if 'First mock collector output' in summary_text else 'unknown')
    )
    if raw_status == 'skeleton-no-backend':
        mode = 'skeleton-no-backend'
        mode_label = '未接真实 backend 的 skeleton'
    elif 'mock' in raw_status or 'mock collector' in summary_text.lower() or author_data.get('items'):
        mode = 'mock-watchlist'
        mode_label = 'mock watchlist fallback'
    else:
        mode = raw_status or 'unknown'
        mode_label = raw_status or 'unknown'

    lane = {
        'collector': collector,
        'collector_status': raw_status,
        'mode': mode,
        'mode_label': mode_label,
        'signal_layer_only': True,
        'stable_ingest': False,
        'roles': ['author-signal', 'editorial-reference', 'risk/evidence'],
        'artifact_paths': {
            'author_signals': str(X_AUTHOR_SIGNALS),
            'linked_objects': str(X_LINKED_OBJECTS),
            'candidate_boosts': str(X_CANDIDATE_BOOSTS),
            'watchlist_summary': str(X_WATCHLIST_SUMMARY),
        },
        'reference_docs': X_REFERENCE_DOCS,
        'artifact_counts': {
            'author_signals': len(author_data.get('items', [])),
            'linked_objects': len(linked_data.get('items', [])),
            'candidate_boosts': len(boost_data.get('items', [])),
        },
        'summary_highlights': collect_summary_highlights(summary_text),
        'summary_excerpt': normalize_sentence(summary_text.splitlines()[2]) if len(summary_text.splitlines()) > 2 else '',
    }

    author_lookup = {}
    for item in author_data.get('items', []):
        canonical_urls = [normalize_url(url) for url in item.get('canonical_urls', []) if normalize_url(url)]
        for canonical_url in canonical_urls:
            author_lookup.setdefault(canonical_url, []).append(item)

    linked_lookup = {
        normalize_url(item.get('canonical_url')): item
        for item in linked_data.get('items', [])
        if normalize_url(item.get('canonical_url'))
    }
    boost_lookup = {
        normalize_url(item.get('canonical_url')): item
        for item in boost_data.get('items', [])
        if normalize_url(item.get('canonical_url'))
    }

    lane['lookups'] = {
        'author_lookup': author_lookup,
        'linked_lookup': linked_lookup,
        'boost_lookup': boost_lookup,
    }
    return lane


def build_author_signal_line(signals: list) -> str:
    if not signals:
        return ''
    snippets = []
    for signal in signals[:2]:
        handle = signal.get('author_handle') or 'unknown-author'
        excerpt = compact_excerpt(signal.get('text_excerpt', ''))
        if excerpt:
            snippets.append(f'{handle} 提到“{excerpt}”')
        else:
            snippets.append(f'{handle} 给了一个作者信号')
    return '；'.join(snippets) + '。'


def build_circle_note(boost: dict, linked: dict, track: str) -> str:
    author_count = int(boost.get('author_count') or len(linked.get('authors', [])) or 0)
    post_count = int(boost.get('post_count') or len(linked.get('source_posts', [])) or 0)
    repeat_convergence = bool(boost.get('repeat_convergence'))
    if repeat_convergence and author_count:
        return f'X watchlist 里有 {author_count} 位作者在短时间内重复提到同一对象，形成了{track_label(track)}的圈内冒头信号。'
    if author_count:
        return f'X watchlist 至少有 {author_count} 位作者把它带进了今天的观察面，补上了圈内热度来源。'
    if post_count:
        return f'X signal lane 里出现了 {post_count} 条相关提及，可作为今天的弱旁证。'
    return ''


def build_x_why_now(signals: list, boost: dict, item_name: str) -> str:
    if signals:
        excerpt = compact_excerpt(signals[0].get('text_excerpt', ''))
        if excerpt:
            return f'圈内作者直接把 {item_name} 的价值点说了出来：{excerpt}。'
    boost_reason = normalize_sentence(boost.get('boost_reason', ''))
    if boost_reason:
        return f'X boost 给出的理由是：{boost_reason}'
    return ''


def build_risk_note(item: dict, signals: list) -> str:
    risk_signals = [signal for signal in signals if signal.get('x_signal_role') == 'risk/evidence']
    if risk_signals:
        risk = risk_signals[0]
        handle = risk.get('author_handle') or 'unknown-author'
        excerpt = compact_excerpt(risk.get('text_excerpt', ''))
        if excerpt:
            return f'弱风险备注：{handle} 提醒“{excerpt}”。'
        return f'弱风险备注：{handle} 给了一个保守信号。'
    if 'known risk/evidence caution' in (item.get('raw_reason') or '').lower():
        return '弱风险备注：原始校准结果已提示 known risk/evidence caution，今天仍不适合把它当成无争议信号。'
    return ''


def build_x_signal(item: dict, x_lane: dict) -> dict:
    links = [normalize_url(link) for link in item.get('links', []) if normalize_url(link)]
    aliases = item_aliases(item.get('name', ''), item.get('repo', ''), links)
    lookups = x_lane.get('lookups', {})

    matched_url = ''
    linked = {}
    boost = {}
    all_signals = []
    for link in links:
        linked = lookups.get('linked_lookup', {}).get(link) or {}
        boost = lookups.get('boost_lookup', {}).get(link) or {}
        all_signals = lookups.get('author_lookup', {}).get(link) or []
        if linked or boost or all_signals:
            matched_url = link
            break

    if not matched_url:
        return {
            'matched': False,
            'signal_layer_only': True,
            'stable_ingest': False,
            'collector_status': x_lane.get('collector_status'),
            'mode': x_lane.get('mode'),
            'mode_label': x_lane.get('mode_label'),
        }

    item_specific = [signal for signal in all_signals if excerpt_mentions_item(signal.get('text_excerpt', ''), aliases)]
    scoped_signals = sorted(item_specific, key=lambda signal: -(signal.get('author_signal_weight') or 0.0))

    author_handles = []
    handle_source = [signal.get('author_handle') for signal in scoped_signals] if scoped_signals else linked.get('authors', [])
    for handle in handle_source:
        if handle and handle not in author_handles:
            author_handles.append(handle)

    signal_roles = []
    role_source = [signal.get('x_signal_role') for signal in scoped_signals] if scoped_signals else linked.get('x_signal_roles', [])
    for role in role_source:
        if role and role not in signal_roles:
            signal_roles.append(role)

    mention_types = []
    mention_source = [signal.get('mention_type') for signal in scoped_signals] if scoped_signals else linked.get('mention_types', [])
    for mention_type in mention_source:
        if mention_type and mention_type not in mention_types:
            mention_types.append(mention_type)

    author_count = int(boost.get('author_count') or len(author_handles))
    post_count = int(boost.get('post_count') or len(linked.get('source_posts', [])) or len(scoped_signals))
    repeat_convergence = bool(boost.get('repeat_convergence'))
    boost_strength = float(boost.get('boost_strength') or 0.0)
    risk_note = build_risk_note(item, scoped_signals)
    score_delta = min(12, author_count * 2 + round(boost_strength * 4) + (3 if repeat_convergence else 0) - (2 if risk_note else 0))
    if score_delta < 0:
        score_delta = 0

    return {
        'matched': True,
        'signal_layer_only': True,
        'stable_ingest': False,
        'collector_status': x_lane.get('collector_status'),
        'mode': x_lane.get('mode'),
        'mode_label': x_lane.get('mode_label'),
        'canonical_url': matched_url,
        'author_count': author_count,
        'post_count': post_count,
        'repeat_convergence': repeat_convergence,
        'boost_strength': boost_strength,
        'boost_reason': normalize_sentence(boost.get('boost_reason', '')),
        'recommended_effects': boost.get('recommended_effects', []),
        'authors': author_handles,
        'signal_roles': signal_roles,
        'mention_types': mention_types,
        'circle_note': build_circle_note(boost, linked, item.get('track', '')),
        'author_signal_line': build_author_signal_line(scoped_signals),
        'why_now': build_x_why_now(scoped_signals, boost, item.get('name', '这个对象')),
        'risk_note': risk_note,
        'score_delta': score_delta,
    }


def attach_x_signal(item: dict, x_lane: dict) -> dict:
    enriched = dict(item)
    x_signal = build_x_signal(item, x_lane)
    enriched['x_signal'] = x_signal
    if x_signal.get('matched'):
        enriched['signal_score'] += x_signal.get('score_delta', 0)
        enriched['today_signal'] = merge_sentences(enriched.get('today_signal', ''), x_signal.get('circle_note', ''))
        enriched['why_today'] = merge_sentences(enriched.get('why_today', ''), x_signal.get('why_now', ''))
        if x_signal.get('risk_note'):
            enriched['change_note'] = merge_sentences(enriched.get('change_note', ''), x_signal.get('risk_note', ''))
    return enriched


def sort_items(items: list) -> list:
    return sorted(
        items,
        key=lambda item: (-item['signal_score'], TRACK_SORT_WEIGHT.get(item.get('track', ''), 9), item['name'].lower()),
    )


def enrich_with_x(items: list, x_lane: dict) -> list:
    return [attach_x_signal(item, x_lane) for item in items]


def build_payload(applied_text: str, openclaw_text: str, x_lane: dict | None = None) -> dict:
    x_lane = x_lane or build_x_signal_lane()

    applied_adopt = enrich_with_x(
        [build_item(line, 'applied-ai-evolution', 'Adopt', 'adopt') for line in bullets_under(applied_text, 'Adopt')],
        x_lane,
    )
    applied_follow = enrich_with_x(
        [build_item(line, 'applied-ai-evolution', 'Follow / framework-to-study', 'follow') for line in bullets_under(applied_text, 'Follow / framework-to-study')],
        x_lane,
    )
    applied_official = [build_official_item(line) for line in bullets_under(applied_text, 'Official anchors')]

    openclaw_adopt = enrich_with_x(
        [build_item(line, 'openclaw-evolution', 'Adopt / adopt-candidate', 'adopt-candidate') for line in bullets_under(openclaw_text, 'Adopt / adopt-candidate')],
        x_lane,
    )
    openclaw_follow = enrich_with_x(
        [build_item(line, 'openclaw-evolution', 'Follow', 'follow') for line in bullets_under(openclaw_text, 'Follow')],
        x_lane,
    )
    openclaw_deep = [build_hold_item(line, 'openclaw-evolution') for line in bullets_under(openclaw_text, 'Deep-dive')]

    priority = sort_items(applied_adopt)[:2] + sort_items(openclaw_adopt)[:2]
    priority = sort_items(priority)
    follow = sort_items(applied_follow + openclaw_follow)
    official = applied_official[:3]
    deprioritized = sort_items(openclaw_deep)[:2]

    visible_items = priority + follow
    x_matched_items = [item for item in visible_items if (item.get('x_signal') or {}).get('matched')]
    x_risk_items = [item['name'] for item in visible_items if (item.get('x_signal') or {}).get('risk_note')]

    generated_at = datetime.now(timezone.utc)
    return {
        'title': 'daily-payload-v2',
        'generated_at': generated_at.isoformat(),
        'sources': [str(APPLIED), str(OPENCLAW)],
        'x_signal_lane': {
            'collector': x_lane.get('collector'),
            'collector_status': x_lane.get('collector_status'),
            'mode': x_lane.get('mode'),
            'mode_label': x_lane.get('mode_label'),
            'signal_layer_only': True,
            'stable_ingest': False,
            'roles': x_lane.get('roles', []),
            'artifact_paths': x_lane.get('artifact_paths', {}),
            'artifact_counts': x_lane.get('artifact_counts', {}),
            'reference_docs': x_lane.get('reference_docs', []),
            'summary_highlights': x_lane.get('summary_highlights', []),
            'summary_excerpt': x_lane.get('summary_excerpt', ''),
            'matched_item_count': len(x_matched_items),
            'matched_items': [item['name'] for item in x_matched_items],
            'risk_items': x_risk_items,
            'lane_note': 'X 只作为 author-signal / editorial-reference / weak risk 的信号层，不作为 stable ingest。',
        },
        'summary': {
            'priority': priority,
            'follow': follow,
            'official_anchors': official,
            'deprioritized': deprioritized,
        },
        'editorial_signals': {
            'changed_today_count': sum(1 for item in priority + follow if item.get('changed_today')),
            'priority_tracks': sorted({item['track_label'] for item in priority}),
            'front_page_candidates': [item['name'] for item in priority[:3]],
            'x_matched_items': [item['name'] for item in x_matched_items],
        },
    }


def main():
    payload = build_payload(read(APPLIED), read(OPENCLAW))
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(str(OUT))


if __name__ == '__main__':
    main()
