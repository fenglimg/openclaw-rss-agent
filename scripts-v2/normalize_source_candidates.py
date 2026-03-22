#!/usr/bin/env python3
import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

INPUT = Path('test-output/openclaw-evolution-source-candidates.json')
JSON_OUT = Path('test-output/openclaw-evolution-source-candidates-normalized.json')
MD_OUT = Path('outputs/openclaw-evolution-source-candidate-queue-normalized.md')


def load_items():
    return json.loads(INPUT.read_text(encoding='utf-8')).get('items', [])


def normalize(url):
    p = urlparse(url)
    host = p.netloc.lower()
    path = p.path.rstrip('/')

    if 'github.com' in host:
        parts = [x for x in path.split('/') if x]
        if len(parts) >= 2:
            repo_root = f'https://github.com/{parts[0]}/{parts[1]}'
            if len(parts) >= 4 and parts[2] == 'issues':
                return {
                    'canonical_url': url,
                    'object_type': 'github-issue',
                    'parent_url': repo_root,
                }
            if len(parts) >= 5 and parts[2] == 'blob':
                file_path = '/'.join(parts[4:])
                if file_path.lower().endswith('skill.md'):
                    return {
                        'canonical_url': url,
                        'object_type': 'github-skill-spec',
                        'parent_url': repo_root,
                    }
                return {
                    'canonical_url': repo_root,
                    'object_type': 'github-repo',
                    'parent_url': None,
                }
            return {
                'canonical_url': repo_root,
                'object_type': 'github-repo',
                'parent_url': None,
            }

    if 'clawhub.ai' in host:
        parts = [x for x in path.split('/') if x]
        if len(parts) >= 2:
            return {
                'canonical_url': f'https://clawhub.ai/{parts[0]}/{parts[1]}',
                'object_type': 'clawhub-skill-page',
                'parent_url': None,
            }
    if 'playbooks.com' in host:
        return {'canonical_url': url.rstrip('/'), 'object_type': 'weekly-intelligence-page', 'parent_url': None}
    if 'topclawhubskills.com' in host:
        return {'canonical_url': 'https://topclawhubskills.com/', 'object_type': 'trend-ranking-page', 'parent_url': None}
    if 'clawhubtrends.com' in host:
        return {'canonical_url': url.rstrip('/'), 'object_type': 'trend-ranking-page', 'parent_url': None}
    return {'canonical_url': url.rstrip('/'), 'object_type': 'other', 'parent_url': None}


def priority(obj_type, refs):
    if obj_type == 'github-repo' and refs >= 2:
        return 'P0'
    if obj_type in {'trend-ranking-page', 'weekly-intelligence-page'}:
        return 'P1'
    if obj_type in {'github-issue', 'github-skill-spec', 'clawhub-skill-page'}:
        return 'P2'
    return 'P2'


def main():
    items = load_items()
    grouped = defaultdict(lambda: {'canonical_url': None, 'object_type': None, 'parent_url': None, 'raw_urls': set(), 'skills': set(), 'references': 0})
    for item in items:
        norm = normalize(item['url'])
        g = grouped[norm['canonical_url']]
        g['canonical_url'] = norm['canonical_url']
        g['object_type'] = norm['object_type']
        g['parent_url'] = norm['parent_url']
        g['raw_urls'].add(item['url'])
        for s in item.get('skills', []):
            g['skills'].add(s)
        g['references'] += item.get('references', 1)

    records = []
    for g in grouped.values():
        rec = {
            'canonical_url': g['canonical_url'],
            'object_type': g['object_type'],
            'parent_url': g['parent_url'],
            'raw_urls': sorted(g['raw_urls']),
            'skills': sorted(g['skills']),
            'references': g['references'],
        }
        rec['priority'] = priority(rec['object_type'], rec['references'])
        records.append(rec)

    rank = {'P0': 0, 'P1': 1, 'P2': 2}
    records.sort(key=lambda x: (rank[x['priority']], -x['references'], x['canonical_url']))

    JSON_OUT.write_text(json.dumps({'ok': True, 'items': records}, ensure_ascii=False, indent=2), encoding='utf-8')

    lines = ['# OpenClaw Evolution Source Candidate Queue (Normalized)\n', 'Canonicalized source objects after collapsing repo/readme/blob relationships.\n']
    cur = None
    for rec in records:
        if rec['priority'] != cur:
            cur = rec['priority']
            lines.append(f'## {cur}\n')
        lines.append(f"### {rec['canonical_url']}")
        lines.append(f"- Object type: `{rec['object_type']}`")
        if rec['parent_url']:
            lines.append(f"- Parent: {rec['parent_url']}")
        lines.append(f"- References: {rec['references']}")
        lines.append(f"- Surfaced from skills: {', '.join(rec['skills'])}")
        if len(rec['raw_urls']) > 1:
            lines.append(f"- Collapsed raw URLs:")
            for u in rec['raw_urls'][:6]:
                lines.append(f"  - {u}")
        lines.append('')

    MD_OUT.write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'ok': True, 'count': len(records), 'json': str(JSON_OUT), 'md': str(MD_OUT)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
