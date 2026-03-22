#!/usr/bin/env python3
import json
from pathlib import Path

TREND = Path('test-output/skill-mcp-trend-intelligence-refined.json')
ENRICH = Path('test-output/openclaw-evolution-enriched-v2.json')
PROMOTE = Path('test-output/openclaw-evolution-promote-source-v11.json')
BRIEF = Path('outputs/openclaw-evolution-brief-v13.md')
ADOPTION = Path('outputs/openclaw-evolution-adoption-queue-v13.md')
DEEP = Path('outputs/openclaw-evolution-deep-dive-queue-v13.md')
FOLLOW = Path('outputs/openclaw-evolution-follow-queue-v13.md')

DOMAIN_HINTS = ['polymarket', 'weather', 'baidu', 'obsidian']
REUSABLE_HINTS = ['self-improving', 'proactive', 'summarize', 'github', 'browser', 'search', 'vetter']
VARIANT_HINTS = ['nano ', ' pro', ' + ']


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


def source_role_counts(enriched):
    counts = {'promote-source': 0, 'track-ranking-source': 0, 'risk-signal': 0, 'inspect-skill-spec': 0}
    for x in enriched.get('source_candidate_urls', []):
        j = x.get('source_judgment')
        if j in counts:
            counts[j] += 1
    return counts


def score(item, enriched):
    base = float(item.get('trend_score', 0))
    roles = source_role_counts(enriched)
    s = item['skill'].lower()
    bonus = 0.0
    penalty = 0.0
    bonus += min(roles['promote-source'] * 0.7, 1.4)
    bonus += min(roles['inspect-skill-spec'] * 0.2, 0.4)
    bonus += min(roles['track-ranking-source'] * 0.3, 0.6)
    penalty += min(roles['risk-signal'] * 0.8, 1.6)
    if any(k in s for k in DOMAIN_HINTS):
        penalty += 0.5
    if any(k in s for k in VARIANT_HINTS):
        penalty += 0.35
    return round(base + bonus - penalty, 2), roles


def judgment(skill, final_score, roles):
    s = skill.lower()
    reusable = any(k in s for k in REUSABLE_HINTS)
    domain = any(k in s for k in DOMAIN_HINTS)
    variant = any(k in s for k in VARIANT_HINTS)

    if domain:
        return 'deep-dive'
    if roles['risk-signal'] > 0 and not reusable:
        return 'deep-dive'
    if reusable and final_score >= 5.8 and roles['promote-source'] >= 1:
        return 'adopt'
    if variant and final_score < 6.0:
        return 'follow'
    if final_score >= 5.0:
        return 'follow'
    return 'deep-dive'


def why(skill, judgment_label, roles):
    s = skill.lower()
    if judgment_label == 'adopt':
        if 'self-improving' in s:
            return 'Strong reusable self-improvement pattern, now supported by promoted canonical sources and direct inspection targets.'
        if 'summarize' in s:
            return 'Reusable synthesis capability with promoted ecosystem backing and little risk signal.'
        if 'github' in s:
            return 'Clear code-ops surface with repeated canonical source confirmation.'
        if 'browser' in s:
            return 'Durable action surface with both promoted sources and inspectable implementation objects.'
        return 'Reusable capability with enough promoted-source support to justify adoption.'
    if judgment_label == 'follow':
        return 'Signal is real, but either the reusable lesson is weaker or promoted-source support is not yet strong enough for adoption.'
    if roles['risk-signal'] > 0:
        return 'Risk/evidence signals are present, so this should be inspected before any stronger judgment.'
    return 'Interesting signal, but still too domain-specific or unclear to treat as reusable product direction.'


def main():
    trend_items = load(TREND).get('items', [])
    enrich_map = {x['skill']: x for x in load(ENRICH).get('items', [])}
    promote_rows = load(PROMOTE).get('items', [])
    promote_sources = [x for x in promote_rows if x['source_judgment'] == 'promote-source']

    rows = []
    for item in trend_items:
        enriched = enrich_map.get(item['skill'], {'source_candidate_urls': [], 'source_quality_notes': [], 'validation_sources': []})
        final_score, roles = score(item, enriched)
        row = {
            'skill': item['skill'],
            'owners': item.get('owners', []),
            'category': category(item['skill']),
            'trend_score': item.get('trend_score', 0),
            'final_score': final_score,
            'roles': roles,
            'judgment': judgment(item['skill'], final_score, roles),
            'enriched': enriched,
        }
        row['why'] = why(item['skill'], row['judgment'], roles)
        rows.append(row)

    adopts = sorted([x for x in rows if x['judgment'] == 'adopt'], key=lambda x: -x['final_score'])
    follows = sorted([x for x in rows if x['judgment'] == 'follow'], key=lambda x: -x['final_score'])
    dives = sorted([x for x in rows if x['judgment'] == 'deep-dive'], key=lambda x: -x['final_score'])

    brief = ['# OpenClaw Evolution Brief v1.3\n', 'Final judgment now consumes closed-loop enrichment with explicit source roles.\n']
    brief.append('## Adopt\n')
    for row in adopts[:6]:
        brief.append(f"- **{row['skill']}** (`{row['category']}`) — final_score `{row['final_score']}`")
        brief.append(f"  - roles: promote={row['roles']['promote-source']} risk={row['roles']['risk-signal']} inspect={row['roles']['inspect-skill-spec']} ranking={row['roles']['track-ranking-source']}")
        brief.append(f"  - why: {row['why']}")
    brief.append('\n## Follow\n')
    for row in follows[:6]:
        brief.append(f"- **{row['skill']}** — final_score `{row['final_score']}`")
        brief.append(f"  - roles: promote={row['roles']['promote-source']} risk={row['roles']['risk-signal']} inspect={row['roles']['inspect-skill-spec']} ranking={row['roles']['track-ranking-source']}")
        brief.append(f"  - why: {row['why']}")
    brief.append('\n## Deep-dive\n')
    for row in dives[:6]:
        brief.append(f"- **{row['skill']}** — final_score `{row['final_score']}`")
        brief.append(f"  - roles: promote={row['roles']['promote-source']} risk={row['roles']['risk-signal']} inspect={row['roles']['inspect-skill-spec']} ranking={row['roles']['track-ranking-source']}")
        brief.append(f"  - why: {row['why']}")
    brief.append('\n## Promoted canonical sources\n')
    for rec in promote_sources[:6]:
        brief.append(f"- **{rec['canonical_url']}** — refs `{rec['references']}`")
        brief.append(f"  - why: {rec['why']}")

    def render_queue(title, queue):
        lines = [title + '\n']
        for i, row in enumerate(queue[:12], 1):
            lines.append(f"## {i}. {row['skill']}")
            lines.append(f"- Category: `{row['category']}`")
            lines.append(f"- Final score: {row['final_score']}")
            lines.append(f"- Source roles: promote={row['roles']['promote-source']}, risk={row['roles']['risk-signal']}, inspect={row['roles']['inspect-skill-spec']}, ranking={row['roles']['track-ranking-source']}")
            lines.append(f"- Why: {row['why']}")
            for ref in row['enriched'].get('source_candidate_urls', [])[:4]:
                lines.append(f"- Source object: {ref['url']} (`{ref['source_judgment']}` / `{ref['object_type']}`)")
            lines.append('')
        return '\n'.join(lines)

    BRIEF.write_text('\n'.join(brief), encoding='utf-8')
    ADOPTION.write_text(render_queue('# OpenClaw Evolution Adoption Queue v1.3', adopts), encoding='utf-8')
    FOLLOW.write_text(render_queue('# OpenClaw Evolution Follow Queue v1.3', follows), encoding='utf-8')
    DEEP.write_text(render_queue('# OpenClaw Evolution Deep-Dive Queue v1.3', dives), encoding='utf-8')
    print(json.dumps({'ok': True, 'brief': str(BRIEF), 'adoption': str(ADOPTION), 'follow': str(FOLLOW), 'deep': str(DEEP)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
