#!/usr/bin/env python3
import json
from pathlib import Path

CAL = Path('test-output/calibration-rule-applications-v1.json')
OUT_BRIEF = Path('outputs/openclaw-evolution-brief-v15.md')
OUT_ADOPT = Path('outputs/openclaw-evolution-adoption-queue-v15.md')
OUT_FOLLOW = Path('outputs/openclaw-evolution-follow-queue-v15.md')
OUT_DEEP = Path('outputs/openclaw-evolution-deep-dive-queue-v15.md')

BASE_ADOPT = ['Agent Browser', 'Summarize', 'Github', 'self-improving-agent']
BASE_FOLLOW = []
BASE_DEEP = ['Polymarket', 'Weather']


def load_cal():
    items = json.loads(CAL.read_text(encoding='utf-8')).get('items', [])
    return {x['name']: x for x in items if x['track'] == 'openclaw-evolution'}


def main():
    cal = load_cal()
    adopt = list(BASE_ADOPT)
    follow = list(BASE_FOLLOW)
    deep = list(BASE_DEEP)

    gog = cal.get('Gog')
    proactive = cal.get('Proactive Agent')

    if proactive and proactive['calibrated_judgment'] in ('adopt-candidate', 'adopt') and 'Proactive Agent' not in adopt:
        adopt.append('Proactive Agent')
    if gog and gog['calibrated_judgment'] == 'follow' and 'Gog' not in follow:
        follow.append('Gog')

    brief = ['# OpenClaw Evolution Brief v15\n', 'Calibration-native OpenClaw output: final queues now consume calibration results directly.\n']
    brief.append('## Adopt / adopt-candidate\n')
    for name in adopt:
        if name == 'Proactive Agent':
            brief.append(f"- **{name}** — upgraded via calibration rule `{proactive['applied_rules'][0]}`; strategically relevant behavior-layer capability.")
        elif name == 'self-improving-agent':
            brief.append(f"- **{name}** — remains adopt, but with known risk/evidence caution.")
        else:
            brief.append(f"- **{name}**")
    brief.append('\n## Follow\n')
    for name in follow:
        if name == 'Gog':
            brief.append(f"- **{name}** — remains `follow` via calibration rule `{gog['applied_rules'][0]}`; strong support, but reusable lesson still unclear.")
        else:
            brief.append(f"- **{name}**")
    brief.append('\n## Deep-dive\n')
    for name in deep:
        brief.append(f"- **{name}**")

    adopt_md = ['# OpenClaw Evolution Adoption Queue v15\n']
    for i, name in enumerate(adopt, start=1):
        adopt_md.append(f"## {i}. {name}")
        if name == 'Proactive Agent':
            adopt_md.append(f"- Calibrated judgment: `{proactive['calibrated_judgment']}`")
            adopt_md.append(f"- Applied rule: `{proactive['applied_rules'][0]}`")
            adopt_md.append(f"- Why: {proactive['why']}")
        elif name == 'self-improving-agent':
            adopt_md.append('- Why: strong reusable self-improvement pattern, but keep risk/evidence caution visible.')
        else:
            adopt_md.append('- Why: retained as a top OpenClaw evolution adopt signal.')
        adopt_md.append('')

    follow_md = ['# OpenClaw Evolution Follow Queue v15\n']
    for i, name in enumerate(follow, start=1):
        follow_md.append(f"## {i}. {name}")
        if name == 'Gog':
            follow_md.append(f"- Calibrated judgment: `{gog['calibrated_judgment']}`")
            follow_md.append(f"- Applied rule: `{gog['applied_rules'][0]}`")
            follow_md.append(f"- Why: {gog['why']}")
            follow_md.append('- Interpretation: hold because lesson clarity is weaker than browser/search/summarize, not because support is weak.')
        else:
            follow_md.append('- Why: retained as a follow item.')
        follow_md.append('')

    deep_md = ['# OpenClaw Evolution Deep-Dive Queue v15\n']
    for i, name in enumerate(deep, start=1):
        deep_md += [f"## {i}. {name}", '- Why: keep in deep-dive until broader reusable lesson becomes clearer.', '']

    OUT_BRIEF.write_text('\n'.join(brief), encoding='utf-8')
    OUT_ADOPT.write_text('\n'.join(adopt_md), encoding='utf-8')
    OUT_FOLLOW.write_text('\n'.join(follow_md), encoding='utf-8')
    OUT_DEEP.write_text('\n'.join(deep_md), encoding='utf-8')
    print(json.dumps({'ok': True, 'adopt_count': len(adopt), 'follow_count': len(follow)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
