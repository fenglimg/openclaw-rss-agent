#!/usr/bin/env python3
import json
from pathlib import Path

TREND = Path('test-output/skill-mcp-trend-intelligence-refined.json')
ENRICH = Path('test-output/openclaw-evolution-enriched.json')
BRIEF = Path('outputs/openclaw-evolution-brief-v11.md')
ADOPTION = Path('outputs/openclaw-evolution-adoption-queue-v11.md')
DEEPDIVE = Path('outputs/openclaw-evolution-deep-dive-queue-v11.md')


def load_json(p):
    return json.loads(p.read_text(encoding='utf-8'))


def classify(skill):
    s = skill.lower()
    if any(k in s for k in ['self-improving', 'proactive', 'vetter']):
        return 'agent-behavior'
    if any(k in s for k in ['search', 'github', 'browser', 'summarize']):
        return 'tooling-surface'
    if any(k in s for k in ['weather', 'polymarket', 'baidu']):
        return 'domain-skill'
    return 'general-utility'


def quality_bonus(enriched):
    refs = len(enriched.get('validation_sources', []))
    notes = enriched.get('source_quality_notes', [])
    bonus = min(refs * 0.2, 0.8)
    if any('Cross-domain ecosystem confirmation' in n for n in notes):
        bonus += 0.5
    if any('high-trust ecosystem reference' in n for n in notes):
        bonus += 0.4
    return round(bonus, 2)


def risk_penalty(skill, enriched):
    text = ' '.join(x.get('url', '') + ' ' + x.get('title', '') for x in enriched.get('validation_sources', []))
    penalty = 0.0
    if 'suspect' in text.lower() or 'deleted' in text.lower():
        penalty += 0.8
    if classify(skill) == 'domain-skill':
        penalty += 0.5
    return round(penalty, 2)


def judgment(skill, enriched, final_score):
    s = skill.lower()
    if any(k in s for k in ['self-improving', 'proactive', 'summarize', 'github', 'browser']):
        return 'adopt'
    if 'search' in s and final_score >= 5.5:
        return 'adopt'
    if final_score >= 5.0 and classify(skill) != 'domain-skill':
        return 'follow'
    if classify(skill) == 'domain-skill':
        return 'deep-dive'
    return 'follow'


def main():
    trend_items = load_json(TREND).get('items', [])
    enrich_items = {x['skill']: x for x in load_json(ENRICH).get('items', [])}

    scored = []
    for item in trend_items:
        skill = item['skill']
        enriched = enrich_items.get(skill, {})
        base = float(item.get('trend_score', 0))
        bonus = quality_bonus(enriched) if enriched else 0.0
        penalty = risk_penalty(skill, enriched) if enriched else 0.0
        final_score = round(base + bonus - penalty, 2)
        scored.append({
            'skill': skill,
            'owners': item.get('owners', []),
            'category': classify(skill),
            'trend_score': base,
            'quality_bonus': bonus,
            'risk_penalty': penalty,
            'final_score': final_score,
            'judgment': judgment(skill, enriched, final_score),
            'enriched': enriched,
            'trend': item,
        })

    scored.sort(key=lambda x: (x['judgment'] != 'adopt', -x['final_score'], x['skill'].lower()))

    brief_lines = ['# OpenClaw Evolution Brief v1.1\n', 'Judgment-aware output after feeding enrichment and source quality back into ranking.\n']
    brief_lines.append('## Most credible adoption signals\n')
    for row in [x for x in scored if x['judgment'] == 'adopt'][:5]:
        brief_lines.append(f"- **{row['skill']}** (`{row['category']}`) — final_score `{row['final_score']}`")
        brief_lines.append(f"  - base trend: {row['trend_score']} | quality bonus: +{row['quality_bonus']} | risk penalty: -{row['risk_penalty']}")
        brief_lines.append(f"  - why now: {why(row)}")
    brief_lines.append('\n## Follow but do not over-interpret yet\n')
    for row in [x for x in scored if x['judgment'] == 'follow'][:5]:
        brief_lines.append(f"- **{row['skill']}** — final_score `{row['final_score']}`")
        brief_lines.append(f"  - why follow: {why(row)}")
    brief_lines.append('\n## Deep-dive / caution signals\n')
    for row in [x for x in scored if x['judgment'] == 'deep-dive'][:5]:
        brief_lines.append(f"- **{row['skill']}** — final_score `{row['final_score']}`")
        brief_lines.append(f"  - why caution: {why(row)}")

    adoption_lines = ['# OpenClaw Evolution Adoption Queue v1.1\n']
    for i, row in enumerate([x for x in scored if x['judgment'] == 'adopt'][:10], 1):
        adoption_lines.append(f"## {i}. {row['skill']}")
        adoption_lines.append(f"- Category: `{row['category']}`")
        adoption_lines.append(f"- Final score: {row['final_score']} (trend {row['trend_score']} + quality {row['quality_bonus']} - risk {row['risk_penalty']})")
        adoption_lines.append(f"- Reason: {why(row)}")
        for ref in row['enriched'].get('validation_sources', [])[:3]:
            adoption_lines.append(f"- Validation ref: {ref['title']} — {ref['url']}")
        adoption_lines.append('')

    deep_lines = ['# OpenClaw Evolution Deep-Dive Queue v1.1\n']
    for i, row in enumerate([x for x in scored if x['judgment'] == 'deep-dive'][:10], 1):
        deep_lines.append(f"## {i}. {row['skill']}")
        deep_lines.append(f"- Category: `{row['category']}`")
        deep_lines.append(f"- Final score: {row['final_score']} (trend {row['trend_score']} + quality {row['quality_bonus']} - risk {row['risk_penalty']})")
        deep_lines.append(f"- Reason: {why(row)}")
        for ref in row['enriched'].get('validation_sources', [])[:3]:
            deep_lines.append(f"- Validation ref: {ref['title']} — {ref['url']}")
        deep_lines.append('')

    BRIEF.write_text('\n'.join(brief_lines), encoding='utf-8')
    ADOPTION.write_text('\n'.join(adoption_lines), encoding='utf-8')
    DEEPDIVE.write_text('\n'.join(deep_lines), encoding='utf-8')
    print(json.dumps({'ok': True, 'brief': str(BRIEF), 'adoption': str(ADOPTION), 'deepdive': str(DEEPDIVE)}, ensure_ascii=False, indent=2))


def why(row):
    skill = row['skill'].lower()
    if 'self-improving' in skill:
        return 'Strongest combined signal for self-correction / memory / iterative improvement, validated by multiple ecosystem references.'
    if 'proactive' in skill:
        return 'Strong reusable behavior signal around autonomous follow-through rather than domain novelty.'
    if 'summarize' in skill:
        return 'Reusable synthesis primitive with both popularity and ecosystem confirmation.'
    if 'github' in skill:
        return 'GitHub remains a core integration surface and the signal is both hot and ecosystem-confirmed.'
    if 'browser' in skill:
        return 'Browser action remains a durable agent surface, now validated beyond rank-only evidence.'
    if 'search' in skill:
        return 'Search remains a reusable surface, but adoption should still depend on overlap with current search-layer capability.'
    if classify(row['skill']) == 'domain-skill':
        return 'High movement exists, but the lesson may be domain-specific or mixed with trust/risk signals.'
    return 'Signal is real, but product lesson is still less clear than the top adoption candidates.'


if __name__ == '__main__':
    main()
