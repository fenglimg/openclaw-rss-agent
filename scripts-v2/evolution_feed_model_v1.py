#!/usr/bin/env python3
import re


ACTION_BY_JUDGMENT = {
    'adopt': 'try_now',
    'adopt-candidate': 'adopt_candidate',
    'follow': 'follow',
    'official-anchor': 'official_anchor',
    'deep-dive': 'deep_dive',
}

ACTION_LABEL = {
    'try_now': '马上试',
    'follow': '继续跟进',
    'adopt_candidate': '采纳候选',
    'official_anchor': '官方基线',
    'deep_dive': '深入研究',
    'risk_watch': '风险观察',
    'ignore_for_now': '暂时忽略',
}

AUDIENCE_LABEL = {
    'user': '用户升级',
    'openclaw': 'OpenClaw 进化',
    'both': '双向收益',
}

OBJECT_TYPE_OVERRIDES = {
    'agent browser': 'skill',
    'summarize': 'skill',
    'github': 'skill',
    'self-improving-agent': 'capability',
    'proactive agent': 'capability',
    'gog': 'workflow',
    'polymarket': 'workflow',
    'weather': 'skill',
}

TARGET_AUDIENCE_OVERRIDES = {
    'agent browser': 'both',
    'self-improving-agent': 'both',
    'proactive agent': 'both',
}


def normalize_sentence(text: str) -> str:
    cleaned = re.sub(r'\s+', ' ', text or '').strip().replace('`', '')
    cleaned = re.sub(r'[.。！？]+$', '', cleaned)
    if cleaned and cleaned[-1] not in '。！？':
        cleaned += '。'
    return cleaned


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


def compact_excerpt(text: str, limit: int = 110) -> str:
    cleaned = re.sub(r'\s+', ' ', text or '').strip().replace('"', '”')
    if len(cleaned) > limit:
        cleaned = cleaned[: limit - 3].rstrip() + '...'
    return cleaned


def slugify(text: str) -> str:
    lowered = (text or '').lower().strip()
    lowered = lowered.replace('_', '-')
    return re.sub(r'[^a-z0-9]+', '-', lowered).strip('-') or 'unnamed'


def infer_object_type(item: dict) -> str:
    name = (item.get('name') or '').strip()
    repo = (item.get('repo') or '').strip()
    lowered = name.lower()
    judgment = item.get('judgment')
    if judgment == 'official-anchor':
        return 'official-anchor'
    if lowered in OBJECT_TYPE_OVERRIDES:
        return OBJECT_TYPE_OVERRIDES[lowered]
    if repo and '/' in repo:
        return 'repo'
    if 'agent' in lowered:
        return 'capability'
    if item.get('track') == 'openclaw-evolution':
        return 'skill'
    return 'workflow'


def infer_target_audience(item: dict, object_type: str) -> str:
    lowered = (item.get('name') or '').lower().strip()
    if lowered in TARGET_AUDIENCE_OVERRIDES:
        return TARGET_AUDIENCE_OVERRIDES[lowered]
    judgment = item.get('judgment')
    track = item.get('track')
    if judgment == 'official-anchor':
        return 'both'
    if track == 'openclaw-evolution' and object_type in {'skill', 'capability'}:
        return 'openclaw'
    if track == 'openclaw-evolution':
        return 'both'
    return 'user'


def recommended_action_for(item: dict) -> str:
    if item.get('x_signal', {}).get('risk_note') and item.get('judgment') == 'follow':
        return 'risk_watch'
    return ACTION_BY_JUDGMENT.get(item.get('judgment'), 'follow')


def build_canonical_id(item: dict, object_type: str) -> str:
    repo = (item.get('repo') or '').strip().lower()
    if repo and '/' in repo:
        return f'repo:{repo}'
    if object_type in {'repo', 'official-anchor'}:
        for link in item.get('links', []):
            normalized = normalize_url(link)
            if normalized.startswith('https://github.com/'):
                return f"repo:{normalized[len('https://github.com/'):]}"
    return f'{object_type}:{slugify(item.get("name", "unnamed"))}'


def build_stable_evidence(item: dict) -> list:
    evidence = []
    seen = set()
    for index, link in enumerate(item.get('links', []), start=1):
        normalized = normalize_url(link)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        source_type = 'github-repo' if normalized.startswith('https://github.com/') else 'stable-link'
        if item.get('judgment') == 'official-anchor':
            source_type = 'official-docs'
        evidence.append(
            {
                'lane': 'stable',
                'source_type': source_type,
                'role': 'stable-source',
                'label': '主链接' if index == 1 else f'稳定来源 {index}',
                'url': normalized,
                'excerpt': '',
                'note': normalize_sentence(item.get('today_signal', '')),
            }
        )
    return evidence


def build_signal_evidence(item: dict) -> list:
    x_signal = item.get('x_signal') or {}
    if not x_signal.get('matched'):
        return []

    evidence = []
    canonical_url = normalize_url(x_signal.get('canonical_url', ''))
    if canonical_url:
        evidence.append(
            {
                'lane': 'signal',
                'source_type': 'x-linked-object',
                'role': 'editorial-reference',
                'label': 'X linked object',
                'url': canonical_url,
                'excerpt': '',
                'note': normalize_sentence(x_signal.get('circle_note', '')),
            }
        )

    if x_signal.get('author_signal_line'):
        evidence.append(
            {
                'lane': 'signal',
                'source_type': 'x-author-signal',
                'role': 'author-signal',
                'label': '作者信号',
                'url': '',
                'excerpt': compact_excerpt(x_signal.get('author_signal_line', '')),
                'note': normalize_sentence(x_signal.get('why_now', '')),
            }
        )

    if x_signal.get('boost_reason'):
        evidence.append(
            {
                'lane': 'signal',
                'source_type': 'x-candidate-boost',
                'role': 'editorial-reference',
                'label': 'X boost',
                'url': '',
                'excerpt': compact_excerpt(x_signal.get('boost_reason', '')),
                'note': normalize_sentence(x_signal.get('circle_note', '')),
            }
        )

    if x_signal.get('risk_note'):
        evidence.append(
            {
                'lane': 'signal',
                'source_type': 'x-risk-note',
                'role': 'risk/evidence',
                'label': '弱风险',
                'url': '',
                'excerpt': compact_excerpt(x_signal.get('risk_note', '')),
                'note': normalize_sentence(x_signal.get('risk_note', '')),
            }
        )
    return evidence


def build_verification_evidence(item: dict) -> list:
    verification = []
    if item.get('raw_reason'):
        verification.append(
            {
                'lane': 'verification',
                'source_type': 'calibration-judgment',
                'role': 'judgment',
                'label': item.get('source_section', 'Judgment'),
                'url': '',
                'excerpt': compact_excerpt(item.get('raw_reason', '')),
                'note': normalize_sentence(item.get('change_note', '')),
            }
        )
    return verification


def compute_dimension_scores(item: dict, target_audience: str, recommended_action: str, stable_evidence: list, signal_evidence: list) -> dict:
    changed_today = bool(item.get('changed_today'))
    x_signal = item.get('x_signal') or {}
    author_count = int(x_signal.get('author_count') or 0)
    repeat_convergence = bool(x_signal.get('repeat_convergence'))

    relevance = 5 if target_audience == 'both' else 4
    if item.get('judgment') == 'official-anchor':
        relevance = 4

    upgrade_value = 5 if changed_today else 4 if item.get('judgment') in {'adopt', 'adopt-candidate'} else 3
    if recommended_action in {'deep_dive', 'risk_watch'}:
        upgrade_value = max(2, upgrade_value - 1)

    why_now_score = 5 if changed_today else 3
    if x_signal.get('matched'):
        why_now_score += 1
    if repeat_convergence:
        why_now_score += 1
    why_now_score = min(5, why_now_score)

    signal_quality = 2 + min(2, len(stable_evidence))
    if x_signal.get('matched'):
        signal_quality += 1
    if author_count >= 2 or repeat_convergence:
        signal_quality += 1
    signal_quality = min(5, signal_quality)

    actionability = 5 if recommended_action in {'try_now', 'adopt_candidate'} else 4 if recommended_action in {'follow', 'official_anchor'} else 3
    if not item.get('links'):
        actionability = max(2, actionability - 1)

    saturation = 0
    repeat_penalty = 0
    serve_score = relevance + upgrade_value + why_now_score + signal_quality + actionability - saturation - repeat_penalty
    return {
        'relevance': relevance,
        'upgrade_value': upgrade_value,
        'why_now_score': why_now_score,
        'signal_quality': signal_quality,
        'actionability': actionability,
        'saturation': saturation,
        'repeat_penalty': repeat_penalty,
        'serve_score': serve_score,
    }


def build_evidence_summary(stable_evidence: list, signal_evidence: list, verification_evidence: list) -> dict:
    label_preview = []
    for lane in (stable_evidence, signal_evidence, verification_evidence):
        for entry in lane:
            label = entry.get('label')
            if label and label not in label_preview:
                label_preview.append(label)
            if len(label_preview) >= 3:
                break
        if len(label_preview) >= 3:
            break

    lanes_with_evidence = []
    for lane_name, entries in (
        ('stable', stable_evidence),
        ('signal', signal_evidence),
        ('verification', verification_evidence),
    ):
        if entries:
            lanes_with_evidence.append(lane_name)

    return {
        'stable_count': len(stable_evidence),
        'signal_count': len(signal_evidence),
        'verification_count': len(verification_evidence),
        'lanes_with_evidence': lanes_with_evidence,
        'label_preview': label_preview,
    }


def build_candidate_object(item: dict, queue: str) -> dict:
    object_type = infer_object_type(item)
    target_audience = infer_target_audience(item, object_type)
    recommended_action = recommended_action_for(item)
    stable_evidence = build_stable_evidence(item)
    signal_evidence = build_signal_evidence(item)
    verification_evidence = build_verification_evidence(item)
    scores = compute_dimension_scores(item, target_audience, recommended_action, stable_evidence, signal_evidence)
    why_now_text = normalize_sentence((item.get('x_signal') or {}).get('why_now', '') or item.get('why_today', ''))
    evidence_summary = build_evidence_summary(stable_evidence, signal_evidence, verification_evidence)

    candidate = dict(item)
    candidate.update(
        {
            'schema_version': 'candidate-object-v1',
            'canonical_id': build_canonical_id(item, object_type),
            'object_type': object_type,
            'queue': queue,
            'target_audience': target_audience,
            'target_audience_label': AUDIENCE_LABEL[target_audience],
            'recommended_action': recommended_action,
            'recommended_action_label': ACTION_LABEL[recommended_action],
            'why_now': why_now_text,
            'recommended_action_reason': normalize_sentence(item.get('action', '')),
            'upgrade_value_reason': normalize_sentence(item.get('today_signal', '')),
            'evidence_lanes': {
                'stable': stable_evidence,
                'signal': signal_evidence,
                'verification': verification_evidence,
            },
            'evidence_summary': evidence_summary,
        }
    )
    candidate.update(scores)
    return candidate


def build_evidence_lane_contract() -> dict:
    return {
        'stable': {
            'description': '稳定主源，优先承载 GitHub、官方文档、官方 changelog 等可复查证据。',
            'source_types': ['github-repo', 'official-docs', 'stable-link'],
        },
        'signal': {
            'description': '信号增强层，只提供 why-now、editorial weighting、weak risk。',
            'source_types': ['x-linked-object', 'x-author-signal', 'x-candidate-boost', 'x-risk-note'],
        },
        'verification': {
            'description': '验证与扩展层，承载校准判断、search enrichment、补背景说明。',
            'source_types': ['calibration-judgment', 'search-enrichment', 'editorial-verification'],
        },
    }
