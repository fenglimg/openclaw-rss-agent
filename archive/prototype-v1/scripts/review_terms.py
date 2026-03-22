#!/usr/bin/env python3
import argparse
import json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    args = ap.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    strong = []
    cand = []
    ignored = []
    for item in data.get('validated_terms', []):
        rec = item.get('recommendation')
        row = {
            'term': item.get('term'),
            'examples': item.get('examples', []),
            'phrase_score': item.get('phrase_score', 0),
            'score': item.get('score', 0),
            'officialish_hits': item.get('officialish_hits', 0),
            'results': item.get('results', [])[:3],
        }
        if rec == 'strong_candidate':
            strong.append(row)
        elif rec == 'candidate':
            cand.append(row)
        else:
            ignored.append(row)

    report = {
        'ok': True,
        'summary': {
            'strong_candidates': len(strong),
            'candidates': len(cand),
            'ignored_terms': len(ignored),
        },
        'strong_candidates': strong,
        'candidates': cand,
        'ignored_terms': ignored,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
