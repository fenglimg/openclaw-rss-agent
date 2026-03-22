#!/usr/bin/env python3
import json
from pathlib import Path

CAL = Path('test-output/calibration-rule-applications-v1.json')
OUT = Path('outputs/calibration-integrated-summary-v1.md')


def main():
    items = json.loads(CAL.read_text(encoding='utf-8')).get('items', [])
    applied = [x for x in items if x['track'] == 'applied-ai-evolution']
    openclaw = [x for x in items if x['track'] == 'openclaw-evolution']

    lines = ['# Calibration Integrated Summary v1\n']
    lines.append('This file shows how the reusable calibration pass should feed final output building.\n')

    lines.append('## Applied AI Evolution — calibrated boundary results\n')
    for item in applied:
        lines.append(f"### {item['name']}")
        lines.append(f"- previous: `{item['previous_judgment']}`")
        lines.append(f"- calibrated: `{item['calibrated_judgment']}`")
        lines.append(f"- rules: {', '.join(item['applied_rules'])}")
        lines.append(f"- why: {item['why']}")
        lines.append('')

    lines.append('## OpenClaw Evolution — calibrated boundary results\n')
    for item in openclaw:
        lines.append(f"### {item['name']}")
        lines.append(f"- previous: `{item['previous_judgment']}`")
        lines.append(f"- calibrated: `{item['calibrated_judgment']}`")
        lines.append(f"- rules: {', '.join(item['applied_rules'])}")
        lines.append(f"- why: {item['why']}")
        lines.append('')

    lines.append('## Pipeline note\n')
    lines.append('Recommended final chain: enrichment → source judgment → first-pass judgment → calibration pass → final output.')
    lines.append('')
    lines.append('Current high-confidence integrated effects:')
    lines.append('- `jarrodwatts/claude-hud` should land in applied practical adopt output, not stay as generic follow.')
    lines.append('- `gsd-build/get-shit-done` should remain follow but be explained as framework-to-study.')
    lines.append('- `Gog` should remain follow because lesson clarity is weak, not because support is weak.')
    lines.append('- `Proactive Agent` should be promoted near adopt-candidate in openclaw output.')

    OUT.write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'ok': True, 'out': str(OUT), 'count': len(items)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
