#!/usr/bin/env python3
import json
from pathlib import Path

INPUT = Path('test-output/skill-mcp-trend-intelligence-refined.json')
BRIEF = Path('outputs/openclaw-evolution-brief.md')
ADOPTION = Path('outputs/openclaw-evolution-adoption-queue.md')
DEEPDIVE = Path('outputs/openclaw-evolution-deep-dive-queue.md')


def load_items():
    data = json.loads(INPUT.read_text(encoding='utf-8'))
    return data.get('items', [])


def classify(item):
    skill = item.get('skill', '').lower()
    owners = ' '.join(item.get('owners', [])).lower()
    text = f"{skill} {owners}"
    if any(k in text for k in ['search', 'tavily', 'github', 'browser', 'summarize']):
        return 'tooling-surface'
    if any(k in text for k in ['self-improving', 'proactive', 'vetter']):
        return 'agent-behavior'
    if any(k in text for k in ['weather', 'polymarket', 'baidu']):
        return 'domain-skill'
    return 'general-utility'


def should_adopt(item):
    skill = item.get('skill', '').lower()
    if any(k in skill for k in ['self-improving', 'proactive', 'skill vetter', 'summarize', 'github', 'search', 'browser']):
        return True
    return item.get('cross_source', False)


def should_deepdive(item):
    skill = item.get('skill', '').lower()
    if any(k in skill for k in ['polymarket', 'ontology', 'baidu']):
        return True
    return item.get('trend_score', 0) >= 2.8 and not should_adopt(item)


def fmt_rising(item):
    r = item.get('rising') or {}
    if not r:
        return '—'
    return f"rising #{r.get('rank')} · Δ {r.get('delta')} · {r.get('pct_change')} · downloads {r.get('downloads')}"


def fmt_top(item):
    t = item.get('top_base') or {}
    if not t:
        return '—'
    return f"top-base #{t.get('rank')} · downloads {t.get('downloads')} · stars {t.get('stars')} · installs/day {t.get('installs_per_day')}"


def build_brief(items):
    top = items[:10]
    lines = []
    lines.append('# OpenClaw Evolution Brief\n')
    lines.append('First output-layer draft from `skill-mcp-ecosystem` refined trend intelligence.\n')
    lines.append('## What looks strongest right now\n')
    for item in top:
        lines.append(f"- **{item['skill']}** (`{classify(item)}`)")
        lines.append(f"  - owners: {', '.join(item.get('owners', [])) or 'unknown'}")
        lines.append(f"  - sources: {', '.join(item.get('sources', []))}")
        lines.append(f"  - signal: {fmt_rising(item)}")
        if item.get('top_base'):
            lines.append(f"  - base: {fmt_top(item)}")
        lines.append(f"  - why it matters: {why_it_matters(item)}")
    lines.append('\n## Current interpretation\n')
    lines.append('- The ecosystem is showing strong demand for agent self-improvement, proactive execution, search, summarization, browser interaction, and GitHub/tooling surfaces.')
    lines.append('- The most interesting adoption candidates are not random domain skills but reusable agent behavior patterns and tooling surfaces that OpenClaw could absorb.')
    lines.append('- Cross-source overlap is currently the strongest heuristic for “likely durable signal,” while high rising-only movement is useful for early detection.')
    return '\n'.join(lines) + '\n'


def why_it_matters(item):
    skill = item.get('skill', '').lower()
    if 'self-improving' in skill:
        return 'Direct signal that the ecosystem values explicit self-correction, memory capture, and iterative agent improvement loops.'
    if 'proactive' in skill:
        return 'Strong signal for autonomous follow-through and task continuation behavior.'
    if 'vetter' in skill:
        return 'Signals demand for trust/safety filtering in a large skill ecosystem.'
    if 'summarize' in skill:
        return 'Summarization remains a core reusable primitive across many agent workflows.'
    if 'browser' in skill:
        return 'Browser skills remain a durable action surface for practical task execution.'
    if 'github' in skill or 'search' in skill:
        return 'Search/GitHub integration are core ecosystem primitives for useful agents.'
    return 'Useful as a signal of recurring ecosystem demand or unexplained adoption momentum.'


def build_adoption(items):
    picks = [x for x in items if should_adopt(x)][:12]
    lines = ['# OpenClaw Evolution Adoption Queue\n', 'Candidates that look worth absorbing, copying, or explicitly studying for product/skill evolution.\n']
    for i, item in enumerate(picks, 1):
        lines.append(f"## {i}. {item['skill']}")
        lines.append(f"- Category: `{classify(item)}`")
        lines.append(f"- Owners: {', '.join(item.get('owners', [])) or 'unknown'}")
        lines.append(f"- Sources: {', '.join(item.get('sources', []))}")
        lines.append(f"- Signal: {fmt_rising(item)}")
        if item.get('top_base'):
            lines.append(f"- Base: {fmt_top(item)}")
        lines.append(f"- Why consider adoption: {why_it_matters(item)}")
        lines.append(f"- Suggested next step: {next_step(item)}")
        lines.append('')
    return '\n'.join(lines)


def next_step(item):
    skill = item.get('skill', '').lower()
    if 'self-improving' in skill:
        return 'Read the skill spec and compare against existing OpenClaw memory/self-correction patterns.'
    if 'vetter' in skill:
        return 'Study how ecosystem trust/risk checks are exposed to users before installation or execution.'
    if 'search' in skill:
        return 'Compare against current search-layer and identify missing user-facing affordances.'
    if 'github' in skill:
        return 'Check whether current GitHub skill coverage already matches the observed demand surface.'
    if 'browser' in skill:
        return 'Compare browser skill behavior with current OpenClaw browser and action surfaces.'
    if 'summarize' in skill:
        return 'Check if summary workflows should become a more explicit built-in output primitive.'
    if 'proactive' in skill:
        return 'Study what proactive behavior users actually want versus what should remain permission-gated.'
    return 'Inspect the source skill page and determine whether the demand is reusable or domain-specific.'


def build_deepdive(items):
    picks = [x for x in items if should_deepdive(x)][:12]
    lines = ['# OpenClaw Evolution Deep-Dive Queue\n', 'Signals worth researching further before deciding whether to adopt, ignore, or reframe.\n']
    for i, item in enumerate(picks, 1):
        lines.append(f"## {i}. {item['skill']}")
        lines.append(f"- Category: `{classify(item)}`")
        lines.append(f"- Owners: {', '.join(item.get('owners', [])) or 'unknown'}")
        lines.append(f"- Sources: {', '.join(item.get('sources', []))}")
        lines.append(f"- Signal: {fmt_rising(item)}")
        if item.get('top_base'):
            lines.append(f"- Base: {fmt_top(item)}")
        lines.append(f"- Why deep-dive: {deepdive_reason(item)}")
        lines.append('')
    return '\n'.join(lines)


def deepdive_reason(item):
    skill = item.get('skill', '').lower()
    if 'polymarket' in skill:
        return 'High momentum, but unclear whether the demand is durable for OpenClaw versus narrow market-specific novelty.'
    if 'ontology' in skill:
        return 'Interesting adoption signal but unclear user job-to-be-done from ranking data alone.'
    if 'baidu' in skill:
        return 'May indicate regional search demand worth understanding, especially for Chinese-language usage patterns.'
    return 'Shows meaningful movement, but the reusable product lesson is not yet obvious from ranking data alone.'


def main():
    items = load_items()
    BRIEF.write_text(build_brief(items), encoding='utf-8')
    ADOPTION.write_text(build_adoption(items), encoding='utf-8')
    DEEPDIVE.write_text(build_deepdive(items), encoding='utf-8')
    print(json.dumps({
        'ok': True,
        'inputs': str(INPUT),
        'outputs': [str(BRIEF), str(ADOPTION), str(DEEPDIVE)],
        'count': len(items),
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
