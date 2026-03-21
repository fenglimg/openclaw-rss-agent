#!/usr/bin/env python3
import argparse
from pathlib import Path

import yaml

TOPIC_MODEL_PATH = Path(__file__).resolve().parent.parent / 'topic_model.yaml'


def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def save_yaml(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('terms', nargs='+')
    ap.add_argument('--path', default=str(TOPIC_MODEL_PATH))
    args = ap.parse_args()

    path = Path(args.path)
    data = load_yaml(path)
    topic_model = data.setdefault('topic_model', {})
    promoted = topic_model.setdefault('promoted_terms', [])
    existing = {str(x).strip().lower() for x in promoted}

    added = []
    for term in args.terms:
        t = term.strip()
        if not t:
            continue
        if t.lower() in existing:
            continue
        promoted.append(t)
        existing.add(t.lower())
        added.append(t)

    save_yaml(path, data)
    print(yaml.safe_dump({
        'ok': True,
        'path': str(path),
        'added': added,
        'total_promoted_terms': len(promoted),
    }, sort_keys=False, allow_unicode=True))


if __name__ == '__main__':
    main()
