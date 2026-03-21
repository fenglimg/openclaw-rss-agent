#!/usr/bin/env python3
import argparse
import json
import re
from collections import Counter
from pathlib import Path

import yaml

TOPIC_MODEL_PATH = Path(__file__).resolve().parent.parent / 'topic_model.yaml'
STOP = {
    'the','and','for','with','from','that','this','into','over','under','your','you','are','was','will','its','their','about','after','before','have','has','had','not','but','too','can','now','new','using','used','how','why','what','when','where','who','than','then','into','onto','off','out','all','one','two','three','four','five','six','seven','eight','nine','ten','comments'
}


def load_topic_model(path=TOPIC_MODEL_PATH):
    if not path.exists():
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def norm(text):
    return re.sub(r'\s+', ' ', (text or '').strip().lower())


def phrases(text):
    text = re.sub(r'[^a-zA-Z0-9\-\+\s]', ' ', norm(text))
    toks = [t for t in text.split() if len(t) >= 3 and t not in STOP]
    out = []
    for n in (2, 3):
        for i in range(len(toks)-n+1):
            p = ' '.join(toks[i:i+n])
            out.append(p)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    args = ap.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    tm = load_topic_model()
    known = set()
    for sec in ('seed_terms','promoted_terms','weak_terms','suppress_terms'):
        known.update(norm(x) for x in tm.get('topic_model', {}).get(sec, []))

    kept = [x for x in data.get('items', []) if x.get('triage', {}).get('final_decision', x.get('triage', {}).get('decision')) in ('send','digest')]
    c = Counter()
    evidence = {}
    for item in kept:
        text = f"{item.get('title','')} {item.get('summary','')}"
        for p in phrases(text):
            if p in known:
                continue
            if any(tok in STOP for tok in p.split()):
                continue
            c[p] += 1
            evidence.setdefault(p, []).append(item.get('title'))

    candidates = []
    for phrase, count in c.most_common(20):
        if count < 1:
            continue
        candidates.append({
            'term': phrase,
            'count': count,
            'examples': evidence.get(phrase, [])[:3],
        })

    print(json.dumps({
        'ok': True,
        'candidate_terms': candidates,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
