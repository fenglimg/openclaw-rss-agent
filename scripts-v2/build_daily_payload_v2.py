#!/usr/bin/env python3
import json
import re
from datetime import datetime, timezone
from pathlib import Path

APPLIED = Path('outputs/applied-ai-evolution-brief-v5.md')
OPENCLAW = Path('outputs/openclaw-evolution-brief-v15.md')
OUT = Path('test-output/daily-payload-v2.json')

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


def sort_items(items: list) -> list:
    return sorted(
        items,
        key=lambda item: (-item['signal_score'], TRACK_SORT_WEIGHT.get(item.get('track', ''), 9), item['name'].lower()),
    )


def build_payload(applied_text: str, openclaw_text: str) -> dict:
    applied_adopt = [build_item(line, 'applied-ai-evolution', 'Adopt', 'adopt') for line in bullets_under(applied_text, 'Adopt')]
    applied_follow = [build_item(line, 'applied-ai-evolution', 'Follow / framework-to-study', 'follow') for line in bullets_under(applied_text, 'Follow / framework-to-study')]
    applied_official = [build_official_item(line) for line in bullets_under(applied_text, 'Official anchors')]

    openclaw_adopt = [build_item(line, 'openclaw-evolution', 'Adopt / adopt-candidate', 'adopt-candidate') for line in bullets_under(openclaw_text, 'Adopt / adopt-candidate')]
    openclaw_follow = [build_item(line, 'openclaw-evolution', 'Follow', 'follow') for line in bullets_under(openclaw_text, 'Follow')]
    openclaw_deep = [build_hold_item(line, 'openclaw-evolution') for line in bullets_under(openclaw_text, 'Deep-dive')]

    priority = sort_items(applied_adopt)[:2] + sort_items(openclaw_adopt)[:2]
    priority = sort_items(priority)
    follow = sort_items(applied_follow + openclaw_follow)
    official = applied_official[:3]
    deprioritized = sort_items(openclaw_deep)[:2]

    generated_at = datetime.now(timezone.utc)
    return {
        'title': 'daily-payload-v2',
        'generated_at': generated_at.isoformat(),
        'sources': [str(APPLIED), str(OPENCLAW)],
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
        },
    }


def main():
    payload = build_payload(read(APPLIED), read(OPENCLAW))
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(str(OUT))


if __name__ == '__main__':
    main()
