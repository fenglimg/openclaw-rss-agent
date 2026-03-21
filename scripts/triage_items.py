#!/usr/bin/env python3
import argparse
import json
import re


HIGH_SIGNAL = [
    'openclaw', 'agent', 'agents', 'ai', 'llm', 'rss', 'automation', 'workflow',
    'github actions', 'copilot', 'release', 'launch', 'open source', 'cli',
    'sdk', 'api', 'tooling', 'prompt', 'model', 'inference', 'vector', 'rag'
]

MEDIUM_SIGNAL = [
    'python', 'rust', 'go', 'typescript', 'docker', 'kubernetes', 'database',
    'security', 'git', 'github', 'devtools', 'oss', 'parser', 'search',
    'compiler', 'middleware', 'benchmark', 'performance', 'infra', 'deployment',
    'framework', 'library', 'sdk', 'testing', 'release notes', 'actions'
]

LOW_SIGNAL = [
    'funding', 'opinion', 'hiring', 'layoffs', 'sales', 'marketing', 'politics',
    'celebrity', 'sports'
]

SOLID_TECH_FEEDS = ['github blog', 'hacker news']


def norm(text):
    return re.sub(r'\s+', ' ', (text or '').strip().lower())


def score_text(text, words, weight):
    total = 0.0
    for w in words:
        if w in text:
            total += weight
    return total


def decide(item):
    title = norm(item.get('title'))
    summary = norm(item.get('summary'))
    feed_name = norm(item.get('feed_name'))
    tags = [norm(t) for t in item.get('tags', [])]
    text = ' '.join([title, summary, feed_name, ' '.join(tags)])

    score = 0.0
    score += score_text(text, HIGH_SIGNAL, 1.1)
    score += score_text(text, MEDIUM_SIGNAL, 0.7)
    score -= score_text(text, LOW_SIGNAL, 0.9)

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
    if 'github blog' in feed_name and ('github' in text or 'actions' in text or 'copilot' in text or 'open source' in text):
        score += 0.8
    if 'open source' in text or 'sdk' in text or 'library' in text or 'framework' in text:
        score += 0.5
    if summary == 'comments':
        score -= 0.1

    if score >= 3.0:
        decision = 'send'
        reason = 'High-signal match for tracked technical/agent topics'
    elif score >= 1.2:
        decision = 'digest'
        reason = 'Good fit for a technical roundup'
    else:
        decision = 'drop'
        reason = 'Low relevance or low signal for current RSS curation goals'

    return {
        **item,
        'triage': {
            'decision': decision,
            'score': round(score, 2),
            'reason': reason,
        }
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    args = ap.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    items = data.get('new_items', [])

    triaged = [decide(item) for item in items]
    counts = {'send': 0, 'digest': 0, 'drop': 0}
    for item in triaged:
        counts[item['triage']['decision']] += 1

    print(json.dumps({
        'ok': True,
        'items': triaged,
        'counts': counts,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
