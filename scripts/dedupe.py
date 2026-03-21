#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone


def parse_iso(v):
    if not v:
        return None
    try:
        return datetime.fromisoformat(v.replace('Z', '+00:00'))
    except Exception:
        return None


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def stable_key(item):
    if item.get('id'):
        return f"id:{item['id']}"
    if item.get('link'):
        return f"link:{item['link']}"
    raw = f"{item.get('title','')}|{item.get('published','')}"
    return 'hash:' + hashlib.sha256(raw.encode('utf-8')).hexdigest()


def text_match(text, words):
    text = (text or '').lower()
    return any(str(w).lower() in text for w in words)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--items', required=True)
    ap.add_argument('--state', required=True)
    ap.add_argument('--window-hours', type=int, default=24)
    ap.add_argument('--write-state', action='store_true')
    args = ap.parse_args()

    data = load_json(args.items)
    items = data.get('items', [])
    state = load_json(args.state) if os.path.exists(args.state) else {
        'version': 1,
        'lastRunAt': None,
        'seen': {},
        'feedHealth': {},
    }

    cutoff = datetime.now(timezone.utc) - timedelta(hours=args.window_hours)
    local_seen = set()
    new_items = []
    skipped_seen = 0
    skipped_duplicate = 0
    skipped_filtered = 0

    for item in items:
        feed_id = item.get('feed_id') or 'unknown'
        key = stable_key(item)
        title_summary = f"{item.get('title','')}\n{item.get('summary','')}"
        pub = parse_iso(item.get('published'))
        if pub and pub < cutoff:
            skipped_filtered += 1
            continue
        include = item.get('include') or []
        exclude = item.get('exclude') or []
        if exclude and text_match(title_summary, exclude):
            skipped_filtered += 1
            continue
        if include and not text_match(title_summary, include):
            skipped_filtered += 1
            continue
        if key in local_seen:
            skipped_duplicate += 1
            continue
        if key in set(state.get('seen', {}).get(feed_id, [])):
            skipped_seen += 1
            continue
        local_seen.add(key)
        item['_dedupe_key'] = key
        new_items.append(item)

    if args.write_state:
        for item in new_items:
            feed_id = item.get('feed_id') or 'unknown'
            state.setdefault('seen', {}).setdefault(feed_id, []).append(item['_dedupe_key'])
            state['seen'][feed_id] = state['seen'][feed_id][-500:]
        for fh in data.get('feed_health', []):
            state.setdefault('feedHealth', {})[fh['feed_id']] = fh
        state['lastRunAt'] = data.get('generated_at')
        os.makedirs(os.path.dirname(args.state), exist_ok=True)
        with open(args.state, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    print(json.dumps({
        'ok': True,
        'new_items': new_items,
        'counts': {
            'new': len(new_items),
            'skipped_seen': skipped_seen,
            'skipped_duplicate': skipped_duplicate,
            'skipped_filtered': skipped_filtered,
        }
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
