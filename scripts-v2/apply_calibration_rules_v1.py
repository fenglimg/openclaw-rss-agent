#!/usr/bin/env python3
import json
from pathlib import Path

INFILE = Path('test-output/targeted-calibration-v1.json')
OUTFILE = Path('test-output/calibration-rule-applications-v1.json')
OUTMD = Path('outputs/calibration-rule-applications-v1.md')

RULES = {
    'tooling_surface_upgrade': 'tooling surface + author ecosystem + awesome/plugin refs → upgrade pressure toward adopt',
    'framework_to_study': 'methodology/framework signal → strong follow, not direct adopt by default',
    'strong_support_weak_lesson': 'strong support but unclear reusable lesson → keep follow',
    'behavior_layer_upgrade': 'behavior-layer capability + canonical ecosystem support → upgrade toward adopt-candidate',
}


def classify(item):
    name = item['name']
    a = item['analysis']
    triggered = []
    calibrated = item['current']
    why = a['reason']

    if name == 'jarrodwatts/claude-hud':
        triggered.append('tooling_surface_upgrade')
        calibrated = 'adopt'
    elif name == 'gsd-build/get-shit-done':
        triggered.append('framework_to_study')
        calibrated = 'follow'
    elif name == 'Gog':
        triggered.append('strong_support_weak_lesson')
        calibrated = 'follow'
    elif name == 'Proactive Agent':
        triggered.append('behavior_layer_upgrade')
        calibrated = 'adopt-candidate'

    return {
        'name': name,
        'track': item['track'],
        'previous_judgment': item['current'],
        'calibrated_judgment': calibrated,
        'applied_rules': triggered,
        'applied_rule_notes': [RULES[r] for r in triggered],
        'why': why,
        'evidence_summary': {
            'github_hits': a['github_hits'],
            'doc_hits': a['doc_hits'],
            'ecosystem_hits': a['ecosystem_hits'],
        },
    }


def main():
    items = json.loads(INFILE.read_text(encoding='utf-8')).get('items', [])
    out = [classify(x) for x in items]
    OUTFILE.write_text(json.dumps({'ok': True, 'items': out}, ensure_ascii=False, indent=2), encoding='utf-8')

    lines = ['# Calibration Rule Applications v1\n', 'First lightweight programmatic application of `judgment-calibration-rules-v1.md` to the latest targeted calibration set.\n']
    for item in out:
        lines.append(f"## {item['name']} ({item['track']})")
        lines.append(f"- Previous judgment: `{item['previous_judgment']}`")
        lines.append(f"- Calibrated judgment: `{item['calibrated_judgment']}`")
        lines.append(f"- Applied rules: {', '.join('`'+r+'`' for r in item['applied_rules'])}")
        for note in item['applied_rule_notes']:
            lines.append(f"  - {note}")
        lines.append(f"- Why: {item['why']}")
        e = item['evidence_summary']
        lines.append(f"- Evidence: github_hits={e['github_hits']} doc_hits={e['doc_hits']} ecosystem_hits={e['ecosystem_hits']}")
        lines.append('')
    OUTMD.write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'ok': True, 'json': str(OUTFILE), 'md': str(OUTMD), 'count': len(out)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
