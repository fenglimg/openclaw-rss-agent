#!/usr/bin/env python3
import json
from pathlib import Path

INPUT = Path('test-output/openclaw-evolution-source-candidates-normalized.json')
OUT_MD = Path('outputs/openclaw-evolution-promote-source-queue-v11.md')
OUT_JSON = Path('test-output/openclaw-evolution-promote-source-v11.json')


def load_items():
    return json.loads(INPUT.read_text(encoding='utf-8')).get('items', [])


def judgment(item):
    t = item['object_type']
    refs = item['references']
    url = item['canonical_url']
    if t == 'github-repo' and refs >= 2:
        return 'promote-source'
    if t == 'trend-ranking-page':
        return 'track-ranking-source'
    if t == 'weekly-intelligence-page':
        return 'track-weekly-source'
    if t == 'github-issue':
        if 'issues/87' in url or 'issues/630' in url:
            return 'risk-signal'
        return 'evidence-only'
    if t == 'github-skill-spec' or t == 'clawhub-skill-page':
        return 'inspect-skill-spec'
    if t == 'github-org':
        return 'promote-source'
    return 'evidence-only'


def why(item, j):
    t = item['object_type']
    skills = ', '.join(item.get('skills', [])[:3])
    if j == 'promote-source':
        return f'Canonical source repeatedly surfaced across high-signal skills ({skills}) and is suitable for longer-term tracking.'
    if j == 'track-ranking-source':
        return f'Useful ranking/trend source for ongoing ecosystem movement tracking ({skills}).'
    if j == 'track-weekly-source':
        return f'Useful weekly intelligence source for recurring ecosystem interpretation ({skills}).'
    if j == 'risk-signal':
        return f'Issue/discussion object better treated as risk/evidence than as a promoted recurring source ({skills}).'
    if j == 'inspect-skill-spec':
        return f'Useful for close inspection of capability shape, but not a source to promote as a recurring intelligence feed ({skills}).'
    return f'Supporting evidence object, but not strong enough as a standalone promoted source ({skills}).'


def score(item, j):
    refs = item['references']
    base = min(refs * 0.5, 3.0)
    if j == 'promote-source':
        base += 2.0
    elif j == 'track-ranking-source':
        base += 1.5
    elif j == 'track-weekly-source':
        base += 1.5
    elif j == 'risk-signal':
        base += 0.8
    elif j == 'inspect-skill-spec':
        base += 0.6
    return round(base, 2)


def main():
    items = load_items()
    rows = []
    for item in items:
        j = judgment(item)
        rows.append({
            **item,
            'source_judgment': j,
            'source_score': score(item, j),
            'why': why(item, j),
        })

    order = {'promote-source': 0, 'track-ranking-source': 1, 'track-weekly-source': 2, 'risk-signal': 3, 'inspect-skill-spec': 4, 'evidence-only': 5}
    rows.sort(key=lambda x: (order[x['source_judgment']], -x['source_score'], -x['references'], x['canonical_url']))

    OUT_JSON.write_text(json.dumps({'ok': True, 'items': rows}, ensure_ascii=False, indent=2), encoding='utf-8')

    lines = ['# OpenClaw Evolution Promote-Source Queue v1.1\n', 'Source judgment after normalization. Separate recurring sources from evidence, risk, and inspection objects.\n']
    cur = None
    for row in rows:
        if row['source_judgment'] != cur:
            cur = row['source_judgment']
            lines.append(f'## {cur}\n')
        lines.append(f"### {row['canonical_url']}")
        lines.append(f"- Object type: `{row['object_type']}`")
        if row.get('parent_url'):
            lines.append(f"- Parent: {row['parent_url']}")
        lines.append(f"- References: {row['references']}")
        lines.append(f"- Source score: {row['source_score']}")
        lines.append(f"- Surfaced from skills: {', '.join(row.get('skills', []))}")
        lines.append(f"- Why: {row['why']}")
        lines.append('')

    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'ok': True, 'count': len(rows), 'md': str(OUT_MD), 'json': str(OUT_JSON)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
