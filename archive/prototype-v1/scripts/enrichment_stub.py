#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SEARCH_SCRIPT = Path('/root/.openclaw/skills/search-layer/scripts/search.py')


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


def classify_result(result):
    text = ((result.get('title') or '') + ' ' + (result.get('snippet') or '') + ' ' + (result.get('url') or '')).lower()
    if 'github.com' in text and ('/releases' in text or 'changelog' in text):
        return 'official_release'
    if 'developers.openai.com' in text or 'anthropic.com' in text or 'docs.openclaw.ai' in text or 'github.blog' in text:
        return 'official_or_engineering'
    if 'github.com' in text:
        return 'github'
    return 'other'


def build_query(item):
    title = item.get('title') or ''
    feed_name = item.get('feed_name') or ''
    terms = [title]
    if 'show hn:' in title.lower():
        terms.append('github repo')
        terms.append('developer tooling')
    if item.get('triage_mode') == 'agentic':
        terms.append('OpenClaw Claude Code Codex Gemini MCP')
    return ' '.join(terms)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    args = ap.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = []
    for entry in data.get('candidates', []):
        item = entry.get('item', {})
        query = build_query(item)
        search = run_search(query)
        search_results = search.get('results', [])[:5]

        official_hit = False
        cross_source_count = 0
        related_sources = []
        seen_domains = set()

        for r in search_results:
            kind = classify_result(r)
            url = r.get('url') or ''
            domain = url.split('/')[2] if '://' in url else url
            if domain and domain not in seen_domains:
                seen_domains.add(domain)
                cross_source_count += 1
            if kind in ('official_release', 'official_or_engineering'):
                official_hit = True
            related_sources.append({
                'title': r.get('title'),
                'url': url,
                'kind': kind,
            })

        confidence_delta = 0.0
        reason = 'no corroboration found'
        validated = False
        if official_hit:
            confidence_delta += 0.8
            validated = True
            reason = 'confirmed by official or engineering source'
        elif cross_source_count >= 3:
            confidence_delta += 0.5
            validated = True
            reason = 'confirmed by multiple distinct sources'
        elif cross_source_count == 2:
            confidence_delta += 0.2
            reason = 'light corroboration from two sources'

        results.append({
            'id': item.get('id'),
            'validated': validated,
            'crossSourceCount': cross_source_count,
            'officialHit': official_hit,
            'confidenceDelta': round(confidence_delta, 2),
            'reason': reason,
            'query': query,
            'relatedSources': related_sources,
        })

    print(json.dumps({
        'ok': True,
        'results': results,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
