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
    ap.add_argument('--triaged', required=True)
    ap.add_argument('--enrichment', required=True)
    args = ap.parse_args()

    with open(args.triaged, 'r', encoding='utf-8') as f:
        triaged = json.load(f)
    with open(args.enrichment, 'r', encoding='utf-8') as f:
        enrichment = json.load(f)

    tm = load_topic_model()
    thresholds = tm.get('scoring_policy', {}).get('thresholds', {})
    send_threshold = float(thresholds.get('send', 3.8))

    enrich_map = {r.get('id'): r for r in enrichment.get('results', [])}
    merged_items = []
    counts = {'send': 0, 'digest': 0, 'drop': 0}

    for item in triaged.get('items', []):
        tri = item.get('triage', {})
        base_score = float(tri.get('score', 0))
        enr = enrich_map.get(item.get('id'))
        delta = float(enr.get('confidenceDelta', 0.0)) if enr else 0.0
        enriched_score = round(base_score + delta, 2)
        final_decision = tri.get('decision')

        if enr and enr.get('validated'):
            if final_decision == 'digest' and enriched_score >= (send_threshold - 0.2):
                final_decision = 'send'
        item['triage']['enrichment'] = enr or None
        item['triage']['enriched_score'] = enriched_score
        item['triage']['final_decision'] = final_decision
        merged_items.append(item)
        counts[final_decision] += 1

    print(json.dumps({
        'ok': True,
        'items': merged_items,
        'counts': counts,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
