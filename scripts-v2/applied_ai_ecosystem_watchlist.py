#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path

import yaml


def gh_repo(repo):
    try:
        out = subprocess.check_output([
            'gh', 'repo', 'view', repo,
            '--json', 'nameWithOwner,description,stargazerCount,forkCount,pushedAt,isArchived,url,repositoryTopics'
        ], text=True)
        return json.loads(out)
    except Exception:
        return None


def topic_names(meta):
    out = []
    for t in meta.get('repositoryTopics', []) or []:
        if isinstance(t, str):
            out.append(t)
        elif isinstance(t, dict):
            out.append(t.get('name', ''))
    return [x for x in out if x]


def score(entry, meta):
    text = ' '.join([
        entry.get('repo', ''),
        entry.get('role', ''),
        meta.get('description', ''),
        ' '.join(topic_names(meta)),
        ' '.join(entry.get('tags', [])),
    ]).lower()
    stars = meta.get('stargazerCount', 0)
    s = 0.0
    if stars >= 50000:
        s += 3.0
    elif stars >= 10000:
        s += 2.2
    elif stars >= 3000:
        s += 1.4
    elif stars >= 1000:
        s += 0.8
    keyword_groups = ['claude-code', 'codex', 'gemini-cli', 'mcp', 'skill', 'workflow', 'plugin', 'template', 'orchestration']
    hits = sum(1 for k in keyword_groups if k in text)
    s += min(hits * 0.4, 2.4)
    if entry.get('role') in ('framework-core', 'workflow-framework', 'agent-framework'):
        s += 0.8
    if entry.get('role') in ('official-anchor',):
        s += 0.6
    return round(s, 2), hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--watchlist', default='watchlists/applied-ai-ecosystem.yaml')
    args = ap.parse_args()

    data = yaml.safe_load(Path(args.watchlist).read_text(encoding='utf-8'))
    items = []
    for section in ('entries', 'anchors'):
        for entry in data.get(section, []):
            meta = gh_repo(entry['repo'])
            if not meta:
                continue
            watch_score, keyword_hits = score(entry, meta)
            items.append({
                'repo': meta.get('nameWithOwner', entry['repo']),
                'url': meta.get('url', f"https://github.com/{entry['repo']}"),
                'role': entry.get('role', ''),
                'tags': entry.get('tags', []),
                'description': meta.get('description', ''),
                'stars': meta.get('stargazerCount', 0),
                'forks': meta.get('forkCount', 0),
                'pushedAt': meta.get('pushedAt', ''),
                'topics': topic_names(meta),
                'keyword_hits': keyword_hits,
                'watch_score': watch_score,
                'section': section,
            })
    items.sort(key=lambda x: (x['watch_score'], x['stars']), reverse=True)
    print(json.dumps({
        'ok': True,
        'watchlist': data.get('id'),
        'count': len(items),
        'items': items,
        'indexes': data.get('indexes', []),
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
