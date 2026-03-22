#!/usr/bin/env python3
import json
import re
from html import unescape
from urllib.request import Request, urlopen

UA = {'User-Agent': 'openclaw-rss-agent/2.0'}


def fetch(url):
    req = Request(url, headers=UA)
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode('utf-8', errors='ignore')


def clean(text):
    text = unescape(text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_rising(html):
    out = []
    tbody = re.search(r'<tbody>([\s\S]*?)</tbody>', html, re.I)
    if not tbody:
        return out
    rows = re.findall(r'<tr[^>]*data-delta="([^"]+)"[^>]*data-pct="([^"]+)"[^>]*>([\s\S]*?)</tr>', tbody.group(1), re.I)
    for delta_attr, pct_attr, row in rows[:30]:
        tds = re.findall(r'<td[^>]*>([\s\S]*?)</td>', row, re.I)
        if len(tds) < 8:
            continue
        rank = clean(tds[0])
        skill_m = re.search(r'<a[^>]*href="([^"]*skills/[^"]+)"[^>]*>([^<]+)</a>', tds[1], re.I)
        owner_m = re.search(r'<a[^>]*href="([^"]*owners/[^"]+)"[^>]*>([^<]+)</a>', tds[2], re.I)
        if not skill_m or not owner_m:
            continue
        out.append({
            'rank': int(rank) if rank.isdigit() else None,
            'skill': clean(skill_m.group(2)),
            'skill_url': skill_m.group(1),
            'owner': clean(owner_m.group(2)).lstrip('@'),
            'owner_url': owner_m.group(1),
            'delta': clean(tds[3]).replace('+', ''),
            'pct_change': clean(tds[4]).replace('+', ''),
            'downloads': clean(tds[5]),
            'downloads_per_day': clean(tds[6]),
            'velocity': clean(tds[7]),
            'age': clean(tds[8]) if len(tds) > 8 else '',
            'source': 'clawhubtrends-rising',
            'role': 'rising',
        })
    return out


def parse_topclawhubskills(html):
    out = []
    rows = re.findall(r'<tr[^>]*data-search="([^"]+)"[^>]*>([\s\S]*?)</tr>', html, re.I)
    for _search, row in rows[:30]:
        tds = re.findall(r'<td[^>]*>([\s\S]*?)</td>', row, re.I)
        if len(tds) < 7:
            continue
        rank = clean(tds[0])
        skill_m = re.search(r'<a[^>]*href="([^"]*clawhub\.ai/skills/[^"]+)"[^>]*class="skill-name"[^>]*>([^<]+)</a>', tds[1], re.I)
        owner_m = re.search(r'<a[^>]*href="([^"]*github\.com/[^"]+)"[^>]*>@?([^<]+)</a>', tds[2], re.I)
        summary_m = re.search(r'<div[^>]*class="skill-summary"[^>]*>([\s\S]*?)</div>', tds[1], re.I)
        badge_m = re.search(r'<span[^>]*class="badge[^"]*"[^>]*>([^<]+)</span>', tds[-1], re.I)
        if not skill_m or not owner_m:
            continue
        out.append({
            'rank': int(rank) if rank.isdigit() else None,
            'skill': clean(skill_m.group(2)),
            'skill_url': skill_m.group(1),
            'owner': clean(owner_m.group(2)).lstrip('@'),
            'owner_url': owner_m.group(1),
            'downloads': clean(tds[3]),
            'stars': clean(tds[4]),
            'installs_per_day': clean(tds[5]),
            'age': clean(tds[6]),
            'safety': clean(badge_m.group(1)) if badge_m else '',
            'summary': clean(summary_m.group(1)) if summary_m else '',
            'source': 'topclawhubskills',
            'role': 'top-base',
        })
    return out


def merge_items(*groups):
    merged = {}
    for items in groups:
        for item in items:
            key = item['skill'].lower().strip()
            cur = merged.setdefault(key, {
                'skill': item['skill'],
                'owners': set(),
                'sources': set(),
                'roles': set(),
                'best_rank': None,
                'rising': None,
                'top_base': None,
            })
            if item.get('owner'):
                cur['owners'].add(item['owner'])
            cur['sources'].add(item['source'])
            cur['roles'].add(item['role'])
            rank = item.get('rank')
            if isinstance(rank, int):
                cur['best_rank'] = rank if cur['best_rank'] is None else min(cur['best_rank'], rank)
            if item['role'] == 'rising':
                cur['rising'] = {
                    'rank': item.get('rank'),
                    'delta': item.get('delta'),
                    'pct_change': item.get('pct_change'),
                    'downloads': item.get('downloads'),
                    'downloads_per_day': item.get('downloads_per_day'),
                    'velocity': item.get('velocity'),
                    'age': item.get('age'),
                    'owner': item.get('owner'),
                    'skill_url': item.get('skill_url'),
                }
            if item['role'] == 'top-base':
                cur['top_base'] = {
                    'rank': item.get('rank'),
                    'downloads': item.get('downloads'),
                    'stars': item.get('stars'),
                    'installs_per_day': item.get('installs_per_day'),
                    'age': item.get('age'),
                    'owner': item.get('owner'),
                    'safety': item.get('safety'),
                    'summary': item.get('summary'),
                    'skill_url': item.get('skill_url'),
                }
    out = []
    for cur in merged.values():
        score = 0
        if cur['rising']:
            score += 2.0
        if cur['top_base']:
            score += 1.6
        if len(cur['sources']) > 1:
            score += 1.0
        if cur['best_rank']:
            score += max(0, (31 - min(cur['best_rank'], 30))) / 30
        out.append({
            'skill': cur['skill'],
            'owners': sorted(cur['owners']),
            'sources': sorted(cur['sources']),
            'roles': sorted(cur['roles']),
            'best_rank': cur['best_rank'],
            'cross_source': len(cur['sources']) > 1,
            'trend_score': round(score, 2),
            'rising': cur['rising'],
            'top_base': cur['top_base'],
            'profile': 'openclaw-evolution',
            'source_pack': 'skill-mcp-ecosystem',
        })
    out.sort(key=lambda x: (x['trend_score'], -(x['best_rank'] or 999), x['skill'].lower()), reverse=True)
    return out


def main():
    rising_html = fetch('https://clawhubtrends.com/rising.html')
    top_html = fetch('https://topclawhubskills.com/')
    rising = parse_rising(rising_html)
    top = parse_topclawhubskills(top_html)
    merged = merge_items(rising, top)
    print(json.dumps({
        'ok': True,
        'profile': 'openclaw-evolution',
        'source_pack': 'skill-mcp-ecosystem',
        'kind': 'refined-trend-intelligence',
        'sources': {
            'clawhubtrends-rising': {'count': len(rising), 'items': rising[:15]},
            'topclawhubskills': {'count': len(top), 'items': top[:15]},
        },
        'items': merged[:30],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
