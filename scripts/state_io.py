#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime, timezone


def iso_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def default_state():
    return {
        'version': 1,
        'lastRunAt': None,
        'seen': {},
        'feedHealth': {},
    }


def load_state(path):
    if not os.path.exists(path):
        return default_state()
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_state(path, state):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)

    p_load = sub.add_parser('load')
    p_load.add_argument('--state', required=True)

    p_init = sub.add_parser('init')
    p_init.add_argument('--state', required=True)

    p_touch = sub.add_parser('touch-run')
    p_touch.add_argument('--state', required=True)

    args = ap.parse_args()

    if args.cmd == 'load':
        print(json.dumps(load_state(args.state), ensure_ascii=False, indent=2))
    elif args.cmd == 'init':
        state = load_state(args.state)
        save_state(args.state, state)
        print(json.dumps({'ok': True, 'state': args.state}, ensure_ascii=False))
    elif args.cmd == 'touch-run':
        state = load_state(args.state)
        state['lastRunAt'] = iso_now()
        save_state(args.state, state)
        print(json.dumps({'ok': True, 'lastRunAt': state['lastRunAt']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
