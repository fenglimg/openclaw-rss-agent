#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict

REPO_RE = re.compile(r'https://github\.com/([^/]+)/([^/#?]+)')
KEYWORDS = [
    'openclaw', 'claude code', 'codex', 'gemini', 'gemini cli', 'mcp', 'skill',
    'workflow', 'template', 'scaffold', 'agent', 'tooling', 'automation'
]


def extract_repo(url):
    if not url:
        return None
    m = REPO_RE.search(url)
    if not m:
        return None
    owner, repo = m.group(1), m.group(2)
    repo = repo.removesuffix('.git')
    return f'{owner}/{repo}'


def gh_json(args):
    try:
        out = subprocess.check_output(['gh', *args], text=True)
        return json.loads(out)
    except Exception:
        return None


def normalize_topics(value):
    out = []
    for t in value or []:
        if isinstance(t, str):
            out.append(t)
        elif isinstance(t, dict):
            out.append(t.get('name', ''))
    return [x for x in out if x]


def score_repo(item, repo_meta):
    text = ((item.get('title') or '') + ' ' + (item.get('summary') or '')).lower()
    stars = repo_meta.get('stargazerCount', 0)
    pushed = repo_meta.get('pushedAt') or ''
    topics_text = ' '.join(normalize_topics(repo_meta.get('repositoryTopics', []))).lower()
    score = 0.0
    if stars >= 50000:
        score += 3.0
    elif stars >= 10000:
        score += 2.2
    elif stars >= 3000:
        score += 1.4
    elif stars >= 500:
        score += 0.7

    keyword_hits = sum(1 for x in KEYWORDS if x in text or x in (repo_meta.get('description') or '').lower() or x in topics_text)
    score += min(keyword_hits * 0.45, 2.0)

    if repo_meta.get('isTemplate'):
        score += 0.8
    if any(x in text for x in ['template', 'scaffold', 'workflow', 'mcp', 'skill']):
        score += 0.8
    if pushed:
        score += 0.4
    return round(score, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    args = ap.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    items = data.get('items', [])
    repos = {}
    repo_items = defaultdict(list)
    for item in items:
        repo = extract_repo(item.get('link'))
        if repo:
            repo_items[repo].append(item)

    radar = []
    for repo, linked_items in repo_items.items():
        meta = gh_json(['repo', 'view', repo, '--json', 'nameWithOwner,description,stargazerCount,forkCount,pushedAt,isTemplate,repositoryTopics,url'])
        if not meta:
            continue
        best_item = max(linked_items, key=lambda x: x.get('triage', {}).get('enriched_score', x.get('triage', {}).get('score', 0)))
        radar.append({
            'repo': meta.get('nameWithOwner') or repo,
            'url': meta.get('url') or f'https://github.com/{repo}',
            'description': meta.get('description') or '',
            'stars': meta.get('stargazerCount', 0),
            'forks': meta.get('forkCount', 0),
            'isTemplate': meta.get('isTemplate', False),
            'topics': meta.get('repositoryTopics', []),
            'linked_title': best_item.get('title') or '',
            'linked_feed': best_item.get('feed_name') or best_item.get('feed_id') or '',
            'score': score_repo(best_item, meta),
        })

    radar.sort(key=lambda x: (x['score'], x['stars']), reverse=True)
    print(json.dumps({'ok': True, 'repos': radar[:5]}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
