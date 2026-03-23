#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

OUT_JSON = Path('test-output/targeted-calibration-v1.json')
OUT_MD = Path('outputs/targeted-calibration-v1.md')

TARGETS = [
    {
        'name': 'jarrodwatts/claude-hud',
        'track': 'applied-ai-evolution',
        'current': 'follow',
        'queries': [
            'jarrodwatts/claude-hud Claude Code plugin GitHub awesome claude code',
            'jarrodwatts claude-hud claude-delegator Claude Code ecosystem',
            'claude-hud statusline plugin workflow Claude Code'
        ]
    },
    {
        'name': 'gsd-build/get-shit-done',
        'track': 'applied-ai-evolution',
        'current': 'follow',
        'queries': [
            'gsd-build/get-shit-done Claude Code framework spec-driven development GitHub',
            'get-shit-done framework Claude Code workflow methodology GitHub',
            'gsd build get-shit-done context engineering framework'
        ]
    },
    {
        'name': 'Gog',
        'track': 'openclaw-evolution',
        'current': 'follow',
        'queries': [
            'Gog OpenClaw skill ClawHub GitHub steipete',
            'steipete gog skill OpenClaw skill meaning use case',
            'Gog ClawHub OpenClaw awesome skills'
        ]
    },
    {
        'name': 'Proactive Agent',
        'track': 'openclaw-evolution',
        'current': 'follow',
        'queries': [
            'Proactive Agent OpenClaw skill ClawHub GitHub',
            'OpenClaw proactive agent skill autonomous follow through',
            'proactive agent clawhub skill github'
        ]
    },
]


def search(query):
    cmd = [
        'python3', '/root/.openclaw/skills/search-layer/scripts/search.py',
        '--queries', query,
        '--mode', 'deep',
        '--intent', 'exploratory',
        '--num', '5'
    ]
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out).get('results', [])


def analyze(target, results):
    urls = ' '.join(r.get('url', '') for r in results)
    titles = ' '.join(r.get('title', '') for r in results).lower()
    github_hits = sum(1 for r in results if 'github.com' in r.get('url', ''))
    doc_hits = sum(1 for r in results if 'docs' in r.get('url', '') or 'clawhub.ai' in r.get('url', ''))
    ecosystem_hits = sum(1 for r in results if any(k in r.get('url', '') for k in ['awesome', 'clawhub', 'skills', 'claude-code']))

    label = 'hold-follow'
    reason = 'Signal remains interesting, but the extra targeted evidence is not yet strong enough to justify an upgrade.'

    name = target['name'].lower()
    if 'claude-hud' in name:
        if github_hits >= 3 and ecosystem_hits >= 2:
            label = 'upgrade-to-adopt'
            reason = 'Concrete tooling surface with repeated ecosystem references, adjacent author projects, and clear practical utility.'
    elif 'get-shit-done' in name:
        if github_hits >= 3 and ('framework' in titles or 'methodology' in titles or 'spec' in titles):
            label = 'keep-follow-methodology'
            reason = 'Strong methodology/reference-framework signal, but still better treated as a framework to study than a direct product capability to adopt.'
    elif name == 'gog':
        if ecosystem_hits >= 2 and doc_hits >= 1:
            label = 'keep-follow-unclear-lesson'
            reason = 'Well-supported skill, but the reusable product lesson remains less clear than browser/search/summarize style capabilities.'
    elif 'proactive agent' in name:
        if github_hits + doc_hits >= 2:
            label = 'upgrade-to-adopt-candidate'
            reason = 'Proactive execution remains strategically relevant; if stronger canonical references exist, it should move closer to adopt.'
        else:
            label = 'keep-follow-needs-source-support'
            reason = 'Behavioral relevance is high, but canonical ecosystem support is still too weak.'

    return {
        'github_hits': github_hits,
        'doc_hits': doc_hits,
        'ecosystem_hits': ecosystem_hits,
        'recommended_change': label,
        'reason': reason,
    }


def main():
    out = []
    for target in TARGETS:
        all_results = []
        for q in target['queries']:
            try:
                all_results.extend(search(q))
            except Exception as e:
                all_results.append({'title': f'ERROR: {e}', 'url': '', 'source': 'error'})
        # dedupe by url/title
        dedup, seen = [], set()
        for r in all_results:
            key = (r.get('url', ''), r.get('title', ''))
            if key in seen:
                continue
            seen.add(key)
            dedup.append(r)
        analysis = analyze(target, dedup[:10])
        out.append({
            **target,
            'analysis': analysis,
            'refs': dedup[:8],
        })

    OUT_JSON.write_text(json.dumps({'ok': True, 'items': out}, ensure_ascii=False, indent=2), encoding='utf-8')

    lines = ['# Targeted Calibration v1\n', 'Focused calibration on borderline items to understand whether they should upgrade, hold, or split into clearer semantic buckets.\n']
    for item in out:
        a = item['analysis']
        lines.append(f"## {item['name']} ({item['track']})")
        lines.append(f"- Current judgment: `{item['current']}`")
        lines.append(f"- Recommended change: `{a['recommended_change']}`")
        lines.append(f"- Why: {a['reason']}")
        lines.append(f"- Evidence summary: github_hits={a['github_hits']} doc_hits={a['doc_hits']} ecosystem_hits={a['ecosystem_hits']}")
        lines.append(f"- Top refs:")
        for r in item['refs'][:5]:
            lines.append(f"  - {r.get('title','')} — {r.get('url','')} ({r.get('source','')})")
        lines.append('')
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'ok': True, 'json': str(OUT_JSON), 'md': str(OUT_MD), 'count': len(out)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
