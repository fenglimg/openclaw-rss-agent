#!/usr/bin/env python3
import argparse
import json
import re
from urllib.request import Request, urlopen

SOURCES = [
    {"url": "https://clawhub.ai/ademczuk/skills-weekly", "role": "trend-source", "name": "skills-weekly"},
    {"url": "https://playbooks.com/skills/openclaw/skills/last30days-weekly", "role": "trend-source", "name": "last30days-weekly"},
    {"url": "https://clawhubtrends.com/rising.html", "role": "rising-source", "name": "clawhubtrends-rising"},
    {"url": "https://topclawhubskills.com/", "role": "top-base-source", "name": "topclawhubskills"},
    {"url": "https://openclaw-hub.org/openclaw-hub-top-skills.html", "role": "top-base-source", "name": "openclaw-hub-top-skills"},
]

SKILL_PATTERNS = [
    re.compile(r'/skills?/([a-zA-Z0-9._-]+)'),
    re.compile(r'@([a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+)'),
    re.compile(r'([A-Z][A-Za-z0-9+._-]{2,}(?:\s+[A-Z][A-Za-z0-9+._-]{2,}){0,3})'),
]


def fetch(url):
    req = Request(url, headers={'User-Agent': 'openclaw-rss-agent/2.0'})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode('utf-8', errors='ignore')


def strip_html(text):
    text = re.sub(r'<script[\s\S]*?</script>', ' ', text, flags=re.I)
    text = re.sub(r'<style[\s\S]*?</style>', ' ', text, flags=re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def extract_candidates(html):
    raw = strip_html(html)
    found = []
    for pat in SKILL_PATTERNS:
        for m in pat.findall(raw):
            if isinstance(m, tuple):
                m = m[0]
            s = m.strip()
            if len(s) < 3:
                continue
            if s.lower() in {'openclaw', 'skills', 'weekly', 'github', 'readme', 'stars'}:
                continue
            found.append(s)
    # preserve order, lightly dedupe
    out = []
    seen = set()
    for x in found:
        key = x.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(x)
    return out[:20]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=5)
    args = ap.parse_args()

    items = []
    for src in SOURCES:
        try:
            html = fetch(src['url'])
            candidates = extract_candidates(html)[: args.limit]
            items.append({
                'name': src['name'],
                'url': src['url'],
                'role': src['role'],
                'candidates': candidates,
                'count': len(candidates),
            })
        except Exception as e:
            items.append({
                'name': src['name'],
                'url': src['url'],
                'role': src['role'],
                'error': str(e),
                'candidates': [],
                'count': 0,
            })

    print(json.dumps({
        'ok': True,
        'profile': 'openclaw-evolution',
        'source_pack': 'skill-mcp-ecosystem',
        'kind': 'trend-sources-snapshot',
        'items': items,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
