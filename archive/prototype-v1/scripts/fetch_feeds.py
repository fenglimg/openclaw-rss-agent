#!/usr/bin/env python3
import argparse
import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape

import requests
import yaml


TAG_RE = re.compile(r'<[^>]+>')
WS_RE = re.compile(r'\s+')


def iso_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def to_iso(dt):
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def parse_date(value):
    if not value:
        return None
    value = str(value).strip()
    for fn in (
        lambda v: parsedate_to_datetime(v),
        lambda v: datetime.fromisoformat(v.replace('Z', '+00:00')),
    ):
        try:
            return fn(value)
        except Exception:
            pass
    return None


def clean_html(text):
    if not text:
        return None
    text = unescape(text)
    text = TAG_RE.sub(' ', text)
    text = WS_RE.sub(' ', text).strip()
    return text or None


def text_of(node, path, ns=None):
    found = node.find(path, ns or {})
    if found is not None and found.text:
        return found.text.strip()
    return None


def collect_feed_entries(xml_text):
    root = ET.fromstring(xml_text)
    tag = root.tag.lower()
    entries = []
    if tag.endswith('rss') or tag.endswith('rdf'):
        channel = root.find('channel') if root.find('channel') is not None else root
        for item in channel.findall('.//item'):
            title = text_of(item, 'title')
            link = text_of(item, 'link')
            guid = text_of(item, 'guid')
            pub = text_of(item, 'pubDate') or text_of(item, 'date')
            summary = text_of(item, 'description') or text_of(item, 'summary')
            entries.append({
                'id': guid or link or title,
                'title': clean_html(title),
                'link': clean_html(link),
                'published': to_iso(parse_date(pub)) if pub else None,
                'summary': clean_html(summary),
            })
        return entries

    ns = {
        'atom': 'http://www.w3.org/2005/Atom',
        'content': 'http://purl.org/rss/1.0/modules/content/',
    }
    for entry in root.findall('atom:entry', ns):
        title = text_of(entry, 'atom:title', ns)
        link = None
        for ln in entry.findall('atom:link', ns):
            href = ln.attrib.get('href')
            rel = ln.attrib.get('rel', 'alternate')
            if href and rel == 'alternate':
                link = href
                break
            if href and not link:
                link = href
        entry_id = text_of(entry, 'atom:id', ns) or link or title
        pub = text_of(entry, 'atom:published', ns) or text_of(entry, 'atom:updated', ns)
        summary = text_of(entry, 'atom:summary', ns) or text_of(entry, 'atom:content', ns)
        entries.append({
            'id': clean_html(entry_id),
            'title': clean_html(title),
            'link': clean_html(link),
            'published': to_iso(parse_date(pub)) if pub else None,
            'summary': clean_html(summary),
        })
    return entries


def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    return data.get('feeds', [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    ap.add_argument('--limit-per-feed', type=int, default=10)
    ap.add_argument('--timeout', type=int, default=20)
    args = ap.parse_args()

    feeds = load_config(args.config)
    session = requests.Session()
    session.headers.update({'User-Agent': 'openclaw-rss-agent/0.1'})

    all_items = []
    feed_health = []

    for feed in feeds:
        if not feed.get('enabled', True):
            continue
        url = feed.get('url')
        feed_id = feed.get('id')
        feed_name = feed.get('name') or feed_id or url
        started = time.time()
        try:
            resp = session.get(url, timeout=args.timeout)
            resp.raise_for_status()
            entries = collect_feed_entries(resp.text)[: args.limit_per_feed]
            for item in entries:
                all_items.append({
                    'feed_id': feed_id,
                    'feed_name': feed_name,
                    'feed_url': url,
                    'tags': feed.get('tags', []),
                    'source_role': feed.get('source_role'),
                    'language': feed.get('language'),
                    'triage_mode': feed.get('triage_mode'),
                    'include': feed.get('include', []),
                    'exclude': feed.get('exclude', []),
                    'boost_keywords': feed.get('boost_keywords', []),
                    'suppress_keywords': feed.get('suppress_keywords', []),
                    'priority_topics': feed.get('priority_topics', []),
                    **item,
                })
            feed_health.append({
                'feed_id': feed_id,
                'feed_name': feed_name,
                'ok': True,
                'url': url,
                'status_code': resp.status_code,
                'items_fetched': len(entries),
                'fetched_at': iso_now(),
                'latency_ms': int((time.time() - started) * 1000),
            })
        except Exception as e:
            feed_health.append({
                'feed_id': feed_id,
                'feed_name': feed_name,
                'ok': False,
                'url': url,
                'error': str(e),
                'fetched_at': iso_now(),
                'latency_ms': int((time.time() - started) * 1000),
            })

    print(json.dumps({
        'ok': True,
        'generated_at': iso_now(),
        'count': len(all_items),
        'items': all_items,
        'feed_health': feed_health,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
