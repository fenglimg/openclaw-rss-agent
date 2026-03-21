#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

import yaml


GENERAL_HIGH = [
    'ai', 'llm', 'open source', 'cli', 'sdk', 'api', 'tooling', 'release', 'launch',
    'github actions', 'copilot', 'workflow', 'automation', 'prompt', 'model'
]
GENERAL_MEDIUM = [
    'python', 'rust', 'go', 'typescript', 'docker', 'kubernetes', 'database',
    'security', 'git', 'github', 'devtools', 'oss', 'parser', 'search',
    'compiler', 'middleware', 'benchmark', 'performance', 'infra', 'deployment',
    'framework', 'library', 'testing', 'release notes', 'actions'
]
GENERAL_LOW = ['funding', 'opinion', 'hiring', 'layoffs', 'sales', 'marketing', 'politics', 'celebrity', 'sports', 'attack', 'war', 'military', 'missile', 'iran']

AGENTIC_HIGH = [
    'openclaw', 'agent', 'agents', 'agentic', 'ai agent', 'coding agent', 'workflow',
    'automation', 'rss', 'prompt', 'tooling', 'cli', 'sdk', 'api', 'copilot',
    'model context', 'rag', 'vector', 'inference', 'tool calling', 'multi-agent'
]
AGENTIC_MEDIUM = [
    'llm', 'github actions', 'github', 'search', 'parser', 'library', 'framework',
    'devtools', 'open source', 'release', 'middleware', 'orchestration', 'evaluation'
]
AGENTIC_LOW = ['politics', 'celebrity', 'sports', 'sales', 'marketing', 'opinion']

SOLID_TECH_FEEDS = ['github blog', 'hacker news']
TOPIC_MODEL_PATH = Path(__file__).resolve().parent.parent / 'topic_model.yaml'


def norm(text):
    return re.sub(r'\s+', ' ', (text or '').strip().lower())


def score_text(text, words, weight):
    total = 0.0
    hits = 0
    for w in words:
        if w and norm(w) in text:
            total += weight
            hits += 1
    return total, hits


def load_topic_model(path=TOPIC_MODEL_PATH):
    if not path.exists():
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def get_source_adjust(item, tm):
    sp = tm.get('source_policy', {})
    role_weights = sp.get('role_weights', {})
    source_overrides = sp.get('source_overrides', {})
    feed_id = item.get('feed_id') or ''
    source_role = item.get('source_role') or ''
    return float(source_overrides.get(feed_id, role_weights.get(source_role, 0.0)))


def get_language_adjust(item, tm):
    lp = tm.get('language_policy', {})
    by_language = lp.get('by_language', {})
    lang = item.get('language') or ''
    default_adjust = float(lp.get('default_adjust', 0.0))
    return float(by_language.get(lang, {}).get('adjust', default_adjust))


def get_profile(mode, tm):
    tp = tm.get('topic_model', {})
    sp = tm.get('scoring_policy', {})
    thresholds = sp.get('thresholds', {})
    if mode == 'agentic':
        return {
            'high': AGENTIC_HIGH,
            'medium': AGENTIC_MEDIUM,
            'low': AGENTIC_LOW,
            'w_high': 1.3,
            'w_medium': 0.8,
            'w_low': 0.9,
            'seed_terms': tp.get('seed_terms', []),
            'promoted_terms': tp.get('promoted_terms', []),
            'weak_terms': tp.get('weak_terms', []),
            'suppress_terms': tp.get('suppress_terms', []),
            'cooccurrence_rules': tp.get('cooccurrence_rules', []),
            'seed_weight': sp.get('seed_term_weight', 1.2),
            'promoted_weight': sp.get('promoted_term_weight', 0.7),
            'weak_weight': sp.get('weak_term_weight', 0.2),
            'suppress_weight': sp.get('suppress_term_penalty', 1.0),
            'max_weak': sp.get('max_weak_term_contribution', 0.6),
            'send_threshold': thresholds.get('send', 3.8),
            'digest_threshold': thresholds.get('digest', 1.5),
        }
    return {
        'high': GENERAL_HIGH,
        'medium': GENERAL_MEDIUM,
        'low': GENERAL_LOW,
        'w_high': 1.1,
        'w_medium': 0.7,
        'w_low': 0.9,
        'seed_terms': tp.get('seed_terms', []),
        'promoted_terms': tp.get('promoted_terms', []),
        'weak_terms': tp.get('weak_terms', []),
        'suppress_terms': tp.get('suppress_terms', []),
        'cooccurrence_rules': tp.get('cooccurrence_rules', []),
        'seed_weight': sp.get('seed_term_weight', 1.2),
        'promoted_weight': sp.get('promoted_term_weight', 0.7),
        'weak_weight': sp.get('weak_term_weight', 0.2),
        'suppress_weight': sp.get('suppress_term_penalty', 1.0),
        'max_weak': sp.get('max_weak_term_contribution', 0.6),
        'send_threshold': thresholds.get('send', 3.8) - 0.4,
        'digest_threshold': thresholds.get('digest', 1.5),
    }


def cooccurrence_bonus(text, rules):
    bonus = 0.0
    hits = 0
    for rule in rules:
        words = [norm(x) for x in rule.get('all', [])]
        if words and all(w in text for w in words):
            bonus += float(rule.get('bonus', 0.0))
            hits += 1
    return bonus, hits


def decide(item, default_mode, tm, ignore_feed_mode=False):
    mode = default_mode if ignore_feed_mode else (item.get('triage_mode') or default_mode)
    profile = get_profile(mode, tm)
    title = norm(item.get('title'))
    summary = norm(item.get('summary'))
    feed_name = norm(item.get('feed_name'))
    tags = [norm(t) for t in item.get('tags', [])]
    boost_keywords = [norm(t) for t in item.get('boost_keywords', [])]
    source_adjust = get_source_adjust(item, tm)
    language_adjust = get_language_adjust(item, tm)
    suppress_keywords = [norm(t) for t in item.get('suppress_keywords', [])]
    priority_topics = [norm(t) for t in item.get('priority_topics', [])]
    text = ' '.join([title, summary, feed_name, ' '.join(tags)])

    score = 0.0
    high_score, high_hits = score_text(text, profile['high'], profile['w_high'])
    med_score, med_hits = score_text(text, profile['medium'], profile['w_medium'])
    low_score, low_hits = score_text(text, profile['low'], profile['w_low'])
    score += high_score + med_score - low_score
    base_hits = high_hits + med_hits

    seed_score, seed_hits = score_text(text, profile['seed_terms'], profile['seed_weight'])
    promoted_score, promoted_hits = score_text(text, profile['promoted_terms'], profile['promoted_weight'])
    weak_score, weak_hits = score_text(text, profile['weak_terms'], profile['weak_weight'])
    weak_score = min(weak_score, profile['max_weak'])
    suppress_score, suppress_hits = score_text(text, profile['suppress_terms'], profile['suppress_weight'])
    score += seed_score + promoted_score + weak_score - suppress_score
    base_hits += seed_hits + promoted_hits

    include = [norm(x) for x in item.get('include', [])]
    exclude = [norm(x) for x in item.get('exclude', [])]
    if include:
        if any(x in text for x in include):
            score += 1.0
            base_hits += 1
        else:
            score -= 0.8
    if exclude and any(x in text for x in exclude):
        score -= 3.0

    boost_score, boost_hits = score_text(text, boost_keywords, 0.35)
    priority_score, priority_hits = score_text(text, priority_topics, 0.25)
    suppress_local_score, suppress_local_hits = score_text(text, suppress_keywords, 0.8)
    score += boost_score + priority_score - suppress_local_score

    co_bonus, co_hits = cooccurrence_bonus(text, profile['cooccurrence_rules'])
    score += co_bonus
    score += source_adjust
    score += language_adjust
    base_hits += co_hits

    if title.startswith('show hn:'):
        score += 0.9
        base_hits += 1
    if any(feed in feed_name for feed in SOLID_TECH_FEEDS):
        score += 0.4
    if mode == 'general-tech':
        if 'github blog' in feed_name and ('github' in text or 'actions' in text or 'copilot' in text or 'open source' in text):
            score += 0.6
            base_hits += 1
        if 'open source' in text or 'sdk' in text or 'library' in text or 'framework' in text:
            score += 0.4
            base_hits += 1
        if any(x in text for x in ['attack', 'war', 'military', 'missile', 'election', 'president', 'prime minister']):
            score -= 1.6
        workflow_scaffold_hits = sum(1 for x in ['show hn:', 'repo template', 'ai-assisted', 'sdlc', 'software development'] if x in text or x in title)
        if workflow_scaffold_hits >= 2:
            score += 1.5
            base_hits += 1
        elif workflow_scaffold_hits == 1:
            score += 0.6
    else:
        if 'openclaw' in text or 'agent' in text or 'workflow' in text or 'automation' in text:
            score += 0.9
            base_hits += 1
        if 'ai-assisted' in text or 'tooling' in text or 'sdlc' in text or 'repo template' in text:
            score += 0.7
            base_hits += 1
        if 'rss' in text:
            score += 0.5
            base_hits += 1
        if 'github blog' in feed_name and ('copilot' in text or 'actions' in text or 'workflow' in text):
            score += 0.6
            base_hits += 1
    if summary == 'comments':
        score -= 0.1

    if base_hits == 0 and (boost_hits > 0 or priority_hits > 0):
        score = min(score, profile['digest_threshold'] - 0.05)

    discovery_tooling_floor = False
    if mode == 'general-tech':
        is_show_hn = 'show hn:' in title
        is_github_repo = 'github.com/' in (item.get('link') or '')
        tooling_hits = sum(1 for x in ['repo template', 'ai-assisted', 'sdlc', 'scaffold', 'tooling'] if x in text or x in title)
        if is_show_hn and is_github_repo and tooling_hits >= 2:
            score = max(score, profile['digest_threshold'])
            discovery_tooling_floor = True

    if score >= profile['send_threshold'] and base_hits >= 2:
        decision = 'send'
        reason = f'High-signal match for {mode} curation goals'
    elif score >= profile['digest_threshold']:
        decision = 'digest'
        reason = f'Good fit for {mode} roundup'
    else:
        decision = 'drop'
        reason = f'Low relevance for {mode} curation goals'

    return {
        **item,
        'triage': {
            'mode': mode,
            'decision': decision,
            'score': round(score, 2),
            'reason': reason,
            'debug': {
                'base_hits': base_hits,
                'seed_hits': seed_hits,
                'promoted_hits': promoted_hits,
                'weak_hits': weak_hits,
                'cooccurrence_hits': co_hits,
                'boost_hits': boost_hits,
                'source_adjust': source_adjust,
                'language_adjust': language_adjust,
                'priority_hits': priority_hits,
                'discovery_tooling_floor': discovery_tooling_floor,
                'suppress_hits': suppress_hits + suppress_local_hits,
            }
        }
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--mode', choices=['general-tech', 'agentic'], default='general-tech')
    ap.add_argument('--ignore-feed-mode', action='store_true')
    args = ap.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    items = data.get('new_items', [])
    tm = load_topic_model()

    triaged = [decide(item, args.mode, tm, ignore_feed_mode=args.ignore_feed_mode) for item in items]
    counts = {'send': 0, 'digest': 0, 'drop': 0}
    for item in triaged:
        counts[item['triage']['decision']] += 1

    print(json.dumps({
        'ok': True,
        'default_mode': args.mode,
        'ignore_feed_mode': args.ignore_feed_mode,
        'topic_model_loaded': bool(tm),
        'items': triaged,
        'counts': counts,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
