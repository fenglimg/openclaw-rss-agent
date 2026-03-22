#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from urllib.request import urlopen, Request

FEED_URL = 'https://mshibanami.github.io/GitHubTrendingRSS/daily/all.xml'
REPO_RE = re.compile(r'https://github\.com/([^/]+)/([^/#?]+)')
KEYWORDS = [
    'openclaw', 'claude', 'codex', 'gemini', 'mcp', 'skill', 'workflow',
    'agent', 'agents', 'template', 'scaffold', 'automation', 'tooling'
]


def fetch_feed(url):
    req = Request(url, headers={'User-Agent': 'openclaw-rss-agent/2.0'})
    with urlopen(req, timeout=30) as resp:
        return resp.read()


def parse_items(xml_bytes):
    root = ET.fromstring(xml_bytes)
    channel = root.find('channel')
    items = []
    if channel is None:
        return items
    for item in channel.findall('item')[:20]:
        items.append({
            'title': item.findtext('title', default='').strip(),
            'link': item.findtext('link', default='').strip(),
            'description': item.findtext('description', default='').strip(),
            'published': item.findtext('pubDate', default='').strip(),
        })
    return items


def extract_repo(url):
    m = REPO_RE.search(url or '')
    if not m:
        return None
    repo = f"{m.group(1)}/{m.group(2).removesuffix('.git')}"
    return repo


def gh_repo(repo):
    try:
        out = subprocess.check_output([
            'gh', 'repo', 'view', repo,
            '--json', 'nameWithOwner,description,stargazerCount,forkCount,pushedAt,isTemplate,repositoryTopics,url'
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


def score(item, meta):
    text = ' '.join([
        item.get('title', ''),
        item.get('description', ''),
        meta.get('description', ''),
        ' '.join(topic_names(meta)),
    ]).lower()
    stars = meta.get('stargazerCount', 0)
    s = 0.0
    if stars >= 50000:
        s += 3.0
    elif stars >= 10000:
        s += 2.2
    elif stars >= 3000:
        s += 1.6
    elif stars >= 500:
        s += 0.8
    hits = sum(1 for k in KEYWORDS if k in text)
    s += min(hits * 0.45, 2.2)
    if meta.get('isTemplate'):
        s += 0.8
    if any(x in text for x in ['template', 'scaffold', 'workflow', 'mcp', 'skill']):
        s += 0.8
    return round(s, 2), hits


def classify(item, meta, keyword_hits):
    text = ' '.join([
        item.get('title', ''),
        item.get('description', ''),
        meta.get('description', ''),
        ' '.join(topic_names(meta)),
    ]).lower()
    if any(x in text for x in ['mcp', 'mcp-server', 'model-context-protocol']):
        return 'candidate_high_signal_repo'
    if any(x in text for x in ['template', 'scaffold', 'starter']):
        return 'candidate_try_now'
    if keyword_hits >= 2:
        return 'candidate_follow_project'
    return 'project_radar'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--feed-url', default=FEED_URL)
    ap.add_argument('--limit', type=int, default=8)
    args = ap.parse_args()

    xml_bytes = fetch_feed(args.feed_url)
    items = parse_items(xml_bytes)
    out = []
    for item in items:
        repo = extract_repo(item.get('link'))
        if not repo:
            continue
        meta = gh_repo(repo)
        if not meta:
            continue
        repo_score, keyword_hits = score(item, meta)
        out.append({
            'bucket': classify(item, meta, keyword_hits),
            'repo': meta.get('nameWithOwner') or repo,
            'url': meta.get('url') or item.get('link'),
            'title': item.get('title'),
            'description': meta.get('description') or item.get('description') or '',
            'stars': meta.get('stargazerCount', 0),
            'forks': meta.get('forkCount', 0),
            'isTemplate': meta.get('isTemplate', False),
            'topics': topic_names(meta),
            'score': repo_score,
            'keyword_hits': keyword_hits,
            'profile': 'applied-ai-evolution',
            'source_pack': 'project-radar',
            'source': 'github-trending-rss',
        })

    out.sort(key=lambda x: (x['score'], x['stars']), reverse=True)
    print(json.dumps({
        'ok': True,
        'profile': 'applied-ai-evolution',
        'source_pack': 'project-radar',
        'feed_url': args.feed_url,
        'count': len(out[:args.limit]),
        'items': out[:args.limit],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
