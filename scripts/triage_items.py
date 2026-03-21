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
GENERAL_LOW = ['funding', 'opinion', 'hiring', 'layoffs', 'sales', 'marketing', 'politics', 'celebrity', 'sports']

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
    for w in words:
        if w in text:
            total += weight
    return total


def get_profile(mode):
    if mode == 'agentic':
        return {
            'high': AGENTIC_HIGH,
            'medium': AGENTIC_MEDIUM,
            'low': AGENTIC_LOW,
            'w_high': 1.3,
            'w_medium': 0.75,
            'w_low': 0.9,
            'send_threshold': 3.2,
            'digest_threshold': 1.5,
        }
    return {
        'high': GENERAL_HIGH,
        'medium': GENERAL_MEDIUM,
        'low': GENERAL_LOW,
        'w_high': 1.1,
        'w_medium': 0.7,
        'w_low': 0.9,
        'send_threshold': 3.0,
        'digest_threshold': 1.2,
    }


def decide(item, mode):
    profile = get_profile(mode)
    title = norm(item.get('title'))
    summary = norm(item.get('summary'))
    feed_name = norm(item.get('feed_name'))
    tags = [norm(t) for t in item.get('tags', [])]
    text = ' '.join([title, summary, feed_name, ' '.join(tags)])

    score = 0.0
    score += score_text(text, profile['high'], profile['w_high'])
    score += score_text(text, profile['medium'], profile['w_medium'])
    score -= score_text(text, profile['low'], profile['w_low'])

    include = [norm(x) for x in item.get('include', [])]
    exclude = [norm(x) for x in item.get('exclude', [])]
    if include:
        if any(x in text for x in include):
            score += 1.6
        else:
            score -= 0.8
    if exclude and any(x in text for x in exclude):
        score -= 3.0

    if title.startswith('show hn:'):
        score += 0.9
    if any(feed in feed_name for feed in SOLID_TECH_FEEDS):
        score += 0.5
    if mode == 'general-tech':
        if 'github blog' in feed_name and ('github' in text or 'actions' in text or 'copilot' in text or 'open source' in text):
            score += 0.8
        if 'open source' in text or 'sdk' in text or 'library' in text or 'framework' in text:
            score += 0.5
    else:
        if 'openclaw' in text or 'agent' in text or 'workflow' in text or 'automation' in text:
            score += 0.9
        if 'rss' in text:
            score += 0.7
        if 'github blog' in feed_name and ('copilot' in text or 'actions' in text or 'workflow' in text):
            score += 0.6
    if summary == 'comments':
        score -= 0.1

    if score >= profile['send_threshold']:
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
        }
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--mode', choices=['general-tech', 'agentic'], default='general-tech')
    args = ap.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    items = data.get('new_items', [])

    triaged = [decide(item, args.mode) for item in items]
    counts = {'send': 0, 'digest': 0, 'drop': 0}
    for item in triaged:
        counts[item['triage']['decision']] += 1

    print(json.dumps({
        'ok': True,
        'mode': args.mode,
        'items': triaged,
        'counts': counts,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
