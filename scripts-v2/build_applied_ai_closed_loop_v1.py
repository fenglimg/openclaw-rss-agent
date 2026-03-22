#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

RADAR = Path('test-output/project-radar-sample-v12.json')
WATCH = Path('test-output/applied-ai-ecosystem-watchlist.json')
MERGED = Path('test-output/applied-ai-candidates-v1.json')
ENRICHED = Path('test-output/applied-ai-enriched-v1.json')
BRIEF = Path('outputs/applied-ai-evolution-brief-v1.md')
ADOPTION = Path('outputs/applied-ai-evolution-adoption-queue-v1.md')
DEEP = Path('outputs/applied-ai-evolution-deep-dive-queue-v1.md')

HIGH_VALUE_HINTS = ['claude-code', 'codex', 'gemini-cli', 'workflow', 'plugin', 'template', 'orchestration', 'multi-agent', 'skills']


def load(p):
    return json.loads(p.read_text(encoding='utf-8'))


def merge_candidates():
    radar = load(RADAR).get('items', [])
    watch = load(WATCH).get('items', [])
    merged = []
    for x in radar:
        merged.append({
            'name': x['repo'],
            'url': x['url'],
            'kind': 'project-radar',
            'base_score': x.get('score', 0),
            'description': x.get('description', ''),
            'topics': x.get('topics', []),
        })
    for x in watch[:10]:
        merged.append({
            'name': x['repo'],
            'url': x['url'],
            'kind': 'applied-watchlist',
            'base_score': x.get('watch_score', 0),
            'description': x.get('description', ''),
            'topics': x.get('topics', []),
            'role': x.get('role', ''),
        })
    # de-dupe by url
    out, seen = [], set()
    for x in merged:
        if x['url'] in seen:
            continue
        seen.add(x['url'])
        out.append(x)
    MERGED.write_text(json.dumps({'ok': True, 'items': out}, ensure_ascii=False, indent=2), encoding='utf-8')
    return out


def run_search(query):
    cmd = [
        'python3', '/root/.openclaw/skills/search-layer/scripts/search.py',
        '--queries', query,
        '--mode', 'deep',
        '--intent', 'exploratory',
        '--num', '4'
    ]
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)


def select(items):
    picked = []
    for x in sorted(items, key=lambda i: i['base_score'], reverse=True):
        text = (x['name'] + ' ' + x.get('description', '') + ' ' + ' '.join(x.get('topics', []))).lower()
        if any(k in text for k in HIGH_VALUE_HINTS):
            picked.append(x)
        if len(picked) >= 8:
            break
    return picked


def classify(name, desc=''):
    text = (name + ' ' + desc).lower()
    if any(k in text for k in ['workflow', 'template', 'spec-driven', 'methodology']):
        return 'workflow-framework'
    if any(k in text for k in ['plugin', 'hud', 'statusline']):
        return 'tooling-surface'
    if any(k in text for k in ['orchestrator', 'multi-agent', 'octopus', 'hydra']):
        return 'orchestration'
    if any(k in text for k in ['official', 'gemini-cli', 'claude-code', 'codex']):
        return 'official-anchor'
    return 'applied-project'


def enrich(items):
    enriched = []
    for x in items:
        q = f"{x['name']} Claude Code Codex Gemini CLI GitHub workflow"
        res = run_search(q).get('results', [])
        refs = []
        for r in res[:4]:
            refs.append({'title': r.get('title',''), 'url': r.get('url',''), 'source': r.get('source','')})
        urls = ' '.join(r['url'] for r in refs)
        quality = []
        if 'github.com' in urls:
            quality.append('Has GitHub-confirmed ecosystem references.')
        if any('docs' in r['url'] or 'official' in r['title'].lower() for r in refs):
            quality.append('Has documentation/official-reference style support.')
        if not quality:
            quality.append('Mostly soft references so far.')
        suggested = 'follow'
        text = (x['name'] + ' ' + x.get('description','')).lower()
        if any(k in text for k in ['workflow', 'plugin', 'template', 'orchestrator', 'skills']) and 'github.com' in urls:
            suggested = 'adopt-or-follow'
        if any(k in text for k in ['inference', 'multimodal', 'model']) and x['kind'] == 'project-radar':
            suggested = 'deep-dive'
        enriched.append({
            **x,
            'category': classify(x['name'], x.get('description','')),
            'validation_refs': refs,
            'quality_notes': quality,
            'suggested_judgment': suggested,
        })
    ENRICHED.write_text(json.dumps({'ok': True, 'items': enriched}, ensure_ascii=False, indent=2), encoding='utf-8')
    return enriched


def build_outputs(items):
    adopt = [x for x in items if x['suggested_judgment'] == 'adopt-or-follow']
    deep = [x for x in items if x['suggested_judgment'] == 'deep-dive']
    follow = [x for x in items if x['suggested_judgment'] == 'follow']

    brief = ['# Applied AI Evolution Brief v1\n', 'First closed-loop draft combining `project-radar` and `applied-ai-ecosystem` with search-layer enrichment.\n']
    brief.append('## Strongest practical signals\n')
    for x in adopt[:6]:
        brief.append(f"- **{x['name']}** (`{x['category']}` / `{x['kind']}`)")
        brief.append(f"  - why: {' '.join(x['quality_notes'])}")
        for r in x['validation_refs'][:2]:
            brief.append(f"  - ref: {r['title']} — {r['url']}")
    brief.append('\n## Follow\n')
    for x in follow[:6]:
        brief.append(f"- **{x['name']}** (`{x['category']}`)")
        brief.append(f"  - why: {' '.join(x['quality_notes'])}")
    brief.append('\n## Deep-dive\n')
    for x in deep[:6]:
        brief.append(f"- **{x['name']}** (`{x['category']}`)")
        brief.append(f"  - why: {' '.join(x['quality_notes'])}")

    ad = ['# Applied AI Evolution Adoption Queue v1\n']
    for i, x in enumerate(adopt[:10], 1):
        ad.append(f"## {i}. {x['name']}")
        ad.append(f"- Category: `{x['category']}`")
        ad.append(f"- Kind: `{x['kind']}`")
        ad.append(f"- Why: {' '.join(x['quality_notes'])}")
        for r in x['validation_refs'][:3]:
            ad.append(f"- Validation ref: {r['title']} — {r['url']}")
        ad.append('')

    dd = ['# Applied AI Evolution Deep-Dive Queue v1\n']
    for i, x in enumerate(deep[:10], 1):
        dd.append(f"## {i}. {x['name']}")
        dd.append(f"- Category: `{x['category']}`")
        dd.append(f"- Kind: `{x['kind']}`")
        dd.append(f"- Why: {' '.join(x['quality_notes'])}")
        for r in x['validation_refs'][:3]:
            dd.append(f"- Validation ref: {r['title']} — {r['url']}")
        dd.append('')

    BRIEF.write_text('\n'.join(brief), encoding='utf-8')
    ADOPTION.write_text('\n'.join(ad), encoding='utf-8')
    DEEP.write_text('\n'.join(dd), encoding='utf-8')


def main():
    items = merge_candidates()
    picked = select(items)
    enriched = enrich(picked)
    build_outputs(enriched)
    print(json.dumps({'ok': True, 'merged': str(MERGED), 'enriched': str(ENRICHED), 'brief': str(BRIEF), 'adoption': str(ADOPTION), 'deep': str(DEEP), 'count': len(enriched)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
