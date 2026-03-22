#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

INPUT = Path('test-output/skill-mcp-trend-intelligence-refined.json')
SOURCE_J = Path('test-output/openclaw-evolution-promote-source-v11.json')
OUTPUT = Path('test-output/openclaw-evolution-enriched-v2.json')
BRIEF = Path('outputs/openclaw-evolution-brief-enriched-v2.md')

KEEP_KEYWORDS = ['self-improving', 'proactive', 'summarize', 'github', 'browser', 'search', 'skill vetter']
GOOD_SOURCE_JUDGMENTS = {'promote-source', 'track-ranking-source', 'track-weekly-source', 'risk-signal', 'inspect-skill-spec'}


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def load_items():
    return load_json(INPUT).get('items', [])


def pick_candidates(items):
    out = []
    for item in items:
        skill = item.get('skill', '').lower()
        if any(k in skill for k in KEEP_KEYWORDS) or item.get('cross_source'):
            out.append(item)
        if len(out) >= 6:
            break
    return out


def source_judgment_map():
    items = load_json(SOURCE_J).get('items', [])
    return {x['canonical_url']: x for x in items}


def run_search(query):
    cmd = [
        'python3', '/root/.openclaw/skills/search-layer/scripts/search.py',
        '--queries', query,
        '--mode', 'deep',
        '--intent', 'exploratory',
        '--num', '4'
    ]
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)


def summarize_results(results, source_map):
    refs = []
    for r in results[:6]:
        url = r.get('url', '')
        src_meta = source_map.get(url)
        refs.append({
            'title': r.get('title', ''),
            'url': url,
            'source': r.get('source', ''),
            'source_judgment': src_meta.get('source_judgment') if src_meta else None,
        })
    return refs


def infer_filtered_source_candidates(results, source_map):
    out = []
    seen = set()
    for r in results:
        url = r.get('url', '')
        meta = source_map.get(url)
        if not meta:
            continue
        if meta.get('source_judgment') not in GOOD_SOURCE_JUDGMENTS:
            continue
        if url in seen:
            continue
        seen.add(url)
        out.append({
            'url': url,
            'source_judgment': meta.get('source_judgment'),
            'object_type': meta.get('object_type'),
            'source_score': meta.get('source_score'),
        })
    return out[:6]


def source_quality_notes(filtered):
    notes = []
    js = [x['source_judgment'] for x in filtered]
    if 'promote-source' in js:
        notes.append('Includes canonical sources already strong enough for promotion.')
    if 'track-ranking-source' in js or 'track-weekly-source' in js:
        notes.append('Includes ranking/weekly intelligence surfaces useful for continued monitoring.')
    if 'risk-signal' in js:
        notes.append('Contains explicit risk/evidence signal that should affect judgment, not just popularity.')
    if not notes:
        notes.append('No source-judged high-value objects were confirmed yet.')
    return notes


def suggested_judgment(item, filtered):
    skill = item.get('skill', '').lower()
    js = {x['source_judgment'] for x in filtered}
    if any(k in skill for k in ['self-improving', 'summarize', 'github', 'browser']) and 'promote-source' in js:
        return 'adopt-or-follow'
    if 'risk-signal' in js or any(k in skill for k in ['polymarket', 'weather', 'baidu']):
        return 'deep-dive'
    if filtered:
        return 'follow'
    return 'follow-light'


def build_brief(enriched):
    lines = ['# OpenClaw Evolution Brief (Enriched v2)\n', 'Enrichment now fed by source judgment, so low-value evidence is filtered harder and source roles are explicit.\n']
    for item in enriched:
        lines.append(f"## {item['skill']}")
        lines.append(f"- prior signal: {item['signal_summary']}")
        lines.append(f"- suggested judgment: `{item['suggested_judgment']}`")
        lines.append(f"- source quality notes: {' '.join(item['source_quality_notes'])}")
        lines.append(f"- filtered source candidates:")
        for ref in item['source_candidate_urls'][:4]:
            lines.append(f"  - {ref['url']} (`{ref['source_judgment']}` / `{ref['object_type']}` / score {ref['source_score']})")
        lines.append('')
    return '\n'.join(lines)


def main():
    items = load_items()
    selected = pick_candidates(items)
    source_map = source_judgment_map()
    enriched = []
    for item in selected:
        query = f"{item['skill']} OpenClaw skill GitHub ClawHub"
        search = run_search(query)
        results = search.get('results', [])
        filtered_sources = infer_filtered_source_candidates(results, source_map)
        enriched.append({
            'skill': item['skill'],
            'owners': item.get('owners', []),
            'signal_summary': f"trend_score={item.get('trend_score')} cross_source={item.get('cross_source')} best_rank={item.get('best_rank')}",
            'validation_sources': summarize_results(results, source_map),
            'source_candidate_urls': filtered_sources,
            'source_quality_notes': source_quality_notes(filtered_sources),
            'suggested_judgment': suggested_judgment(item, filtered_sources),
        })
    OUTPUT.write_text(json.dumps({'ok': True, 'items': enriched}, ensure_ascii=False, indent=2), encoding='utf-8')
    BRIEF.write_text(build_brief(enriched), encoding='utf-8')
    print(json.dumps({'ok': True, 'count': len(enriched), 'output': str(OUTPUT), 'brief': str(BRIEF)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
