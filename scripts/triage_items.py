#!/usr/bin/env python3
import argparse
import json
import re


GENERAL_HIGH = [
    'ai', 'llm', 'open source', 'cli', 'sdk', 'api', 'tooling', 'release', 'launch',
    'github actions', 'copilot', 'workflow', 'automation', 'prompt', 'model'
]
GENERAL_MEDIUM = [
    'python', 'rust', 'go', 'typescript', 'docker', 'kubernetes', 'database',
    'security', 'git', 'github', 'devtools', 'oss', 'parser', 'search',
    'compiler', 'middleware', 'benchmark', 'performance', 'infra', 'deployment',
    'framework', 'library', 'testing', 'release notes', 'actions'
]
GENERAL_LOW = ['funding', 'opinion', 'hiring', 'layoffs', 'sales', 'marketing', 'politics', 'celebrity', 'sports', 'attack', 'war', 'military', 'missile', 'iran', 'uk']

AGENTIC_HIGH = [
    'openclaw', 'agent', 'agents', 'agentic', 'ai agent', 'coding agent', 'workflow',
    'automation', 'rss', 'prompt', 'tooling', 'cli', 'sdk', 'api', 'copilot',
    'model context', 'rag', 'vector', 'inference', 'tool calling', 'multi-agent'
]
AGENTIC_MEDIUM = [
    'llm', 'github actions', 'github', 'search', 'parser', 'library', 'framework',
    'devtools', 'open source', 'release', 'middleware', 'orchestration', 'evaluation'
]
AGENTIC_LOW = ['politics', 'celebrity', 'sports', 'sales', 'marketing', 'opinion']

SOLID_TECH_FEEDS = ['github blog', 'hacker news']


def norm(text):
    return re.sub(r'\s+', ' ', (text or '').strip().lower())


def score_text(text, words, weight):
    total = 0.0
    hits = 0
    for w in words:
        if w and w in text:
            total += weight
            hits += 1
    return total, hits


def get_profile(mode):
    if mode == 'agentic':
        return {
            'high': AGENTIC_HIGH,
            'medium': AGENTIC_MEDIUM,
            'low': AGENTIC_LOW,
            'w_high': 1.3,
            'w_medium': 0.8,
            'w_low': 0.9,
            'send_threshold': 3.6,
            'digest_threshold': 1.3,
        }
    return {
        'high': GENERAL_HIGH,
        'medium': GENERAL_MEDIUM,
        'low': GENERAL_LOW,
        'w_high': 1.1,
        'w_medium': 0.7,
        'w_low': 0.9,
        'send_threshold': 3.4,
        'digest_threshold': 1.4,
    }


def decide(item, default_mode, ignore_feed_mode=False):
    mode = default_mode if ignore_feed_mode else (item.get('triage_mode') or default_mode)
    profile = get_profile(mode)
    title = norm(item.get('title'))
    summary = norm(item.get('summary'))
    feed_name = norm(item.get('feed_name'))
    tags = [norm(t) for t in item.get('tags', [])]
    priority_topics = [norm(t) for t in item.get('priority_topics', [])]
    boost_keywords = [norm(t) for t in item.get('boost_keywords', [])]
    suppress_keywords = [norm(t) for t in item.get('suppress_keywords', [])]
    text = ' '.join([title, summary, feed_name, ' '.join(tags)])

    score = 0.0
    high_score, high_hits = score_text(text, profile['high'], profile['w_high'])
    med_score, med_hits = score_text(text, profile['medium'], profile['w_medium'])
    low_score, low_hits = score_text(text, profile['low'], profile['w_low'])
    score += high_score + med_score - low_score
    base_hits = high_hits + med_hits

    include = [norm(x) for x in item.get('include', [])]
    exclude = [norm(x) for x in item.get('exclude', [])]
    if include:
        if any(x in text for x in include):
            score += 1.0
            base_hits += 1
        else:
            score -= 0.8
    if exclude and any(x in text for x in exclude):
        score -= 3.0

    boost_score, boost_hits = score_text(text, boost_keywords, 0.35)
    priority_score, priority_hits = score_text(text, priority_topics, 0.25)
    suppress_score, suppress_hits = score_text(text, suppress_keywords, 0.8)
    score += boost_score + priority_score - suppress_score

    if title.startswith('show hn:'):
        score += 0.9
        base_hits += 1
    if any(feed in feed_name for feed in SOLID_TECH_FEEDS):
        score += 0.4
    if mode == 'general-tech':
        if 'github blog' in feed_name and ('github' in text or 'actions' in text or 'copilot' in text or 'open source' in text):
            score += 0.6
            base_hits += 1
        if 'open source' in text or 'sdk' in text or 'library' in text or 'framework' in text:
            score += 0.4
            base_hits += 1
        if any(x in text for x in ['attack', 'war', 'military', 'missile', 'election', 'president', 'prime minister']):
            score -= 1.6
    else:
        if 'openclaw' in text or 'agent' in text or 'workflow' in text or 'automation' in text:
            score += 0.9
            base_hits += 1
        if 'ai-assisted' in text or 'tooling' in text or 'sdlc' in text or 'repo template' in text:
            score += 0.7
            base_hits += 1
        if 'rss' in text:
            score += 0.5
            base_hits += 1
        if 'github blog' in feed_name and ('copilot' in text or 'actions' in text or 'workflow' in text):
            score += 0.6
            base_hits += 1
    if summary == 'comments':
        score -= 0.1

    # Guardrail: config keywords can help, but cannot alone promote weak items to send.
    if base_hits == 0 and (boost_hits > 0 or priority_hits > 0):
        score = min(score, profile['digest_threshold'] - 0.05)

    if score >= profile['send_threshold'] and base_hits >= 2:
        decision = 'send'
        reason = f'High-signal match for {mode} curation goals'
    elif score >= profile['digest_threshold']:
        decision = 'digest'
        reason = f'Good fit for {mode} roundup'
    else:
        decision = 'drop'
        reason = f'Low relevance for {mode} curation goals'

    return {
        **item,
        'triage': {
            'mode': mode,
            'decision': decision,
            'score': round(score, 2),
            'reason': reason,
            'debug': {
                'base_hits': base_hits,
                'boost_hits': boost_hits,
                'priority_hits': priority_hits,
                'suppress_hits': suppress_hits,
            }
        }
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--mode', choices=['general-tech', 'agentic'], default='general-tech')
    ap.add_argument('--ignore-feed-mode', action='store_true')
    args = ap.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    items = data.get('new_items', [])

    triaged = [decide(item, args.mode, ignore_feed_mode=args.ignore_feed_mode) for item in items]
    counts = {'send': 0, 'digest': 0, 'drop': 0}
    for item in triaged:
        counts[item['triage']['decision']] += 1

    print(json.dumps({
        'ok': True,
        'default_mode': args.mode,
        'ignore_feed_mode': args.ignore_feed_mode,
        'items': triaged,
        'counts': counts,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
