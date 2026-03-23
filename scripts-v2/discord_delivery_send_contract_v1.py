#!/usr/bin/env python3
import json
import sys
from pathlib import Path

INPUT = Path('test-output/discord-chunked-delivery-v1.json')
OUTPUT = Path('test-output/discord-delivery-result-v1.json')


def main():
    if not INPUT.exists():
        print(json.dumps({'ok': False, 'error': 'missing chunk file'}, ensure_ascii=False))
        return 1
    data = json.loads(INPUT.read_text(encoding='utf-8'))
    chunks = data.get('chunks', [])
    result = {
        'ok': True,
        'status': 'send-stage-contract-ready',
        'input': str(INPUT),
        'chunk_count': len(chunks),
        'delivery_plan': [
            {
                'index': i + 1,
                'length': len(chunk),
                'status': 'pending-send',
            }
            for i, chunk in enumerate(chunks)
        ],
        'notes': [
            'This file defines the concrete send-stage contract for Discord chunk delivery.',
            'Next step: replace pending-send entries with real message tool sends and persisted message ids.'
        ]
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'ok': True, 'output': str(OUTPUT), 'chunk_count': len(chunks)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
