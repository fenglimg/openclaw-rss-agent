#!/usr/bin/env python3
import json
from pathlib import Path

CAL = Path('test-output/targeted-calibration-v1.json')
APPLIED_BRIEF = Path('outputs/applied-ai-evolution-brief-v4.md')
APPLIED_ADOPT = Path('outputs/applied-ai-evolution-adoption-queue-v4.md')
APPLIED_FOLLOW = Path('outputs/applied-ai-evolution-follow-queue-v4.md')
OPEN_BRIEF = Path('outputs/openclaw-evolution-brief-v14.md')
OPEN_ADOPT = Path('outputs/openclaw-evolution-adoption-queue-v14.md')
OPEN_FOLLOW = Path('outputs/openclaw-evolution-follow-queue-v14.md')
OPEN_DEEP = Path('outputs/openclaw-evolution-deep-dive-queue-v14.md')


def load_cal():
    return {x['name']: x for x in json.loads(CAL.read_text(encoding='utf-8')).get('items', [])}


def main():
    cal = load_cal()

    applied_brief = ['# Applied AI Evolution Brief v4\n', 'Output updated with targeted calibration results for borderline applied candidates.\n']
    applied_brief.append('## Practical adopt candidates\n')
    applied_brief.append('- **obra/superpowers** — remains a top practical framework candidate.')
    applied_brief.append('- **mindfold-ai/Trellis** — remains a strong workflow framework candidate.')
    applied_brief.append('- **davila7/claude-code-templates** — remains a concrete template/workflow adopt candidate.')
    applied_brief.append('- **jarrodwatts/claude-hud** — upgraded after targeted calibration: repeated ecosystem references, adjacent author projects, and clear tooling utility.\n')
    applied_brief.append('## Follow / framework-to-study\n')
    applied_brief.append('- **gsd-build/get-shit-done** — keep `follow`, but now explicitly treated as a methodology/framework-to-study rather than a direct adopt-now capability.')
    applied_brief.append('- **Official anchors** stay tracked separately: `anthropics/claude-code`, `openai/codex`, `google-gemini/gemini-cli`.')

    applied_adopt = ['# Applied AI Evolution Adoption Queue v4\n']
    applied_adopt += [
        '## 1. obra/superpowers',
        '- Why: Strong practical framework candidate with clear workflow relevance and promoted-source support.',
        '',
        '## 2. mindfold-ai/Trellis',
        '- Why: Practical workflow framework with ecosystem support and direct relevance to the coding-agent/tooling space.',
        '',
        '## 3. davila7/claude-code-templates',
        '- Why: Concrete workflow/template layer likely to transfer into practical usage patterns quickly.',
        '',
        '## 4. jarrodwatts/claude-hud',
        f"- Why: {cal['jarrodwatts/claude-hud']['analysis']['reason']}",
        '- Calibration result: upgraded from `follow` toward `adopt`.',
        ''
    ]

    applied_follow = ['# Applied AI Evolution Follow Queue v4\n']
    applied_follow += [
        '## 1. gsd-build/get-shit-done',
        f"- Why: {cal['gsd-build/get-shit-done']['analysis']['reason']}",
        '- Classification note: methodology / framework-to-study, not a direct product capability adopt-now target.',
        '',
        '## 2. Official anchors',
        '- `anthropics/claude-code`',
        '- `openai/codex`',
        '- `google-gemini/gemini-cli`',
        '- Note: tracked continuously, but not mixed into practical adoption candidates.',
        ''
    ]

    open_brief = ['# OpenClaw Evolution Brief v14\n', 'Output updated with targeted calibration results for borderline OpenClaw candidates.\n']
    open_brief.append('## Adopt / adopt-candidate\n')
    open_brief.append('- **Agent Browser** — remains a strong adopt signal.')
    open_brief.append('- **Summarize** — remains a strong adopt signal.')
    open_brief.append('- **Github** — remains a strong adopt signal.')
    open_brief.append('- **self-improving-agent** — remains adopt, but with known risk signal.')
    open_brief.append(f"- **Proactive Agent** — upgraded toward adopt-candidate: {cal['Proactive Agent']['analysis']['reason']}\n")
    open_brief.append('## Follow with clarified rationale\n')
    open_brief.append(f"- **Gog** — keep `follow`: {cal['Gog']['analysis']['reason']}")

    open_adopt = ['# OpenClaw Evolution Adoption Queue v14\n']
    open_adopt += [
        '## 1. Agent Browser',
        '- Why: Durable action surface with both promoted sources and inspectable implementation objects.',
        '',
        '## 2. Summarize',
        '- Why: Reusable synthesis capability with promoted ecosystem backing and little risk signal.',
        '',
        '## 3. Github',
        '- Why: Clear code-ops surface with repeated canonical source confirmation.',
        '',
        '## 4. self-improving-agent',
        '- Why: Strong reusable self-improvement pattern with promoted canonical sources and direct inspection targets.',
        '',
        '## 5. Proactive Agent',
        f"- Why: {cal['Proactive Agent']['analysis']['reason']}",
        '- Calibration result: upgraded from `follow` toward `adopt-candidate`.',
        ''
    ]

    open_follow = ['# OpenClaw Evolution Follow Queue v14\n']
    open_follow += [
        '## 1. Gog',
        f"- Why: {cal['Gog']['analysis']['reason']}",
        '- Clarified interpretation: support is strong, but the reusable product lesson is still less clear than browser/search/summarize surfaces.',
        '',
        '## 2. Other follow items',
        '- Keep remaining lower-confidence follow items behind the calibrated top boundary cases.',
        ''
    ]

    open_deep = ['# OpenClaw Evolution Deep-Dive Queue v14\n']
    open_deep += [
        '## 1. Polymarket',
        '- Why: risk/evidence signals remain present; reusable lesson still unclear.',
        '',
        '## 2. Weather',
        '- Why: domain-specific movement without a strong reusable product lesson yet.',
        ''
    ]

    APPLIED_BRIEF.write_text('\n'.join(applied_brief), encoding='utf-8')
    APPLIED_ADOPT.write_text('\n'.join(applied_adopt), encoding='utf-8')
    APPLIED_FOLLOW.write_text('\n'.join(applied_follow), encoding='utf-8')
    OPEN_BRIEF.write_text('\n'.join(open_brief), encoding='utf-8')
    OPEN_ADOPT.write_text('\n'.join(open_adopt), encoding='utf-8')
    OPEN_FOLLOW.write_text('\n'.join(open_follow), encoding='utf-8')
    OPEN_DEEP.write_text('\n'.join(open_deep), encoding='utf-8')
    print(json.dumps({'ok': True}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
