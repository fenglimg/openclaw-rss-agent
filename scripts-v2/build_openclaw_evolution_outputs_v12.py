#!/usr/bin/env python3
import json
from pathlib import Path

TREND = Path('test-output/skill-mcp-trend-intelligence-refined.json')
ENRICH = Path('test-output/openclaw-evolution-enriched.json')
SOURCES = Path('test-output/openclaw-evolution-source-candidates.json')
BRIEF = Path('outputs/openclaw-evolution-brief-v12.md')
ADOPTION = Path('outputs/openclaw-evolution-adoption-queue-v12.md')
DEEPDIVE = Path('outputs/openclaw-evolution-deep-dive-queue-v12.md')
PROMOTE = Path('outputs/openclaw-evolution-promote-source-queue.md')

ADOPT_KEYWORDS = ['self-improving', 'proactive', 'summarize', 'github', 'browser', 'search', 'vetter']
VARIANT_HINTS = ['nano ', ' pro', ' + ', 'agent browser']
DOMAIN_HINTS = ['polymarket', 'weather', 'baidu', 'obsidian']


def load(p):
    return json.loads(p.read_text(encoding='utf-8'))


def category(skill):
    s = skill.lower()
    if any(k in s for k in ['self-improving', 'proactive', 'vetter']):
        return 'agent-behavior'
    if any(k in s for k in ['search', 'github', 'browser', 'summarize']):
        return 'tooling-surface'
    if any(k in s for k in DOMAIN_HINTS):
        return 'domain-skill'
    return 'general-utility'


def quality_bonus(enriched):
    refs = len(enriched.get('validation_sources', []))
    notes = enriched.get('source_quality_notes', [])
    b = min(refs * 0.2, 0.8)
    if any('Cross-domain ecosystem confirmation' in n for n in notes):
        b += 0.5
    if any('high-trust ecosystem reference' in n for n in notes):
        b += 0.4
    return round(b, 2)


def risk_penalty(skill, enriched):
    text = ' '.join((x.get('title', '') + ' ' + x.get('url', '')) for x in enriched.get('validation_sources', []))
    s = skill.lower()
    p = 0.0
    if 'suspect' in text.lower() or 'deleted' in text.lower():
        p += 0.8
    if any(k in s for k in DOMAIN_HINTS):
        p += 0.5
    if any(k in s for k in VARIANT_HINTS):
        p += 0.35
    return round(p, 2)


def is_variant(skill):
    s = skill.lower()
    return any(k in s for k in VARIANT_HINTS)


def is_reusable_pattern(skill):
    s = skill.lower()
    return any(k in s for k in ADOPT_KEYWORDS)


def judgment(row):
    s = row['skill'].lower()
    if row['category'] == 'domain-skill':
        return 'deep-dive'
    if is_variant(row['skill']) and row['final_score'] < 6.0:
        return 'follow'
    if is_reusable_pattern(row['skill']) and row['final_score'] >= 5.2 and row['quality_bonus'] >= 0.8:
        return 'adopt'
    if row['final_score'] >= 5.0:
        return 'follow'
    return 'deep-dive'


def rationale(row):
    s = row['skill'].lower()
    if judgment(row) == 'adopt':
        if 'self-improving' in s:
            return 'Reusable self-correction / memory pattern with strong validation, despite some risk hints.'
        if 'proactive' in s:
            return 'Reusable proactive execution behavior with clear product-level relevance.'
        if 'summarize' in s:
            return 'Reusable synthesis primitive with strong ecosystem validation.'
        if 'github' in s:
            return 'Core code-ops integration surface backed by multiple trusted ecosystem references.'
        if 'browser' in s:
            return 'Durable action surface that appears product-relevant beyond pure popularity.'
        if 'search' in s:
            return 'Reusable information-retrieval surface worth explicit product comparison.'
        return 'Reusable pattern with adequate validation and low enough risk.'
    if judgment(row) == 'follow':
        return 'Real signal, but not yet strong enough or clear enough for adoption.'
    return 'Worth deeper inspection due to domain specificity, risk hints, or unclear reusable lesson.'


def main():
    trend_items = load(TREND).get('items', [])
    enrich_items = {x['skill']: x for x in load(ENRICH).get('items', [])}
    source_items = load(SOURCES).get('items', [])

    rows = []
    for item in trend_items:
        skill = item['skill']
        enriched = enrich_items.get(skill, {})
        base = float(item.get('trend_score', 0))
        q = quality_bonus(enriched) if enriched else 0.0
        r = risk_penalty(skill, enriched) if enriched else 0.0
        final = round(base + q - r, 2)
        row = {
            'skill': skill,
            'owners': item.get('owners', []),
            'category': category(skill),
            'trend_score': base,
            'quality_bonus': q,
            'risk_penalty': r,
            'final_score': final,
            'enriched': enriched,
        }
        row['judgment'] = judgment(row)
        row['rationale'] = rationale(row)
        rows.append(row)

    adopts = [x for x in rows if x['judgment'] == 'adopt']
    follows = [x for x in rows if x['judgment'] == 'follow']
    dives = [x for x in rows if x['judgment'] == 'deep-dive']
    adopts.sort(key=lambda x: -x['final_score'])
    follows.sort(key=lambda x: -x['final_score'])
    dives.sort(key=lambda x: -x['final_score'])

    promote = [x for x in source_items if x['priority'] == 'P0']

    brief = ['# OpenClaw Evolution Brief v1.2\n', 'Judgment tightened: adoption now favors reusable patterns with stronger validation and clearer product relevance.\n']
    brief.append('## Adopt now\n')
    for row in adopts[:6]:
        brief.append(f"- **{row['skill']}** (`{row['category']}`) — final_score `{row['final_score']}`")
        brief.append(f"  - why: {row['rationale']}")
    brief.append('\n## Follow\n')
    for row in follows[:6]:
        brief.append(f"- **{row['skill']}** — final_score `{row['final_score']}`")
        brief.append(f"  - why: {row['rationale']}")
    brief.append('\n## Deep-dive\n')
    for row in dives[:6]:
        brief.append(f"- **{row['skill']}** — final_score `{row['final_score']}`")
        brief.append(f"  - why: {row['rationale']}")
    brief.append('\n## Promote-source\n')
    for rec in promote[:6]:
        brief.append(f"- **{rec['url']}** (`{rec['kind']}`) — refs `{rec['references']}`")
        brief.append(f"  - why: {rec['reason']}")

    adoption = ['# OpenClaw Evolution Adoption Queue v1.2\n']
    for i, row in enumerate(adopts[:10], 1):
        adoption.append(f"## {i}. {row['skill']}")
        adoption.append(f"- Category: `{row['category']}`")
        adoption.append(f"- Final score: {row['final_score']} (trend {row['trend_score']} + quality {row['quality_bonus']} - risk {row['risk_penalty']})")
        adoption.append(f"- Why adopt: {row['rationale']}")
        for ref in row['enriched'].get('validation_sources', [])[:3]:
            adoption.append(f"- Validation ref: {ref['title']} — {ref['url']}")
        adoption.append('')

    deep = ['# OpenClaw Evolution Deep-Dive Queue v1.2\n']
    for i, row in enumerate(dives[:10], 1):
        deep.append(f"## {i}. {row['skill']}")
        deep.append(f"- Category: `{row['category']}`")
        deep.append(f"- Final score: {row['final_score']} (trend {row['trend_score']} + quality {row['quality_bonus']} - risk {row['risk_penalty']})")
        deep.append(f"- Why deep-dive: {row['rationale']}")
        for ref in row['enriched'].get('validation_sources', [])[:3]:
            deep.append(f"- Validation ref: {ref['title']} — {ref['url']}")
        deep.append('')

    promote_lines = ['# OpenClaw Evolution Promote-Source Queue\n', 'Source judgment track separated from content judgment.\n']
    for i, rec in enumerate(promote[:12], 1):
        promote_lines.append(f"## {i}. {rec['url']}")
        promote_lines.append(f"- Kind: `{rec['kind']}`")
        promote_lines.append(f"- References: {rec['references']}")
        promote_lines.append(f"- Why promote: {rec['reason']}")
        promote_lines.append('')

    BRIEF.write_text('\n'.join(brief), encoding='utf-8')
    ADOPTION.write_text('\n'.join(adoption), encoding='utf-8')
    DEEPDIVE.write_text('\n'.join(deep), encoding='utf-8')
    PROMOTE.write_text('\n'.join(promote_lines), encoding='utf-8')
    print(json.dumps({'ok': True, 'brief': str(BRIEF), 'adoption': str(ADOPTION), 'deep': str(DEEPDIVE), 'promote': str(PROMOTE)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
