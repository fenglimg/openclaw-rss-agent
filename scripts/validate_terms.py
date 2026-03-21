#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

SEARCH_SCRIPT = Path('/root/.openclaw/skills/search-layer/scripts/search.py')
CONTEXT = 'OpenClaw Claude Code Codex Gemini MCP skills workflow automation coding agents developer tooling'


def run_search(query):
    if not SEARCH_SCRIPT.exists():
        return {'ok': False, 'error': 'search_layer_script_missing', 'results': []}
    try:
        out = subprocess.check_output([
            sys.executable,
            str(SEARCH_SCRIPT),
            '--queries', query,
            '--mode', 'deep',
            '--intent', 'exploratory',
            '--num', '5',
        ], text=True, timeout=120)
        data = json.loads(out)
        return {'ok': True, 'results': data.get('results', [])}
    except Exception as e:
        return {'ok': False, 'error': str(e), 'results': []}


def score_results(results):
    score = 0
    officialish = 0
    for r in results:
        text = ((r.get('title') or '') + ' ' + (r.get('snippet') or '') + ' ' + (r.get('url') or '')).lower()
        if any(x in text for x in ['openclaw', 'claude code', 'codex', 'gemini', 'mcp', 'skill', 'agent', 'workflow', 'tooling']):
            score += 1
        if any(x in text for x in ['developers.openai.com', 'anthropic.com', 'docs.openclaw.ai', 'github.blog', 'github.com']):
            officialish += 1
    return score, officialish


def label(score, officialish):
    if score >= 3 or (score >= 2 and officialish >= 1):
        return 'promote'
    if score >= 1:
        return 'watch'
    return 'ignore'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    args = ap.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    outputs = []
    for c in data.get('candidate_terms', [])[:10]:
        term = c.get('term')
        query = f'{term} {CONTEXT}'
        search = run_search(query)
        results = search.get('results', [])[:5]
        score, officialish = score_results(results)
        outputs.append({
            'term': term,
            'count': c.get('count', 0),
            'examples': c.get('examples', []),
            'score': score,
            'officialish_hits': officialish,
            'recommendation': label(score, officialish),
            'results': [
                {
                    'title': r.get('title'),
                    'url': r.get('url')
                } for r in results
            ]
        })

    print(json.dumps({
        'ok': True,
        'validated_terms': outputs,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
