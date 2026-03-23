#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone


COOLDOWN_HOURS_BY_ACTION = {
    'try_now': 20,
    'adopt_candidate': 20,
    'follow': 30,
    'official_anchor': 12,
    'deep_dive': 36,
    'risk_watch': 24,
    'ignore_for_now': 72,
}

REFRESH_ITEM_LIMIT = 6


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None


def as_utc_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def normalize_key(value: str | None) -> str:
    cleaned = re.sub(r'\s+', ' ', value or '').strip().lower()
    cleaned = cleaned.replace('`', '')
    return re.sub(r'[^\w:/._-]+', '-', cleaned, flags=re.UNICODE).strip('-')


def fingerprint(*parts: str) -> str:
    normalized = [normalize_key(part) for part in parts if normalize_key(part)]
    if not normalized:
        return ''
    joined = '|'.join(normalized)
    digest = hashlib.sha1(joined.encode('utf-8')).hexdigest()[:12]
    return f'fp:{digest}'


def derive_adoption_state(action: str) -> str:
    mapping = {
        'try_now': 'queued-to-try',
        'adopt_candidate': 'adopt-candidate',
        'follow': 'watching',
        'official_anchor': 'baseline',
        'deep_dive': 'follow-up-needed',
        'risk_watch': 'risk-observing',
        'ignore_for_now': 'ignored-for-now',
    }
    return mapping.get(action, 'watching')


def derive_event_key(candidate: dict) -> str:
    x_signal = candidate.get('x_signal') or {}
    stable = ((candidate.get('evidence_lanes') or {}).get('stable') or [])
    primary_stable = stable[0].get('url', '') if stable else ''
    return fingerprint(
        candidate.get('canonical_id', ''),
        candidate.get('raw_reason', ''),
        (candidate.get('freshness') or {}).get('status', ''),
        primary_stable,
        x_signal.get('canonical_url', ''),
        'repeat-convergence' if x_signal.get('repeat_convergence') else '',
        'risk-note' if x_signal.get('risk_note') else '',
    ) or normalize_key(candidate.get('canonical_id', ''))


def derive_angle_key(candidate: dict) -> str:
    return fingerprint(
        candidate.get('canonical_id', ''),
        candidate.get('recommended_action', ''),
        candidate.get('target_audience', ''),
        candidate.get('recommended_action_reason', ''),
        candidate.get('why_now', ''),
    ) or normalize_key(candidate.get('canonical_id', ''))


def derive_cooldown_hours(candidate: dict) -> int:
    action = candidate.get('recommended_action') or 'follow'
    hours = COOLDOWN_HOURS_BY_ACTION.get(action, 24)
    if candidate.get('changed_today'):
        hours = max(12, hours - 6)
    if candidate.get('queue') == 'official_anchors':
        hours = min(hours, 12)
    return hours


def bump_counter(previous: dict, now: datetime, field: str, days: int) -> int:
    previous_time = parse_timestamp(previous.get('last_recommended_at'))
    if not previous_time:
        return 1
    if now - previous_time <= timedelta(days=days):
        return int(previous.get(field) or 0) + 1
    return 1


def memory_index(memory: dict) -> dict:
    return {
        record.get('canonical_id'): record
        for record in (memory.get('records') or [])
        if record.get('canonical_id')
    }


def build_memory_record(candidate: dict, previous: dict, now: datetime, surface: str) -> dict:
    cooldown_until = now + timedelta(hours=derive_cooldown_hours(candidate))
    return {
        'canonical_id': candidate.get('canonical_id'),
        'name': candidate.get('name'),
        'object_type': candidate.get('object_type'),
        'target_audience': candidate.get('target_audience'),
        'recommended_action': candidate.get('recommended_action'),
        'adoption_state': derive_adoption_state(candidate.get('recommended_action', 'follow')),
        'last_seen_at': as_utc_iso(now),
        'last_recommended_at': as_utc_iso(now),
        'last_recommend_reason': candidate.get('why_now', ''),
        'last_recommend_angle': candidate.get('recommended_action_reason', ''),
        'last_event_key': derive_event_key(candidate),
        'last_angle_key': derive_angle_key(candidate),
        'last_queue': candidate.get('queue'),
        'times_recommended_7d': bump_counter(previous, now, 'times_recommended_7d', 7),
        'times_recommended_30d': bump_counter(previous, now, 'times_recommended_30d', 30),
        'suppressed_until': previous.get('suppressed_until'),
        'suppression_reason': previous.get('suppression_reason', ''),
        'cooldown_until': as_utc_iso(cooldown_until),
        'last_serve_score': candidate.get('serve_score'),
        'last_effective_serve_score': candidate.get('serve_score'),
        'last_repeat_penalty': 0,
        'last_served_surface': surface,
    }


def build_memory_snapshot(payload: dict, previous: dict | None = None, surface: str = 'daily-digest') -> dict:
    previous = previous or {}
    now = parse_timestamp(payload.get('generated_at')) or datetime.now(timezone.utc)
    prior_records = memory_index(previous)
    candidates = ((payload.get('feed') or {}).get('candidate_objects') or [])
    seen_ids = set()
    records = []

    for candidate in candidates:
        canonical_id = candidate.get('canonical_id')
        if not canonical_id:
            continue
        seen_ids.add(canonical_id)
        records.append(build_memory_record(candidate, prior_records.get(canonical_id, {}), now, surface))

    for canonical_id, record in prior_records.items():
        if canonical_id not in seen_ids:
            carried = copy.deepcopy(record)
            carried['last_seen_at'] = carried.get('last_seen_at') or as_utc_iso(now)
            records.append(carried)

    records.sort(
        key=lambda record: (
            -(record.get('last_effective_serve_score') or record.get('last_serve_score') or 0),
            record.get('canonical_id', ''),
        )
    )
    return {
        'title': 'evolution-recommendation-memory-v1',
        'generated_at': as_utc_iso(now),
        'source_payload': payload.get('title'),
        'record_count': len(records),
        'records': records,
    }


def apply_repeat_gating(candidate: dict, previous: dict, now: datetime) -> dict:
    decision = copy.deepcopy(candidate)
    serving = {}
    last_recommended_at = parse_timestamp(previous.get('last_recommended_at'))
    explicit_suppressed_until = parse_timestamp(previous.get('suppressed_until'))
    stored_cooldown_until = parse_timestamp(previous.get('cooldown_until'))
    cooldown_hours = derive_cooldown_hours(candidate)
    cooldown_until = stored_cooldown_until
    if cooldown_until is None and last_recommended_at is not None:
        cooldown_until = last_recommended_at + timedelta(hours=cooldown_hours)

    event_key = derive_event_key(candidate)
    angle_key = derive_angle_key(candidate)
    same_event = bool(previous) and previous.get('last_event_key') == event_key and bool(event_key)
    same_angle = bool(previous) and previous.get('last_angle_key') == angle_key and bool(angle_key)
    cooldown_active = cooldown_until is not None and cooldown_until > now
    manual_suppression_active = explicit_suppressed_until is not None and explicit_suppressed_until > now

    times_recommended_7d = int(previous.get('times_recommended_7d') or 0)
    times_recommended_30d = int(previous.get('times_recommended_30d') or 0)

    repeat_penalty = 0
    if times_recommended_7d > 0:
        repeat_penalty += min(4, max(0, times_recommended_7d - 1))
    if times_recommended_30d >= 4:
        repeat_penalty += 1
    if cooldown_active:
        repeat_penalty += 2
    if same_event:
        repeat_penalty += 3
    if same_angle:
        repeat_penalty += 2

    fresh_override = bool(candidate.get('changed_today')) or int(candidate.get('why_now_score') or 0) >= 5
    if fresh_override:
        repeat_penalty = min(repeat_penalty, 2)
    serve_bucket = 'visible'
    serveable = True
    suppression_reason = ''
    next_suppressed_until = explicit_suppressed_until

    if manual_suppression_active and not fresh_override:
        serveable = False
        serve_bucket = 'suppressed'
        suppression_reason = previous.get('suppression_reason') or 'manual-suppression'
    elif cooldown_active and same_event and same_angle and not fresh_override:
        serveable = False
        serve_bucket = 'suppressed'
        suppression_reason = 'cooldown:same-event+same-angle'
        next_suppressed_until = cooldown_until
    elif cooldown_active and same_event and not fresh_override:
        serve_bucket = 'deprioritized'
        repeat_penalty += 1
        suppression_reason = 'cooldown:same-event'
    elif same_angle and not fresh_override:
        serve_bucket = 'deprioritized'
        suppression_reason = 'repeat-angle'

    base_serve_score = int(candidate.get('serve_score') or 0)
    effective_serve_score = base_serve_score - repeat_penalty
    if not serveable:
        effective_serve_score -= 100

    if not next_suppressed_until and cooldown_until and serve_bucket != 'visible':
        next_suppressed_until = cooldown_until

    serving.update(
        {
            'surface': 'refresh',
            'base_serve_score': base_serve_score,
            'effective_serve_score': effective_serve_score,
            'repeat_penalty': repeat_penalty,
            'cooldown_hours': cooldown_hours,
            'cooldown_active': cooldown_active,
            'manual_suppression_active': manual_suppression_active,
            'same_event': same_event,
            'same_angle': same_angle,
            'fresh_override': fresh_override,
            'event_key': event_key,
            'angle_key': angle_key,
            'serve_bucket': serve_bucket,
            'serveable': serveable,
            'suppressed_until': as_utc_iso(next_suppressed_until) if next_suppressed_until else None,
            'suppression_reason': suppression_reason,
        }
    )
    decision['serving'] = serving
    return decision


def sort_refresh_candidates(candidates: list[dict]) -> list[dict]:
    return sorted(
        candidates,
        key=lambda item: (
            0 if (item.get('serving') or {}).get('serveable') else 1,
            -((item.get('serving') or {}).get('effective_serve_score') or 0),
            -int(item.get('serve_score') or 0),
            item.get('name', '').lower(),
        ),
    )


def build_refresh_card(candidate: dict, rank: int) -> dict:
    serving = candidate.get('serving') or {}
    return {
        'rank': rank,
        'canonical_id': candidate.get('canonical_id'),
        'name': candidate.get('name'),
        'queue': candidate.get('queue'),
        'target_audience': candidate.get('target_audience'),
        'target_audience_label': candidate.get('target_audience_label'),
        'recommended_action': candidate.get('recommended_action'),
        'recommended_action_label': candidate.get('recommended_action_label'),
        'why_now': candidate.get('why_now', ''),
        'recommended_action_reason': candidate.get('recommended_action_reason', ''),
        'evidence_summary': candidate.get('evidence_summary', {}),
        'base_serve_score': serving.get('base_serve_score', candidate.get('serve_score', 0)),
        'effective_serve_score': serving.get('effective_serve_score', candidate.get('serve_score', 0)),
        'repeat_penalty': serving.get('repeat_penalty', 0),
        'cooldown_active': serving.get('cooldown_active', False),
        'same_event': serving.get('same_event', False),
        'same_angle': serving.get('same_angle', False),
        'fresh_override': serving.get('fresh_override', False),
        'suppressed_until': serving.get('suppressed_until'),
        'suppression_reason': serving.get('suppression_reason', ''),
        'links': candidate.get('links', []),
    }


def update_memory_with_refresh(memory: dict, candidates: list[dict], selected_ids: set[str], now: datetime) -> dict:
    prior_records = memory_index(memory)
    seen_ids = set()
    records = []

    for candidate in candidates:
        canonical_id = candidate.get('canonical_id')
        if not canonical_id:
            continue
        seen_ids.add(canonical_id)
        previous = prior_records.get(canonical_id, {})
        serving = candidate.get('serving') or {}
        selected = canonical_id in selected_ids
        record = copy.deepcopy(previous) if previous else {}

        record.update(
            {
                'canonical_id': canonical_id,
                'name': candidate.get('name'),
                'object_type': candidate.get('object_type'),
                'target_audience': candidate.get('target_audience'),
                'recommended_action': candidate.get('recommended_action'),
                'adoption_state': derive_adoption_state(candidate.get('recommended_action', 'follow')),
                'last_seen_at': as_utc_iso(now),
                'last_event_key': serving.get('event_key', derive_event_key(candidate)),
                'last_angle_key': serving.get('angle_key', derive_angle_key(candidate)),
                'last_queue': candidate.get('queue'),
                'last_serve_score': candidate.get('serve_score'),
                'last_effective_serve_score': serving.get('effective_serve_score', candidate.get('serve_score')),
                'last_repeat_penalty': serving.get('repeat_penalty', 0),
                'last_served_surface': 'refresh' if selected else record.get('last_served_surface', 'daily-digest'),
            }
        )

        if selected:
            cooldown_until = now + timedelta(hours=derive_cooldown_hours(candidate))
            record.update(
                {
                    'last_recommended_at': as_utc_iso(now),
                    'last_recommend_reason': candidate.get('why_now', ''),
                    'last_recommend_angle': candidate.get('recommended_action_reason', ''),
                    'times_recommended_7d': bump_counter(previous, now, 'times_recommended_7d', 7),
                    'times_recommended_30d': bump_counter(previous, now, 'times_recommended_30d', 30),
                    'cooldown_until': as_utc_iso(cooldown_until),
                    'suppressed_until': as_utc_iso(cooldown_until),
                    'suppression_reason': 'refresh-cooldown',
                }
            )
        else:
            if serving.get('suppressed_until'):
                record['suppressed_until'] = serving.get('suppressed_until')
            if serving.get('suppression_reason'):
                record['suppression_reason'] = serving.get('suppression_reason')
            record['times_recommended_7d'] = int(record.get('times_recommended_7d') or 0)
            record['times_recommended_30d'] = int(record.get('times_recommended_30d') or 0)

        records.append(record)

    for canonical_id, previous in prior_records.items():
        if canonical_id in seen_ids:
            continue
        records.append(copy.deepcopy(previous))

    records.sort(
        key=lambda record: (
            -(record.get('last_effective_serve_score') or record.get('last_serve_score') or 0),
            record.get('canonical_id', ''),
        )
    )
    return {
        'title': 'evolution-recommendation-memory-v1',
        'generated_at': as_utc_iso(now),
        'source_payload': memory.get('source_payload'),
        'record_count': len(records),
        'records': records,
    }


def build_refresh_feed(payload: dict, memory: dict, item_limit: int = REFRESH_ITEM_LIMIT) -> tuple[dict, dict]:
    now = parse_timestamp(payload.get('generated_at')) or datetime.now(timezone.utc)
    candidates = ((payload.get('feed') or {}).get('candidate_objects') or [])
    prior_records = memory_index(memory)
    ranked_candidates = sort_refresh_candidates(
        [apply_repeat_gating(candidate, prior_records.get(candidate.get('canonical_id'), {}), now) for candidate in candidates]
    )

    visible = [candidate for candidate in ranked_candidates if (candidate.get('serving') or {}).get('serveable')]
    selected = visible[:item_limit]
    selected_ids = {candidate.get('canonical_id') for candidate in selected if candidate.get('canonical_id')}
    suppressed = [candidate for candidate in ranked_candidates if not (candidate.get('serving') or {}).get('serveable')]
    gated = [candidate for candidate in ranked_candidates if (candidate.get('serving') or {}).get('repeat_penalty', 0) > 0]

    feed = {
        'title': 'evolution-refresh-feed-v1',
        'generated_at': as_utc_iso(now),
        'source_payload': payload.get('title'),
        'memory_title': memory.get('title'),
        'surface': 'refresh',
        'policy': {
            'anti_repeat': ['cooldown', 'repeat_penalty', 'suppressed_until', 'event_gating', 'angle_gating'],
            'sort_key': 'effective_serve_score',
            'item_limit': item_limit,
        },
        'summary': {
            'candidate_count': len(candidates),
            'visible_count': len(visible),
            'selected_count': len(selected),
            'suppressed_count': len(suppressed),
            'gated_count': len(gated),
            'selected_names': [candidate.get('name') for candidate in selected],
            'suppressed_names': [candidate.get('name') for candidate in suppressed],
        },
        'items': [build_refresh_card(candidate, index) for index, candidate in enumerate(selected, start=1)],
        'suppressed_items': [
            {
                'canonical_id': candidate.get('canonical_id'),
                'name': candidate.get('name'),
                'queue': candidate.get('queue'),
                'base_serve_score': (candidate.get('serving') or {}).get('base_serve_score', candidate.get('serve_score')),
                'effective_serve_score': (candidate.get('serving') or {}).get('effective_serve_score', candidate.get('serve_score')),
                'repeat_penalty': (candidate.get('serving') or {}).get('repeat_penalty', 0),
                'suppressed_until': (candidate.get('serving') or {}).get('suppressed_until'),
                'suppression_reason': (candidate.get('serving') or {}).get('suppression_reason', ''),
                'same_event': (candidate.get('serving') or {}).get('same_event', False),
                'same_angle': (candidate.get('serving') or {}).get('same_angle', False),
            }
            for candidate in suppressed
        ],
    }
    updated_memory = update_memory_with_refresh(memory, ranked_candidates, selected_ids, now)
    updated_memory['source_payload'] = payload.get('title')
    return feed, updated_memory


def dumps_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)
