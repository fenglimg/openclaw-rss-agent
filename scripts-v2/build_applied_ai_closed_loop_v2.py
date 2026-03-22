#!/usr/bin/env python3
import json
from pathlib import Path

MERGED = Path('test-output/applied-ai-candidates-v1.json')
ENRICH_V1 = Path('test-output/applied-ai-enriched-v1.json')
SOURCE_J = Path('test-output/applied-ai-source-judgment-v1.json')
ENRICH_V2 = Path('test-output/applied-ai-enriched-v2.json')
BRIEF = Path('outputs/applied-ai-evolution-brief-v2.md')
ADOPTION = Path('outputs/applied-ai-evolution-adoption-queue-v2.md')
DEEP = Path('outputs/applied-ai-evolution-deep-dive-queue-v2.md')
FOLLOW = Path('outputs/applied-ai-evolution-follow-queue-v2.md')


def load(p):
    return json.loads(p.read_text(encoding='utf-8'))


def source_map():
    return {x['canonical_url']: x for x in load(SOURCE_J).get('items', [])}


def classify(name, desc=''):
    text = (name + ' ' + desc).lower()
    if any(k in text for k in ['workflow', 'template', 'spec-driven', 'methodology']):
        return 'workflow-framework'
    if any(k in text for k in ['plugin', 'hud', 'statusline']):
        return 'tooling-surface'
    if any(k in text for k in ['orchestrator', 'multi-agent', 'octopus', 'hydra']):
        return 'orchestration'
    if any(k in text for k in ['claude-code', 'codex', 'gemini-cli']) and 'github.com/' in text:
        return 'official-anchor'
    return 'applied-project'


def canonical(url):
    # match the applied source classifier behavior roughly for GitHub repos
    if 'github.com/' in url:
        tail = url.split('github.com/', 1)[1].strip('/')
        parts = tail.split('/')
        if len(parts) == 1:
            return 'https://github.com/' + parts[0]
        if len(parts) >= 2:
            if len(parts) >= 4 and parts[2] == 'issues':
                return 'https://github.com/' + '/'.join(parts[:4])
            return 'https://github.com/' + '/'.join(parts[:2])
    return url.rstrip('/')


def role_counts(refs, smap):
    counts = {'promote-source': 0, 'reference-project': 0, 'editorial-reference': 0, 'risk/evidence': 0}
    filtered = []
    for r in refs:
        cu = canonical(r['url'])
        meta = smap.get(cu)
        if not meta:
            continue
        j = meta['source_judgment']
        if j in counts:
            counts[j] += 1
        if j != 'evidence-only':
            filtered.append({
                'url': cu,
                'source_judgment': j,
                'object_type': meta['object_type'],
                'title': r.get('title','')
            })
    # dedupe filtered
    out, seen = [], set()
    for x in filtered:
        key = (x['url'], x['source_judgment'])
        if key in seen:
            continue
        seen.add(key)
        out.append(x)
    return counts, out


def final_judgment(item, counts):
    text = (item['name'] + ' ' + item.get('description','')).lower()
    score = float(item.get('base_score', 0))
    score += min(counts['promote-source'] * 0.8, 1.6)
    score += min(counts['reference-project'] * 0.4, 0.8)
    score += min(counts['editorial-reference'] * 0.2, 0.4)
    score -= min(counts['risk/evidence'] * 0.8, 1.6)
    score = round(score, 2)

    if any(k in text for k in ['workflow', 'plugin', 'template', 'orchestrator', 'multi-agent']) and counts['promote-source'] >= 1 and score >= 5.0:
        return score, 'adopt'
    if any(k in text for k in ['claude-code', 'codex', 'gemini-cli']) and counts['promote-source'] >= 1 and score >= 4.8:
        return score, 'follow'
    if any(k in text for k in ['inference', 'multimodal', 'model-serving', 'omni-modality']):
        return score, 'deep-dive'
    if counts['risk/evidence'] > 0 and score < 5.0:
        return score, 'deep-dive'
    if score >= 4.6:
        return score, 'follow'
    return score, 'deep-dive'


def why(item, judgment, counts):
    text = (item['name'] + ' ' + item.get('description','')).lower()
    if judgment == 'adopt':
        return 'Practical workflow/tooling candidate with promoted source support and clearer reusable value.'
    if judgment == 'follow':
        if counts['promote-source'] > 0:
            return 'Looks real and ecosystem-backed, but not yet compelling enough as a top adoption candidate.'
        return 'Interesting applied signal, but stronger source support is still needed.'
    if any(k in text for k in ['inference', 'multimodal', 'model']):
        return 'Technically interesting, but lesson for applied workflow adoption is less clear right now.'
    return 'Needs deeper inspection due to weaker source support, domain ambiguity, or less reusable product signal.'


def main():
    merged = {x['url']: x for x in load(MERGED).get('items', [])}
    enrich_v1 = load(ENRICH_V1).get('items', [])
    smap = source_map()
    rows = []
    for item in enrich_v1:
        base = merged.get(item['url'], item)
        counts, filtered = role_counts(item.get('validation_refs', []), smap)
        score, judgment = final_judgment(base, counts)
        rows.append({
            'name': base['name'],
            'url': base['url'],
            'kind': base['kind'],
            'category': classify(base['name'], base.get('description','')),
            'description': base.get('description',''),
            'base_score': base.get('base_score', 0),
            'final_score': score,
            'judgment': judgment,
            'source_roles': counts,
            'filtered_refs': filtered,
            'why': why(base, judgment, counts),
        })

    ENRICH_V2.write_text(json.dumps({'ok': True, 'items': rows}, ensure_ascii=False, indent=2), encoding='utf-8')

    adopts = sorted([x for x in rows if x['judgment'] == 'adopt'], key=lambda x: -x['final_score'])
    follows = sorted([x for x in rows if x['judgment'] == 'follow'], key=lambda x: -x['final_score'])
    dives = sorted([x for x in rows if x['judgment'] == 'deep-dive'], key=lambda x: -x['final_score'])

    brief = ['# Applied AI Evolution Brief v2\n', 'Closed-loop applied output after feeding source judgment back into enrichment and final ranking.\n']
    brief.append('## Adopt\n')
    for x in adopts[:6]:
        brief.append(f"- **{x['name']}** (`{x['category']}` / `{x['kind']}`) — final_score `{x['final_score']}`")
        brief.append(f"  - source roles: promote={x['source_roles']['promote-source']} refproj={x['source_roles']['reference-project']} editorial={x['source_roles']['editorial-reference']} risk={x['source_roles']['risk/evidence']}")
        brief.append(f"  - why: {x['why']}")
    brief.append('\n## Follow\n')
    for x in follows[:6]:
        brief.append(f"- **{x['name']}** — final_score `{x['final_score']}`")
        brief.append(f"  - source roles: promote={x['source_roles']['promote-source']} refproj={x['source_roles']['reference-project']} editorial={x['source_roles']['editorial-reference']} risk={x['source_roles']['risk/evidence']}")
        brief.append(f"  - why: {x['why']}")
    brief.append('\n## Deep-dive\n')
    for x in dives[:6]:
        brief.append(f"- **{x['name']}** — final_score `{x['final_score']}`")
        brief.append(f"  - source roles: promote={x['source_roles']['promote-source']} refproj={x['source_roles']['reference-project']} editorial={x['source_roles']['editorial-reference']} risk={x['source_roles']['risk/evidence']}")
        brief.append(f"  - why: {x['why']}")

    def render(title, queue):
        lines = [title + '\n']
        for i, x in enumerate(queue[:12], 1):
            lines.append(f"## {i}. {x['name']}")
            lines.append(f"- Category: `{x['category']}`")
            lines.append(f"- Kind: `{x['kind']}`")
            lines.append(f"- Final score: {x['final_score']}")
            lines.append(f"- Source roles: promote={x['source_roles']['promote-source']}, reference-project={x['source_roles']['reference-project']}, editorial={x['source_roles']['editorial-reference']}, risk={x['source_roles']['risk/evidence']}")
            lines.append(f"- Why: {x['why']}")
            for ref in x['filtered_refs'][:4]:
                lines.append(f"- Source object: {ref['url']} (`{ref['source_judgment']}` / `{ref['object_type']}`)")
            lines.append('')
        return '\n'.join(lines)

    BRIEF.write_text('\n'.join(brief), encoding='utf-8')
    ADOPTION.write_text(render('# Applied AI Evolution Adoption Queue v2', adopts), encoding='utf-8')
    FOLLOW.write_text(render('# Applied AI Evolution Follow Queue v2', follows), encoding='utf-8')
    DEEP.write_text(render('# Applied AI Evolution Deep-Dive Queue v2', dives), encoding='utf-8')
    print(json.dumps({'ok': True, 'enriched': str(ENRICH_V2), 'brief': str(BRIEF), 'adoption': str(ADOPTION), 'follow': str(FOLLOW), 'deep': str(DEEP), 'count': len(rows)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
