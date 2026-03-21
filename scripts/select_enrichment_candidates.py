#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import yaml

TOPIC_MODEL_PATH = Path(__file__).resolve().parent.parent / 'topic_model.yaml'


def load_topic_model(path=TOPIC_MODEL_PATH):
    if not path.exists():
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    args = ap.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    tm = load_topic_model()
    ep = tm.get('enrichment_policy', {})
    enabled = bool(ep.get('enabled', False))
    max_candidates = int(ep.get('max_candidates_per_run', 0))
    send_margin = float(ep.get('send_margin', 0.7))
    noisy_roles = set(ep.get('noisy_source_roles', []))
    validate_send = bool(ep.get('validate_send_candidates', True))
    validate_digest = bool(ep.get('validate_high_digest_candidates', True))

    items = data.get('items', [])
    thresholds = tm.get('scoring_policy', {}).get('thresholds', {})
    send_threshold = float(thresholds.get('send', 3.8))

    candidates = []
    if enabled:
        for item in items:
            triage = item.get('triage', {})
            score = float(triage.get('score', 0))
            decision = triage.get('decision')
            source_role = item.get('source_role')

            should_pick = False
            reason = None
            if validate_send and decision == 'send':
                should_pick = True
                reason = 'send_candidate'
            elif validate_digest and decision == 'digest' and score >= (send_threshold - send_margin):
                should_pick = True
                reason = 'near_send_digest'
            elif source_role in noisy_roles and decision in ('send', 'digest'):
                should_pick = True
                reason = 'noisy_source_high_score'

            if should_pick:
                candidates.append({
                    'reason': reason,
                    'item': item,
                })

    candidates.sort(key=lambda x: x['item'].get('triage', {}).get('score', 0), reverse=True)
    candidates = candidates[:max_candidates]

    print(json.dumps({
        'ok': True,
        'enabled': enabled,
        'max_candidates_per_run': max_candidates,
        'count': len(candidates),
        'candidates': candidates,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
