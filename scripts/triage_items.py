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
    'security', 'git', 'github', 'devtools', 'oss', 'parser', 'search'
]

LOW_SIGNAL = [
    'funding', 'opinion', 'hiring', 'layoffs', 'sales', 'marketing', 'politics',
    'celebrity', 'sports', 'macrumors'
]


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
    score += score_text(text, HIGH_SIGNAL, 1.2)
    score += score_text(text, MEDIUM_SIGNAL, 0.6)
    score -= score_text(text, LOW_SIGNAL, 1.0)

    include = [norm(x) for x in item.get('include', [])]
    exclude = [norm(x) for x in item.get('exclude', [])]
    if include:
        if any(x in text for x in include):
            score += 1.5
        else:
            score -= 1.0
    if exclude and any(x in text for x in exclude):
        score -= 3.0

    if title.startswith('show hn:'):
        score += 0.8
    if 'github blog' in feed_name:
        score += 0.6
    if 'hacker news' in feed_name:
        score += 0.4

    if score >= 3.0:
        decision = 'send'
        reason = 'High-signal match for tracked technical/agent topics'
    elif score >= 1.4:
        decision = 'digest'
        reason = 'Relevant enough for roundup, but not urgent'
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
