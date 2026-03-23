#!/usr/bin/env python3
import json
from pathlib import Path

OUT_SIGNALS = Path('test-output/x-author-signals-v1.json')
OUT_LINKED = Path('test-output/x-linked-objects-v1.json')
OUT_BOOSTS = Path('test-output/x-candidate-boosts-v1.json')
OUT_SUMMARY = Path('outputs/x-watchlist-summary-v1.md')

SIGNALS = {
    'version': 'v1',
    'items': [
        {
            'platform': 'x',
            'author_handle': 'builder_alpha',
            'author_display_name': 'Builder Alpha',
            'post_url': 'https://x.com/builder_alpha/status/1001',
            'post_id': '1001',
            'posted_at': '2026-03-22T15:00:00Z',
            'text_excerpt': 'Claude HUD is one of the few Claude Code add-ons that actually changes how I work day to day.',
            'linked_urls': ['https://github.com/jarrodwatts/claude-hud'],
            'canonical_urls': ['https://github.com/jarrodwatts/claude-hud'],
            'mention_type': 'tool-link',
            'x_signal_role': 'author-signal',
            'engagement': {'likes': 180, 'reposts': 22, 'replies': 11, 'views': 6200},
            'author_signal_weight': 0.85,
            'track_bias': ['applied-ai-evolution'],
        },
        {
            'platform': 'x',
            'author_handle': 'workflow_beta',
            'author_display_name': 'Workflow Beta',
            'post_url': 'https://x.com/workflow_beta/status/1002',
            'post_id': '1002',
            'posted_at': '2026-03-22T15:40:00Z',
            'text_excerpt': 'Still think claude-hud is underrated if you live inside Claude Code all day.',
            'linked_urls': ['https://github.com/jarrodwatts/claude-hud'],
            'canonical_urls': ['https://github.com/jarrodwatts/claude-hud'],
            'mention_type': 'author-recommendation',
            'x_signal_role': 'editorial-reference',
            'engagement': {'likes': 95, 'reposts': 10, 'replies': 4, 'views': 3100},
            'author_signal_weight': 0.7,
            'track_bias': ['applied-ai-evolution'],
        },
        {
            'platform': 'x',
            'author_handle': 'agents_gamma',
            'author_display_name': 'Agents Gamma',
            'post_url': 'https://x.com/agents_gamma/status/1003',
            'post_id': '1003',
            'posted_at': '2026-03-22T14:50:00Z',
            'text_excerpt': 'Proactive Agent is one of the more interesting behavior-layer OpenClaw surfaces I have seen lately.',
            'linked_urls': ['https://github.com/openclaw/skills'],
            'canonical_urls': ['https://github.com/openclaw/skills'],
            'mention_type': 'trend-signal',
            'x_signal_role': 'author-signal',
            'engagement': {'likes': 140, 'reposts': 18, 'replies': 7, 'views': 5400},
            'author_signal_weight': 0.78,
            'track_bias': ['openclaw-evolution'],
        },
        {
            'platform': 'x',
            'author_handle': 'skeptic_delta',
            'author_display_name': 'Skeptic Delta',
            'post_url': 'https://x.com/skeptic_delta/status/1004',
            'post_id': '1004',
            'posted_at': '2026-03-22T16:20:00Z',
            'text_excerpt': 'Interesting idea, but Gog still feels cool before it feels reusable.',
            'linked_urls': ['https://github.com/openclaw/skills'],
            'canonical_urls': ['https://github.com/openclaw/skills'],
            'mention_type': 'editorial-opinion',
            'x_signal_role': 'risk/evidence',
            'engagement': {'likes': 60, 'reposts': 3, 'replies': 9, 'views': 1900},
            'author_signal_weight': 0.55,
            'track_bias': ['openclaw-evolution'],
        },
    ]
}

LINKED = {
    'version': 'v1',
    'items': [
        {
            'canonical_url': 'https://github.com/jarrodwatts/claude-hud',
            'object_type': 'github-repo',
            'source_posts': [
                'https://x.com/builder_alpha/status/1001',
                'https://x.com/workflow_beta/status/1002',
            ],
            'authors': ['builder_alpha', 'workflow_beta'],
            'mention_types': ['tool-link', 'author-recommendation'],
            'track_bias': ['applied-ai-evolution'],
            'x_signal_roles': ['author-signal', 'editorial-reference'],
        },
        {
            'canonical_url': 'https://github.com/openclaw/skills',
            'object_type': 'github-repo',
            'source_posts': [
                'https://x.com/agents_gamma/status/1003',
                'https://x.com/skeptic_delta/status/1004',
            ],
            'authors': ['agents_gamma', 'skeptic_delta'],
            'mention_types': ['trend-signal', 'editorial-opinion'],
            'track_bias': ['openclaw-evolution'],
            'x_signal_roles': ['author-signal', 'risk/evidence'],
        },
    ]
}

BOOSTS = {
    'version': 'v1',
    'items': [
        {
            'canonical_url': 'https://github.com/jarrodwatts/claude-hud',
            'track_bias': ['applied-ai-evolution'],
            'author_count': 2,
            'post_count': 2,
            'repeat_convergence': True,
            'boost_reason': 'multiple trusted authors linked the same object within a short time window',
            'boost_strength': 0.74,
            'recommended_effects': ['candidate-boost', 'enrichment-priority'],
        },
        {
            'canonical_url': 'https://github.com/openclaw/skills',
            'track_bias': ['openclaw-evolution'],
            'author_count': 2,
            'post_count': 2,
            'repeat_convergence': False,
            'boost_reason': 'mixed attention: one behavior-layer positive mention plus one weak skepticism signal',
            'boost_strength': 0.38,
            'recommended_effects': ['editorial-context', 'weak-risk-attachment'],
        },
    ]
}

SUMMARY = '''# X Watchlist Summary v1

First mock collector output showing how X watchlist signals can feed the current evolution discovery system.

## Stronger applied signal

### https://github.com/jarrodwatts/claude-hud
- Track bias: `applied-ai-evolution`
- Authors: `builder_alpha`, `workflow_beta`
- Signal pattern: repeated positive mention + practical tooling framing
- Recommended downstream effects:
  - `candidate-boost`
  - `enrichment-priority`
- Why it matters: this is the exact kind of repeat-convergence signal that can accelerate a practical tool from generic follow toward stronger adopt pressure.

## Mixed openclaw signal

### https://github.com/openclaw/skills
- Track bias: `openclaw-evolution`
- Authors: `agents_gamma`, `skeptic_delta`
- Signal pattern: one positive behavior-layer signal plus one weak skepticism/editorial signal
- Recommended downstream effects:
  - `editorial-context`
  - `weak-risk-attachment`
- Why it matters: this kind of X signal should not directly promote adoption, but it can explain why an item stays in `follow` instead of being upgraded too quickly.

## What this mock demonstrates

- X can boost candidate generation without becoming a stable primary source.
- X can provide repeat-convergence signals across trusted authors.
- X can attach editorial and weak risk context to canonical objects.
- The durable object remains the canonical URL, not the post itself.
'''

def main():
    OUT_SIGNALS.write_text(json.dumps(SIGNALS, ensure_ascii=False, indent=2), encoding='utf-8')
    OUT_LINKED.write_text(json.dumps(LINKED, ensure_ascii=False, indent=2), encoding='utf-8')
    OUT_BOOSTS.write_text(json.dumps(BOOSTS, ensure_ascii=False, indent=2), encoding='utf-8')
    OUT_SUMMARY.write_text(SUMMARY, encoding='utf-8')
    print(json.dumps({'ok': True, 'signals': str(OUT_SIGNALS), 'linked': str(OUT_LINKED), 'boosts': str(OUT_BOOSTS), 'summary': str(OUT_SUMMARY)}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
