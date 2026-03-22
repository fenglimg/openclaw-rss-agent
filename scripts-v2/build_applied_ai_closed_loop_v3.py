#!/usr/bin/env python3
import json
from pathlib import Path

ENRICH_V2 = Path('test-output/applied-ai-enriched-v2.json')
BRIEF = Path('outputs/applied-ai-evolution-brief-v3.md')
ADOPTION = Path('outputs/applied-ai-evolution-adoption-queue-v3.md')
FOLLOW = Path('outputs/applied-ai-evolution-follow-queue-v3.md')
DEEP = Path('outputs/applied-ai-evolution-deep-dive-queue-v3.md')
ANCHOR = Path('outputs/applied-ai-evolution-official-anchor-queue-v3.md')

OFFICIAL_NAMES = {'anthropics/claude-code', 'openai/codex', 'google-gemini/gemini-cli'}


def load_items():
    return json.loads(ENRICH_V2.read_text(encoding='utf-8')).get('items', [])


def practical_category(name, desc=''):
    text = (name + ' ' + desc).lower()
    if any(k in text for k in ['workflow', 'template', 'spec-driven', 'methodology']):
        return 'workflow-framework'
    if any(k in text for k in ['plugin', 'hud', 'statusline']):
        return 'tooling-surface'
    if any(k in text for k in ['orchestrator', 'multi-agent', 'octopus', 'hydra']):
        return 'orchestration'
    if any(k in text for k in ['claude-code', 'codex', 'gemini-cli']):
        return 'official-anchor'
    return 'applied-project'


def retaxonomize(item):
    name = item['name']
    cat = practical_category(name, item.get('description',''))
    score = item['final_score']
    roles = item['source_roles']

    if name in OFFICIAL_NAMES:
        return 'official-anchor', cat, score

    text = (name + ' ' + item.get('description','')).lower()
    if any(k in text for k in ['workflow', 'template', 'plugin', 'orchestrator', 'skills', 'framework']) and roles['promote-source'] >= 1 and score >= 5.0:
        return 'adopt', cat, score + 0.4

    if any(k in text for k in ['inference', 'multimodal', 'model-serving', 'omni-modality']):
        return 'deep-dive', cat, score - 0.2

    if roles['risk/evidence'] > 0 and score < 5.2:
        return 'deep-dive', cat, score - 0.2

    if score >= 4.8:
        return 'follow', cat, score
    return 'deep-dive', cat, score


def why(label, item, cat):
    name = item['name'].lower()
    if label == 'official-anchor':
        return 'Official baseline ecosystem anchor: important to track continuously, but not the same thing as an adoption candidate.'
    if label == 'adopt':
        if 'superpowers' in name:
            return 'Strong practical framework candidate with clear workflow relevance and promoted-source support.'
        if 'trellis' in name:
            return 'Practical workflow framework with ecosystem support and direct relevance to the coding-agent/tooling space.'
        if 'templates' in name:
            return 'Concrete workflow/template layer likely to transfer into practical usage patterns quickly.'
        if 'hud' in name:
            return 'Concrete tooling surface with strong practical utility around Claude Code visibility and agent workflow.'
        return 'Practical applied-AI candidate with enough workflow/tooling relevance and source support to merit adoption consideration.'
    if label == 'follow':
        return 'Worth following, but still weaker than the strongest practical workflow/tooling candidates.'
    return 'Interesting signal, but still too technical, too ambiguous, or too weakly supported for practical adoption right now.'


def render_queue(title, items):
    lines = [title + '\n']
    for i, x in enumerate(items, 1):
        lines.append(f"## {i}. {x['name']}")
        lines.append(f"- Category: `{x['category']}`")
        lines.append(f"- Final score: {x['final_score']}")
        lines.append(f"- Source roles: promote={x['source_roles']['promote-source']}, reference-project={x['source_roles']['reference-project']}, editorial={x['source_roles']['editorial-reference']}, risk={x['source_roles']['risk/evidence']}")
        lines.append(f"- Why: {x['why']}")
        for ref in x.get('filtered_refs', [])[:4]:
            lines.append(f"- Source object: {ref['url']} (`{ref['source_judgment']}` / `{ref['object_type']}`)")
        lines.append('')
    return '\n'.join(lines)


def main():
    items = load_items()
    rows = []
    for item in items:
        label, cat, score = retaxonomize(item)
        rows.append({
            **item,
            'judgment_v3': label,
            'category': cat,
            'final_score': round(score, 2),
            'why': why(label, item, cat),
        })

    adopts = sorted([x for x in rows if x['judgment_v3'] == 'adopt'], key=lambda x: -x['final_score'])
    follows = sorted([x for x in rows if x['judgment_v3'] == 'follow'], key=lambda x: -x['final_score'])
    dives = sorted([x for x in rows if x['judgment_v3'] == 'deep-dive'], key=lambda x: -x['final_score'])
    anchors = sorted([x for x in rows if x['judgment_v3'] == 'official-anchor'], key=lambda x: -x['final_score'])

    brief = ['# Applied AI Evolution Brief v3\n', 'Judgment taxonomy recalibrated: official anchors are now separated from practical adoption candidates.\n']
    brief.append('## Practical adopt candidates\n')
    for x in adopts[:6]:
        brief.append(f"- **{x['name']}** (`{x['category']}` / `{x['kind']}`) — final_score `{x['final_score']}`")
        brief.append(f"  - why: {x['why']}")
    brief.append('\n## Official anchors\n')
    for x in anchors[:6]:
        brief.append(f"- **{x['name']}** — final_score `{x['final_score']}`")
        brief.append(f"  - why: {x['why']}")
    brief.append('\n## Follow\n')
    for x in follows[:6]:
        brief.append(f"- **{x['name']}** — final_score `{x['final_score']}`")
        brief.append(f"  - why: {x['why']}")
    brief.append('\n## Deep-dive\n')
    for x in dives[:6]:
        brief.append(f"- **{x['name']}** — final_score `{x['final_score']}`")
        brief.append(f"  - why: {x['why']}")

    BRIEF.write_text('\n'.join(brief), encoding='utf-8')
    ADOPTION.write_text(render_queue('# Applied AI Evolution Adoption Queue v3', adopts), encoding='utf-8')
    FOLLOW.write_text(render_queue('# Applied AI Evolution Follow Queue v3', follows), encoding='utf-8')
    DEEP.write_text(render_queue('# Applied AI Evolution Deep-Dive Queue v3', dives), encoding='utf-8')
    ANCHOR.write_text(render_queue('# Applied AI Evolution Official Anchor Queue v3', anchors), encoding='utf-8')
    print(json.dumps({'ok': True, 'brief': str(BRIEF), 'adoption': str(ADOPTION), 'follow': str(FOLLOW), 'deep': str(DEEP), 'anchor': str(ANCHOR)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
