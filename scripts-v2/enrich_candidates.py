#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

INPUT = Path('test-output/skill-mcp-trend-intelligence-refined.json')
OUTPUT = Path('test-output/openclaw-evolution-enriched.json')
REFINED_BRIEF = Path('outputs/openclaw-evolution-brief-enriched.md')

KEEP_KEYWORDS = ['self-improving', 'proactive', 'summarize', 'github', 'browser', 'search', 'skill vetter']


def load_items():
    data = json.loads(INPUT.read_text(encoding='utf-8'))
    return data.get('items', [])


def pick_candidates(items):
    out = []
    for item in items:
        skill = item.get('skill', '').lower()
        if any(k in skill for k in KEEP_KEYWORDS) or item.get('cross_source'):
            out.append(item)
        if len(out) >= 6:
            break
    return out


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


def summarize_results(results):
    refs = []
    for r in results[:4]:
        refs.append({
            'title': r.get('title', ''),
            'url': r.get('url', ''),
            'source': r.get('source', ''),
        })
    return refs


def infer_source_candidates(results):
    urls = []
    for r in results:
        url = r.get('url', '')
        if any(k in url for k in ['github.com', 'clawhub.ai', 'playbooks.com', 'topclawhubskills.com', 'clawhubtrends.com']):
            urls.append(url)
    seen = set()
    out = []
    for u in urls:
        if u in seen:
            continue
        seen.add(u)
        out.append(u)
    return out[:6]


def source_quality_notes(results):
    notes = []
    domains = []
    for r in results[:6]:
        url = r.get('url', '')
        if 'github.com' in url:
            domains.append('github')
        elif 'clawhub.ai' in url:
            domains.append('clawhub')
        elif 'playbooks.com' in url:
            domains.append('playbooks')
        elif 'topclawhubskills.com' in url:
            domains.append('topclawhubskills')
        elif 'clawhubtrends.com' in url:
            domains.append('clawhubtrends')
    if any(d in domains for d in ['github', 'clawhub']):
        notes.append('Has at least one high-trust ecosystem reference (GitHub or ClawHub).')
    if sum(1 for d in domains if d in {'github', 'clawhub', 'playbooks'}) >= 2:
        notes.append('Cross-domain ecosystem confirmation exists beyond a single ranking page.')
    if not notes:
        notes.append('Mostly weak or single-surface validation so far; treat cautiously.')
    return notes


def suggested_judgment(item, results):
    skill = item.get('skill', '').lower()
    urls = ' '.join(r.get('url', '') for r in results[:6])
    if any(k in skill for k in ['self-improving', 'proactive', 'summarize', 'github', 'browser', 'search']):
        return 'adopt-or-follow'
    if 'clawhub.ai' in urls or 'github.com' in urls:
        return 'follow'
    return 'deep-dive'


def build_brief(enriched):
    lines = ['# OpenClaw Evolution Brief (Enriched)\n', 'Second-pass brief after selective search-layer enrichment.\n']
    for item in enriched:
        lines.append(f"## {item['skill']}")
        lines.append(f"- prior signal: {item['signal_summary']}")
        lines.append(f"- suggested judgment: `{item['suggested_judgment']}`")
        lines.append(f"- source quality notes: {' '.join(item['source_quality_notes'])}")
        lines.append(f"- top validation refs:")
        for ref in item['validation_sources'][:3]:
            lines.append(f"  - {ref['title']} — {ref['url']} ({ref['source']})")
        if item['source_candidate_urls']:
            lines.append(f"- source expansion candidates:")
            for u in item['source_candidate_urls'][:3]:
                lines.append(f"  - {u}")
        lines.append('')
    return '\n'.join(lines)


def main():
    items = load_items()
    selected = pick_candidates(items)
    enriched = []
    for item in selected:
        query = f"{item['skill']} OpenClaw skill GitHub ClawHub"
        search = run_search(query)
        results = search.get('results', [])
        enriched.append({
            'skill': item['skill'],
            'owners': item.get('owners', []),
            'signal_summary': f"trend_score={item.get('trend_score')} cross_source={item.get('cross_source')} best_rank={item.get('best_rank')}",
            'validation_sources': summarize_results(results),
            'source_candidate_urls': infer_source_candidates(results),
            'source_quality_notes': source_quality_notes(results),
            'suggested_judgment': suggested_judgment(item, results),
        })
    OUTPUT.write_text(json.dumps({'ok': True, 'items': enriched}, ensure_ascii=False, indent=2), encoding='utf-8')
    REFINED_BRIEF.write_text(build_brief(enriched), encoding='utf-8')
    print(json.dumps({'ok': True, 'count': len(enriched), 'output': str(OUTPUT), 'brief': str(REFINED_BRIEF)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
