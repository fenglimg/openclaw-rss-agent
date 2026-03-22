#!/usr/bin/env python3
import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

INPUT = Path('test-output/openclaw-evolution-enriched.json')
OUTPUT = Path('outputs/openclaw-evolution-source-candidate-queue.md')
JSON_OUT = Path('test-output/openclaw-evolution-source-candidates.json')


def load_items():
    data = json.loads(INPUT.read_text(encoding='utf-8'))
    return data.get('items', [])


def classify_url(url):
    host = urlparse(url).netloc.lower()
    path = urlparse(url).path.lower()
    if 'github.com' in host:
        if '/issues/' in path:
            return 'issue-reference'
        if '/blob/' in path and 'skill.md' in path:
            return 'skill-spec'
        return 'github-repo-or-page'
    if 'clawhub.ai' in host:
        return 'clawhub-skill-page'
    if 'playbooks.com' in host:
        return 'weekly-intelligence-page'
    if 'topclawhubskills.com' in host:
        return 'trend-ranking-page'
    if 'clawhubtrends.com' in host:
        return 'trend-ranking-page'
    return 'other'


def priority(entry):
    kind = entry['kind']
    refs = entry['references']
    if kind in {'github-repo-or-page', 'skill-spec', 'clawhub-skill-page'} and refs >= 2:
        return 'P0'
    if kind in {'weekly-intelligence-page', 'trend-ranking-page', 'issue-reference'}:
        return 'P1'
    return 'P2'


def reason(kind, skills):
    s = ', '.join(skills[:3])
    if kind == 'github-repo-or-page':
        return f'Repeatedly surfaced as a supporting ecosystem reference for high-signal skills ({s}).'
    if kind == 'skill-spec':
        return f'Direct skill specification page useful for close capability inspection ({s}).'
    if kind == 'clawhub-skill-page':
        return f'Direct ClawHub skill page repeatedly surfaced during enrichment ({s}).'
    if kind == 'issue-reference':
        return f'Issue/discussion surfaced as contextual validation or risk signal ({s}).'
    if kind == 'weekly-intelligence-page':
        return f'Looks like a weekly intelligence/reference surface related to tracked skills ({s}).'
    if kind == 'trend-ranking-page':
        return f'Looks like a ranking/trend source useful for continued ecosystem monitoring ({s}).'
    return f'Additional source surfaced during enrichment ({s}).'


def main():
    items = load_items()
    grouped = defaultdict(lambda: {'url': None, 'skills': set(), 'references': 0, 'kind': None})
    for item in items:
        for url in item.get('source_candidate_urls', []):
            g = grouped[url]
            g['url'] = url
            g['skills'].add(item['skill'])
            g['references'] += 1
            g['kind'] = classify_url(url)

    records = []
    for g in grouped.values():
        rec = {
            'url': g['url'],
            'kind': g['kind'],
            'skills': sorted(g['skills']),
            'references': g['references'],
        }
        rec['priority'] = priority(rec)
        rec['reason'] = reason(rec['kind'], rec['skills'])
        records.append(rec)

    rank = {'P0': 0, 'P1': 1, 'P2': 2}
    records.sort(key=lambda x: (rank[x['priority']], -x['references'], x['url']))

    JSON_OUT.write_text(json.dumps({'ok': True, 'items': records}, ensure_ascii=False, indent=2), encoding='utf-8')

    lines = ['# OpenClaw Evolution Source Candidate Queue\n', 'Sources surfaced during candidate enrichment that may be worth tracking, promoting, or studying further.\n']
    cur = None
    for rec in records:
        if rec['priority'] != cur:
            cur = rec['priority']
            lines.append(f'## {cur}\n')
        lines.append(f"### {rec['url']}")
        lines.append(f"- Kind: `{rec['kind']}`")
        lines.append(f"- References: {rec['references']}")
        lines.append(f"- Surfaced from skills: {', '.join(rec['skills'])}")
        lines.append(f"- Why it matters: {rec['reason']}")
        lines.append('')

    OUTPUT.write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'ok': True, 'count': len(records), 'output': str(OUTPUT), 'json': str(JSON_OUT)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
