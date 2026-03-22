#!/usr/bin/env python3
import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

INPUT = Path('test-output/applied-ai-enriched-v1.json')
NORM_JSON = Path('test-output/applied-ai-source-candidates-normalized-v1.json')
JUDGE_JSON = Path('test-output/applied-ai-source-judgment-v1.json')
MD_OUT = Path('outputs/applied-ai-source-queue-v1.md')


def load_items():
    return json.loads(INPUT.read_text(encoding='utf-8')).get('items', [])


def classify(url):
    p = urlparse(url)
    host = p.netloc.lower()
    path = p.path.rstrip('/')
    if 'github.com' in host:
        parts = [x for x in path.split('/') if x]
        if len(parts) == 1:
            return url, 'github-user-or-org', None
        if len(parts) >= 2:
            repo = f'https://github.com/{parts[0]}/{parts[1]}'
            if len(parts) >= 5 and parts[2] == 'blob':
                if parts[-1].lower().endswith('.md'):
                    return repo, 'github-repo', None
            if len(parts) >= 4 and parts[2] == 'issues':
                return url, 'github-issue', repo
            return repo, 'github-repo', None
    if 'medium.com' in host or 'substack.com' in host:
        return url.rstrip('/'), 'editorial-reference', None
    if 'docs.' in host or '/docs' in path.lower() or 'developers.openai.com' in host or 'docs.trytrellis.app' in host:
        return url.rstrip('/'), 'official-docs', None
    if 'opencode.ai' in host or 'termo.ai' in host:
        return url.rstrip('/'), 'official-site', None
    return url.rstrip('/'), 'other', None


def judge(obj_type, refs, skills):
    joined = ' '.join(skills).lower()
    if obj_type == 'github-repo' and refs >= 2:
        if any(k in joined for k in ['claude-code', 'codex', 'gemini-cli', 'superpowers', 'trellis', 'workflow', 'templates']):
            return 'promote-source'
        return 'reference-project'
    if obj_type == 'official-docs' or obj_type == 'official-site':
        return 'editorial-reference'
    if obj_type == 'github-user-or-org':
        return 'reference-project'
    if obj_type == 'editorial-reference':
        return 'editorial-reference'
    if obj_type == 'github-issue':
        return 'risk/evidence'
    return 'evidence-only'


def why(j, obj_type, skills):
    s = ', '.join(skills[:3])
    if j == 'promote-source':
        return f'Canonical repo repeatedly supports practical applied-AI candidates ({s}) and looks worth long-term tracking.'
    if j == 'reference-project':
        return f'Useful reference project/user/org for ecosystem orientation, but not yet a primary recurring source ({s}).'
    if j == 'editorial-reference':
        return f'Useful docs/site/editorial surface for interpretation, examples, or workflow learning ({s}).'
    if j == 'risk/evidence':
        return f'Issue/evidence object useful for context, not as a recurring source ({s}).'
    return f'Supporting evidence surfaced during applied enrichment ({s}).'


def main():
    items = load_items()
    grouped = defaultdict(lambda: {'canonical_url': None, 'object_type': None, 'parent_url': None, 'raw_urls': set(), 'skills': set(), 'references': 0})
    for item in items:
        for ref in item.get('validation_refs', []):
            raw = ref['url']
            canon, obj_type, parent = classify(raw)
            g = grouped[canon]
            g['canonical_url'] = canon
            g['object_type'] = obj_type
            g['parent_url'] = parent
            g['raw_urls'].add(raw)
            g['skills'].add(item['name'])
            g['references'] += 1
    norm_rows = []
    for g in grouped.values():
        norm_rows.append({
            'canonical_url': g['canonical_url'],
            'object_type': g['object_type'],
            'parent_url': g['parent_url'],
            'raw_urls': sorted(g['raw_urls']),
            'skills': sorted(g['skills']),
            'references': g['references'],
        })
    NORM_JSON.write_text(json.dumps({'ok': True, 'items': norm_rows}, ensure_ascii=False, indent=2), encoding='utf-8')

    judged = []
    for row in norm_rows:
        j = judge(row['object_type'], row['references'], row['skills'])
        judged.append({
            **row,
            'source_judgment': j,
            'why': why(j, row['object_type'], row['skills'])
        })
    order = {'promote-source': 0, 'reference-project': 1, 'editorial-reference': 2, 'risk/evidence': 3, 'evidence-only': 4}
    judged.sort(key=lambda x: (order[x['source_judgment']], -x['references'], x['canonical_url']))
    JUDGE_JSON.write_text(json.dumps({'ok': True, 'items': judged}, ensure_ascii=False, indent=2), encoding='utf-8')

    lines = ['# Applied AI Evolution Source Queue v1\n', 'First source normalization + source judgment pass for applied-ai-evolution.\n']
    cur = None
    for row in judged:
        if row['source_judgment'] != cur:
            cur = row['source_judgment']
            lines.append(f'## {cur}\n')
        lines.append(f"### {row['canonical_url']}")
        lines.append(f"- Object type: `{row['object_type']}`")
        if row['parent_url']:
            lines.append(f"- Parent: {row['parent_url']}")
        lines.append(f"- References: {row['references']}")
        lines.append(f"- Surfaced from items: {', '.join(row['skills'])}")
        lines.append(f"- Why: {row['why']}")
        lines.append('')
    MD_OUT.write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'ok': True, 'normalized': str(NORM_JSON), 'judged': str(JUDGE_JSON), 'md': str(MD_OUT), 'count': len(judged)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
