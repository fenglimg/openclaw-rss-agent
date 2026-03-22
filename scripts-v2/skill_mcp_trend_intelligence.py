#!/usr/bin/env python3
import argparse
import json
import re
from collections import defaultdict
from urllib.request import Request, urlopen

SOURCES = [
    {"url": "https://clawhub.ai/ademczuk/skills-weekly", "role": "weekly", "name": "skills-weekly"},
    {"url": "https://playbooks.com/skills/openclaw/skills/last30days-weekly", "role": "weekly", "name": "last30days-weekly"},
    {"url": "https://clawhubtrends.com/rising.html", "role": "rising", "name": "clawhubtrends-rising"},
    {"url": "https://topclawhubskills.com/", "role": "top-base", "name": "topclawhubskills"},
    {"url": "https://openclaw-hub.org/openclaw-hub-top-skills.html", "role": "top-base", "name": "openclaw-hub-top-skills"},
]

STOP = {
    'openclaw', 'skills', 'skill', 'weekly', 'rising', 'top', 'home', 'login', 'tools', 'advertise',
    'dashboard', 'leaderboard', 'updated', 'live data', 'every', 'security', 'this', 'absolute delta',
    'most popular clawhub skills', 'openclaw hub top skills', 'top clawhub skills', 'clawhub trends',
    'openclaw skills weekly', 'last30days-weekly', 'home mcp skills advertise', 'top skills getting started'
}

OWNER_SKILL_PAT = re.compile(r'([a-z0-9_-]+)/([a-z0-9._-]{3,})', re.I)
TITLE_PAT = re.compile(r'\b([A-Z][A-Za-z0-9+._-]{2,}(?:\s+[A-Z][A-Za-z0-9+._-]{2,}){0,3})\b')


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


def clean_name(name):
    s = re.sub(r'\s+', ' ', name).strip(' -–—|:,.')
    return s


def candidate_records(raw):
    out = []
    for owner, skill in OWNER_SKILL_PAT.findall(raw):
        owner = clean_name(owner)
        skill = clean_name(skill)
        if owner.lower() in STOP or skill.lower() in STOP:
            continue
        if len(skill) < 3:
            continue
        out.append({'owner': owner, 'skill': skill, 'kind': 'owner/skill'})

    for title in TITLE_PAT.findall(raw):
        title = clean_name(title)
        low = title.lower()
        if low in STOP:
            continue
        if len(title) < 4:
            continue
        if any(x in low for x in ['http', 'github', 'openclaw hub', 'clawhub', 'weekly', 'rising', 'top clawhub']):
            continue
        out.append({'owner': None, 'skill': title, 'kind': 'title'})
    return out


def normalize(skill):
    s = skill.lower().strip()
    s = re.sub(r'[^a-z0-9+._ -]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--per-source-limit', type=int, default=8)
    args = ap.parse_args()

    grouped = defaultdict(lambda: {
        'skill': None,
        'owners': set(),
        'roles': set(),
        'sources': set(),
        'mentions': 0,
    })
    source_samples = []

    for src in SOURCES:
        try:
            html = fetch(src['url'])
            raw = strip_html(html)
            records = candidate_records(raw)
            kept = []
            seen = set()
            for rec in records:
                norm = normalize(rec['skill'])
                if not norm or norm in seen or norm in STOP:
                    continue
                seen.add(norm)
                kept.append(rec)
                g = grouped[norm]
                g['skill'] = rec['skill']
                if rec['owner']:
                    g['owners'].add(rec['owner'])
                g['roles'].add(src['role'])
                g['sources'].add(src['name'])
                g['mentions'] += 1
                if len(kept) >= args.per_source_limit:
                    break
            source_samples.append({
                'name': src['name'],
                'role': src['role'],
                'url': src['url'],
                'parsed_candidates': kept,
                'count': len(kept),
            })
        except Exception as e:
            source_samples.append({
                'name': src['name'],
                'role': src['role'],
                'url': src['url'],
                'error': str(e),
                'parsed_candidates': [],
                'count': 0,
            })

    items = []
    for norm, g in grouped.items():
        score = 0.0
        if 'rising' in g['roles']:
            score += 1.5
        if 'top-base' in g['roles']:
            score += 1.2
        if 'weekly' in g['roles']:
            score += 0.8
        score += min(g['mentions'] * 0.5, 2.0)
        items.append({
            'skill': g['skill'],
            'owners': sorted(g['owners']),
            'roles': sorted(g['roles']),
            'sources': sorted(g['sources']),
            'mentions': g['mentions'],
            'trend_score': round(score, 2),
            'profile': 'openclaw-evolution',
            'source_pack': 'skill-mcp-ecosystem',
        })

    items.sort(key=lambda x: (x['trend_score'], x['mentions'], x['skill'].lower()), reverse=True)

    print(json.dumps({
        'ok': True,
        'profile': 'openclaw-evolution',
        'source_pack': 'skill-mcp-ecosystem',
        'kind': 'trend-intelligence',
        'source_samples': source_samples,
        'items': items[:40],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
