#!/usr/bin/env python3
import json
from pathlib import Path

CAL = Path('test-output/calibration-rule-applications-v1.json')
OUT_BRIEF = Path('outputs/applied-ai-evolution-brief-v5.md')
OUT_ADOPT = Path('outputs/applied-ai-evolution-adoption-queue-v5.md')
OUT_FOLLOW = Path('outputs/applied-ai-evolution-follow-queue-v5.md')
OUT_ANCHOR = Path('outputs/applied-ai-evolution-official-anchor-queue-v5.md')
OUT_DEEP = Path('outputs/applied-ai-evolution-deep-dive-queue-v5.md')

OFFICIAL = ['anthropics/claude-code', 'openai/codex', 'google-gemini/gemini-cli']
BASE_ADOPT = ['obra/superpowers', 'mindfold-ai/Trellis', 'davila7/claude-code-templates']
BASE_FOLLOW = ['gsd-build/get-shit-done']


def load_cal():
    items = json.loads(CAL.read_text(encoding='utf-8')).get('items', [])
    return {x['name']: x for x in items if x['track'] == 'applied-ai-evolution'}


def main():
    cal = load_cal()
    adopt = list(BASE_ADOPT)
    follow = list(BASE_FOLLOW)

    hud = cal.get('jarrodwatts/claude-hud')
    gsd = cal.get('gsd-build/get-shit-done')

    if hud and hud['calibrated_judgment'] == 'adopt' and 'jarrodwatts/claude-hud' not in adopt:
        adopt.append('jarrodwatts/claude-hud')
    if 'jarrodwatts/claude-hud' in follow:
        follow.remove('jarrodwatts/claude-hud')

    brief = ['# Applied AI Evolution Brief v5\n', 'Calibration-native applied output: final practical queues now consume calibration results directly.\n']
    brief.append('## Adopt\n')
    for name in adopt:
        if name == 'jarrodwatts/claude-hud':
            brief.append(f"- **{name}** — upgraded via calibration rule `{hud['applied_rules'][0]}`; direct tooling surface with clear practical utility.")
        else:
            brief.append(f"- **{name}**")
    brief.append('\n## Follow / framework-to-study\n')
    if gsd:
        brief.append(f"- **gsd-build/get-shit-done** — remains `follow` via calibration rule `{gsd['applied_rules'][0]}`; treat as methodology/framework-to-study.")
    brief.append('\n## Official anchors\n')
    for name in OFFICIAL:
        brief.append(f"- **{name}**")

    adopt_md = ['# Applied AI Evolution Adoption Queue v5\n']
    for i, name in enumerate(adopt, start=1):
        adopt_md.append(f"## {i}. {name}")
        if name == 'jarrodwatts/claude-hud':
            adopt_md.append(f"- Calibrated judgment: `{hud['calibrated_judgment']}`")
            adopt_md.append(f"- Applied rule: `{hud['applied_rules'][0]}`")
            adopt_md.append(f"- Why: {hud['why']}")
        else:
            adopt_md.append('- Why: retained as a practical applied adopt candidate.')
        adopt_md.append('')

    follow_md = ['# Applied AI Evolution Follow Queue v5\n']
    if gsd:
        follow_md += [
            '## 1. gsd-build/get-shit-done',
            f"- Calibrated judgment: `{gsd['calibrated_judgment']}`",
            f"- Applied rule: `{gsd['applied_rules'][0]}`",
            f"- Why: {gsd['why']}",
            '- Interpretation: framework-to-study / methodology, not direct adopt-now capability.',
            ''
        ]

    anchor_md = ['# Applied AI Evolution Official Anchor Queue v5\n']
    for i, name in enumerate(OFFICIAL, start=1):
        anchor_md += [f"## {i}. {name}", '- Why: official baseline product tracked separately from practical adopt candidates.', '']

    deep_md = ['# Applied AI Evolution Deep-Dive Queue v5\n', '- No new calibrated deep-dive additions in this pass.\n']

    OUT_BRIEF.write_text('\n'.join(brief), encoding='utf-8')
    OUT_ADOPT.write_text('\n'.join(adopt_md), encoding='utf-8')
    OUT_FOLLOW.write_text('\n'.join(follow_md), encoding='utf-8')
    OUT_ANCHOR.write_text('\n'.join(anchor_md), encoding='utf-8')
    OUT_DEEP.write_text('\n'.join(deep_md), encoding='utf-8')
    print(json.dumps({'ok': True, 'adopt_count': len(adopt)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
