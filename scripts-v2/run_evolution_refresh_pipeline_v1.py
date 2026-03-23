#!/usr/bin/env python3
import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
CURRENT_DIR = SCRIPT_PATH.parent
REPO_ROOT = CURRENT_DIR.parent

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import build_daily_payload_v2 as payload_builder
import build_recommendation_memory_v1 as memory_builder
import recommendation_serving_v1 as serving
import render_evolution_refresh_feed_v1 as refresh_renderer


PAYLOAD = REPO_ROOT / 'test-output/evolution-refresh-payload-v1.json'
PRE_SERVE_MEMORY = REPO_ROOT / 'test-output/evolution-recommendation-memory-pre-serve-v1.json'
POST_SERVE_MEMORY = REPO_ROOT / 'test-output/evolution-recommendation-memory-post-serve-v1.json'
CURRENT_STATE = REPO_ROOT / 'test-output/evolution-recommendation-memory-current-state-v1.json'
REFRESH_FEED = REPO_ROOT / 'test-output/evolution-refresh-feed-automation-v1.json'
REFRESH_REPORT = REPO_ROOT / 'outputs/evolution-refresh-feed-automation-v1.md'
RUN_MANIFEST = REPO_ROOT / 'test-output/evolution-refresh-run-v1.json'
REVIEW = REPO_ROOT / 'outputs/evolution-refresh-review-v1.md'
REVIEW_NOTE_SCRIPT = CURRENT_DIR / 'send_discord_review_note_v1.py'
REVIEW_NOTE_OUTPUT = REPO_ROOT / 'test-output/discord-review-note-evolution-refresh-v1.json'
REVIEW_NOTE_CHANNEL_ID = '1484951098660753558'
RUN_MODES = ('review', 'silent')
STDOUT_FORMATS = ('summary', 'manifest')


def parse_args():
    parser = argparse.ArgumentParser(
        description='Run the automation-ready evolution refresh pipeline with stable repo-root defaults.'
    )
    parser.add_argument('--payload', default=str(PAYLOAD))
    parser.add_argument('--pre-serve-memory', default=str(PRE_SERVE_MEMORY))
    parser.add_argument('--post-serve-memory', default=str(POST_SERVE_MEMORY))
    parser.add_argument('--current-state', default=str(CURRENT_STATE))
    parser.add_argument('--refresh-feed', default=str(REFRESH_FEED))
    parser.add_argument('--refresh-report', default=str(REFRESH_REPORT))
    parser.add_argument('--run-manifest', default=str(RUN_MANIFEST))
    parser.add_argument('--review', default=str(REVIEW))
    parser.add_argument('--item-limit', type=int, default=serving.REFRESH_ITEM_LIMIT)
    parser.add_argument('--surface', default='refresh')
    parser.add_argument('--mode', choices=RUN_MODES, default='review')
    parser.add_argument('--stdout-format', choices=STDOUT_FORMATS, default='summary')
    parser.add_argument('--skip-payload-build', action='store_true')
    parser.add_argument('--notify-review-ready', action='store_true')
    parser.add_argument('--review-note-script', default=str(REVIEW_NOTE_SCRIPT))
    parser.add_argument('--review-note-output', default=str(REVIEW_NOTE_OUTPUT))
    parser.add_argument('--channel-id', default=REVIEW_NOTE_CHANNEL_ID)
    parser.add_argument('--task-name', default='Phase 4 unified refresh runner')
    parser.add_argument('--tests-status', default='not-run')
    parser.add_argument('--recommend-review', choices=['auto', 'yes', 'no'], default='auto')
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def to_repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())


def ensure_parent(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return {}


def dumps_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def write_json(path: Path, data: dict):
    ensure_parent(path)
    path.write_text(dumps_json(data), encoding='utf-8')


def build_payload_snapshot() -> dict:
    return payload_builder.build_payload(
        payload_builder.read(payload_builder.APPLIED),
        payload_builder.read(payload_builder.OPENCLAW),
        payload_builder.build_x_signal_lane(),
    )


def resolve_run_status(run_mode: str) -> str:
    return 'review-ready' if run_mode == 'review' else 'succeeded'


def should_send_review_ready_note(run_mode: str, notify_review_ready: bool) -> bool:
    return run_mode == 'review' and notify_review_ready


def resolve_recommend_review(run_mode: str, value: str) -> str:
    if value in ('yes', 'no'):
        return value
    return 'yes' if run_mode == 'review' else 'no'


def normalize_memory_state(
    memory: dict,
    *,
    title: str,
    lifecycle_stage: str,
    surface: str,
    payload_path: str,
    payload_title: str,
    previous_state_path: str | None = None,
    previous_state_title: str | None = None,
    incoming_state_path: str | None = None,
    incoming_state_title: str | None = None,
    incoming_state_stage: str | None = None,
) -> dict:
    artifact = copy.deepcopy(memory)
    artifact.pop('source_payload', None)
    artifact['title'] = title
    artifact['schema_version'] = 'evolution-recommendation-memory-v1'
    artifact['artifact_role'] = 'recommendation-state'
    artifact['lifecycle_stage'] = lifecycle_stage
    artifact['surface'] = surface
    artifact['record_count'] = len(artifact.get('records') or [])
    artifact['inputs'] = {
        'payload': {
            'title': payload_title,
            'path': payload_path,
        }
    }
    if previous_state_path or previous_state_title:
        artifact['inputs']['previous_current_state'] = {
            'title': previous_state_title or '',
            'path': previous_state_path or '',
            'lifecycle_stage': 'current-state',
        }
    if incoming_state_path or incoming_state_title or incoming_state_stage:
        artifact['inputs']['recommendation_state_in'] = {
            'title': incoming_state_title or '',
            'path': incoming_state_path or '',
            'lifecycle_stage': incoming_state_stage or '',
        }
    artifact['producer'] = {
        'script': 'scripts-v2/run_evolution_refresh_pipeline_v1.py',
        'mode': 'automation-ready',
    }
    return artifact


def normalize_refresh_feed(
    refresh_feed: dict,
    *,
    payload_path: str,
    payload_title: str,
    pre_serve_memory_path: str,
    pre_serve_memory_title: str,
    post_serve_memory_path: str,
    post_serve_memory_title: str,
    surface: str,
) -> dict:
    artifact = copy.deepcopy(refresh_feed)
    artifact.pop('source_payload', None)
    artifact.pop('memory_title', None)
    artifact['title'] = 'evolution-refresh-feed-automation-v1'
    artifact['artifact_role'] = 'refresh-feed'
    artifact['surface'] = surface
    artifact['inputs'] = {
        'payload': {
            'title': payload_title,
            'path': payload_path,
        },
        'recommendation_state_in': {
            'title': pre_serve_memory_title,
            'path': pre_serve_memory_path,
            'lifecycle_stage': 'pre-serve',
        },
    }
    artifact['outputs'] = {
        'recommendation_state_out': {
            'title': post_serve_memory_title,
            'path': post_serve_memory_path,
            'lifecycle_stage': 'post-serve',
        }
    }
    artifact['producer'] = {
        'script': 'scripts-v2/run_evolution_refresh_pipeline_v1.py',
        'mode': 'automation-ready',
    }
    return artifact


def build_review_markdown(run_manifest: dict) -> str:
    summary = run_manifest.get('summary') or {}
    artifacts = run_manifest.get('artifacts') or {}
    execution = run_manifest.get('execution') or {}
    lines = [
        '# Evolution Refresh Runner Review',
        '',
        (
            f"> status: {run_manifest.get('status', 'unknown')}"
            f" | mode {execution.get('mode', 'unknown')}"
            f" | payload candidates {summary.get('candidate_count', 0)}"
            f" | selected {summary.get('selected_count', 0)}"
            f" | suppressed {summary.get('suppressed_count', 0)}"
        ),
        '',
        '## Run Control',
        '',
        f"- payload strategy: `{execution.get('payload_strategy', 'unknown')}`",
        f"- item limit: `{execution.get('item_limit', 0)}`",
        f"- review-ready note requested: `{execution.get('review_ready_note_requested', False)}`",
        f"- tests status: `{execution.get('tests_status', 'not-run')}`",
        f"- recommend immediate review: `{execution.get('recommend_review', 'no')}`",
        '',
        '## Automation Artifacts',
        '',
        f"- payload snapshot: `{artifacts.get('payload', '')}`",
        f"- recommendation state (pre-serve): `{artifacts.get('pre_serve_memory', '')}`",
        f"- recommendation state (post-serve): `{artifacts.get('post_serve_memory', '')}`",
        f"- recommendation state (current-state): `{artifacts.get('current_state', '')}`",
        f"- refresh feed: `{artifacts.get('refresh_feed', '')}`",
        f"- refresh markdown: `{artifacts.get('refresh_report', '')}`",
        f"- run manifest: `{artifacts.get('run_manifest', '')}`",
        f"- review note output: `{artifacts.get('review_note', '')}`",
        '',
        '## Review Focus',
        '',
        '- refresh runner is now a single automation-ready entrypoint',
        '- refresh metadata uses payload/state inputs+outputs instead of legacy source_payload naming',
        '- recommendation memory semantics are explicit: pre-serve / post-serve / current-state',
        '- paths resolve from repo root so cron can call the script from any cwd',
        '',
        '## Selected Items',
        '',
    ]
    for name in summary.get('selected_names', []):
        lines.append(f'- {name}')
    lines.extend(['', '## Suppressed Items', ''])
    for name in summary.get('suppressed_names', []):
        lines.append(f'- {name}')
    return '\n'.join(lines).strip() + '\n'


def build_run_manifest(
    *,
    payload: dict,
    payload_path: str,
    pre_serve_memory: dict,
    post_serve_memory: dict,
    current_state: dict,
    refresh_feed: dict,
    refresh_report_path: str,
    run_manifest_path: str,
    review_path: str,
    pre_serve_memory_path: str,
    post_serve_memory_path: str,
    current_state_path: str,
    refresh_feed_path: str,
    run_mode: str = 'review',
    payload_strategy: str = 'rebuild',
    notify_review_ready: bool = False,
    review_note_output_path: str = '',
    tests_status: str = 'not-run',
    recommend_review: str = 'yes',
) -> dict:
    summary = refresh_feed.get('summary') or {}
    return {
        'title': 'evolution-refresh-run-v1',
        'status': resolve_run_status(run_mode),
        'generated_at': refresh_feed.get('generated_at') or payload.get('generated_at'),
        'runner': 'scripts-v2/run_evolution_refresh_pipeline_v1.py',
        'mode': 'automation-ready',
        'surface': refresh_feed.get('surface', 'refresh'),
        'execution': {
            'mode': run_mode,
            'payload_strategy': payload_strategy,
            'item_limit': ((refresh_feed.get('policy') or {}).get('item_limit') or 0),
            'review_ready_note_requested': notify_review_ready,
            'tests_status': tests_status,
            'recommend_review': recommend_review,
        },
        'inputs': {
            'payload': {
                'title': payload.get('title', ''),
                'path': payload_path,
            },
            'recommendation_state_in': {
                'title': pre_serve_memory.get('title', ''),
                'path': pre_serve_memory_path,
                'lifecycle_stage': pre_serve_memory.get('lifecycle_stage', ''),
            },
        },
        'outputs': {
            'recommendation_state_out': {
                'title': post_serve_memory.get('title', ''),
                'path': post_serve_memory_path,
                'lifecycle_stage': post_serve_memory.get('lifecycle_stage', ''),
            },
            'recommendation_current_state': {
                'title': current_state.get('title', ''),
                'path': current_state_path,
                'lifecycle_stage': current_state.get('lifecycle_stage', ''),
            },
            'refresh_feed': {
                'title': refresh_feed.get('title', ''),
                'path': refresh_feed_path,
            },
        },
        'summary': {
            'candidate_count': summary.get('candidate_count', 0),
            'selected_count': summary.get('selected_count', 0),
            'suppressed_count': summary.get('suppressed_count', 0),
            'selected_names': summary.get('selected_names', []),
            'suppressed_names': summary.get('suppressed_names', []),
        },
        'artifacts': {
            'payload': payload_path,
            'pre_serve_memory': pre_serve_memory_path,
            'post_serve_memory': post_serve_memory_path,
            'current_state': current_state_path,
            'refresh_feed': refresh_feed_path,
            'refresh_report': refresh_report_path,
            'run_manifest': run_manifest_path,
            'review': review_path,
            'review_note': review_note_output_path,
        },
    }


def build_refresh_pipeline_artifacts(
    payload: dict,
    *,
    previous_current_state: dict | None = None,
    payload_path: str,
    pre_serve_memory_path: str,
    post_serve_memory_path: str,
    current_state_path: str,
    refresh_feed_path: str,
    refresh_report_path: str,
    run_manifest_path: str,
    review_path: str,
    item_limit: int = serving.REFRESH_ITEM_LIMIT,
    surface: str = 'refresh',
    run_mode: str = 'review',
    payload_strategy: str = 'rebuild',
    notify_review_ready: bool = False,
    review_note_output_path: str = '',
    tests_status: str = 'not-run',
    recommend_review: str = 'yes',
) -> dict:
    previous_current_state = previous_current_state or {}
    payload_title = payload.get('title', '')

    pre_serve_memory_raw = memory_builder.build_memory(payload, previous_current_state)
    pre_serve_memory = normalize_memory_state(
        pre_serve_memory_raw,
        title='evolution-recommendation-memory-pre-serve-v1',
        lifecycle_stage='pre-serve',
        surface=surface,
        payload_path=payload_path,
        payload_title=payload_title,
        previous_state_path=current_state_path if previous_current_state else None,
        previous_state_title=previous_current_state.get('title') if previous_current_state else None,
    )

    refresh_feed_raw, post_serve_memory_raw = serving.build_refresh_feed(payload, pre_serve_memory_raw, item_limit=item_limit)
    post_serve_memory = normalize_memory_state(
        post_serve_memory_raw,
        title='evolution-recommendation-memory-post-serve-v1',
        lifecycle_stage='post-serve',
        surface=surface,
        payload_path=payload_path,
        payload_title=payload_title,
        incoming_state_path=pre_serve_memory_path,
        incoming_state_title='evolution-recommendation-memory-pre-serve-v1',
        incoming_state_stage='pre-serve',
    )
    current_state = normalize_memory_state(
        post_serve_memory_raw,
        title='evolution-recommendation-memory-current-state-v1',
        lifecycle_stage='current-state',
        surface=surface,
        payload_path=payload_path,
        payload_title=payload_title,
        incoming_state_path=post_serve_memory_path,
        incoming_state_title='evolution-recommendation-memory-post-serve-v1',
        incoming_state_stage='post-serve',
    )
    refresh_feed = normalize_refresh_feed(
        refresh_feed_raw,
        payload_path=payload_path,
        payload_title=payload_title,
        pre_serve_memory_path=pre_serve_memory_path,
        pre_serve_memory_title='evolution-recommendation-memory-pre-serve-v1',
        post_serve_memory_path=post_serve_memory_path,
        post_serve_memory_title='evolution-recommendation-memory-post-serve-v1',
        surface=surface,
    )
    run_manifest = build_run_manifest(
        payload=payload,
        payload_path=payload_path,
        pre_serve_memory=pre_serve_memory,
        post_serve_memory=post_serve_memory,
        current_state=current_state,
        refresh_feed=refresh_feed,
        refresh_report_path=refresh_report_path,
        run_manifest_path=run_manifest_path,
        review_path=review_path,
        pre_serve_memory_path=pre_serve_memory_path,
        post_serve_memory_path=post_serve_memory_path,
        current_state_path=current_state_path,
        refresh_feed_path=refresh_feed_path,
        run_mode=run_mode,
        payload_strategy=payload_strategy,
        notify_review_ready=notify_review_ready,
        review_note_output_path=review_note_output_path,
        tests_status=tests_status,
        recommend_review=recommend_review,
    )
    return {
        'payload': payload,
        'pre_serve_memory': pre_serve_memory,
        'post_serve_memory': post_serve_memory,
        'current_state': current_state,
        'refresh_feed': refresh_feed,
        'run_manifest': run_manifest,
        'review_markdown': build_review_markdown(run_manifest),
        'refresh_report_markdown': refresh_renderer.render_report(refresh_feed),
    }


def run_review_note_command(
    *,
    script_path: Path,
    channel_id: str,
    task_name: str,
    status: str,
    tests_status: str,
    artifacts: str,
    recommend_review: str,
    output_path: Path,
) -> dict:
    ensure_parent(output_path)
    command = [
        sys.executable,
        str(script_path),
        '--channel-id',
        channel_id,
        '--task',
        task_name,
        '--status',
        status,
        '--tests',
        tests_status,
        '--artifacts',
        artifacts,
        '--recommend-review',
        recommend_review,
        '--output',
        str(output_path),
    ]
    completed = subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        check=True,
        capture_output=True,
        text=True,
    )
    result = load_json(output_path)
    if result:
        return result
    stdout = completed.stdout.strip()
    if stdout:
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            pass
    return {
        'ok': True,
        'status': 'sent-command-finished',
        'channel_id': channel_id,
        'message': stdout,
    }


def summarize_artifacts_for_note(run_manifest: dict) -> str:
    artifacts = run_manifest.get('artifacts') or {}
    return ', '.join(
        filter(
            None,
            [
                artifacts.get('run_manifest'),
                artifacts.get('refresh_feed'),
                artifacts.get('refresh_report'),
                artifacts.get('review'),
            ],
        )
    )


def build_cli_summary(run_manifest: dict, review_note_result: dict | None = None) -> dict:
    summary = run_manifest.get('summary') or {}
    execution = run_manifest.get('execution') or {}
    result = {
        'ok': True,
        'status': run_manifest.get('status'),
        'mode': execution.get('mode'),
        'item_limit': execution.get('item_limit'),
        'tests_status': execution.get('tests_status'),
        'selected_count': summary.get('selected_count', 0),
        'suppressed_count': summary.get('suppressed_count', 0),
        'selected_names': summary.get('selected_names', []),
        'artifacts': run_manifest.get('artifacts') or {},
    }
    if review_note_result is not None:
        result['review_note'] = {
            'requested': execution.get('review_ready_note_requested', False),
            'status': review_note_result.get('status', 'unknown'),
            'ok': review_note_result.get('ok', False),
            'channel_id': review_note_result.get('channel_id'),
            'message_id': review_note_result.get('message_id'),
        }
    return result


def main():
    args = parse_args()
    payload_path = resolve_path(args.payload)
    pre_serve_memory_path = resolve_path(args.pre_serve_memory)
    post_serve_memory_path = resolve_path(args.post_serve_memory)
    current_state_path = resolve_path(args.current_state)
    refresh_feed_path = resolve_path(args.refresh_feed)
    refresh_report_path = resolve_path(args.refresh_report)
    run_manifest_path = resolve_path(args.run_manifest)
    review_path = resolve_path(args.review)
    review_note_script_path = resolve_path(args.review_note_script)
    review_note_output_path = resolve_path(args.review_note_output)

    payload_ref = to_repo_relative(payload_path)
    pre_serve_memory_ref = to_repo_relative(pre_serve_memory_path)
    post_serve_memory_ref = to_repo_relative(post_serve_memory_path)
    current_state_ref = to_repo_relative(current_state_path)
    refresh_feed_ref = to_repo_relative(refresh_feed_path)
    refresh_report_ref = to_repo_relative(refresh_report_path)
    run_manifest_ref = to_repo_relative(run_manifest_path)
    review_ref = to_repo_relative(review_path)
    review_note_output_ref = to_repo_relative(review_note_output_path)

    previous_current_state = load_json(current_state_path)
    payload_strategy = 'reuse' if args.skip_payload_build and payload_path.exists() else 'rebuild'
    if payload_strategy == 'reuse':
        payload = load_json(payload_path)
    else:
        payload = build_payload_snapshot()
        write_json(payload_path, payload)

    recommend_review = resolve_recommend_review(args.mode, args.recommend_review)
    artifacts = build_refresh_pipeline_artifacts(
        payload,
        previous_current_state=previous_current_state,
        payload_path=payload_ref,
        pre_serve_memory_path=pre_serve_memory_ref,
        post_serve_memory_path=post_serve_memory_ref,
        current_state_path=current_state_ref,
        refresh_feed_path=refresh_feed_ref,
        refresh_report_path=refresh_report_ref,
        run_manifest_path=run_manifest_ref,
        review_path=review_ref,
        item_limit=args.item_limit,
        surface=args.surface,
        run_mode=args.mode,
        payload_strategy=payload_strategy,
        notify_review_ready=args.notify_review_ready,
        review_note_output_path=review_note_output_ref,
        tests_status=args.tests_status,
        recommend_review=recommend_review,
    )

    write_json(pre_serve_memory_path, artifacts['pre_serve_memory'])
    write_json(post_serve_memory_path, artifacts['post_serve_memory'])
    write_json(current_state_path, artifacts['current_state'])
    write_json(refresh_feed_path, artifacts['refresh_feed'])
    ensure_parent(refresh_report_path)
    refresh_report_path.write_text(artifacts['refresh_report_markdown'], encoding='utf-8')
    ensure_parent(review_path)
    review_path.write_text(artifacts['review_markdown'], encoding='utf-8')

    review_note_result = None
    if should_send_review_ready_note(args.mode, args.notify_review_ready):
        review_note_result = run_review_note_command(
            script_path=review_note_script_path,
            channel_id=args.channel_id,
            task_name=args.task_name,
            status=resolve_run_status(args.mode),
            tests_status=args.tests_status,
            artifacts=summarize_artifacts_for_note(artifacts['run_manifest']),
            recommend_review=recommend_review,
            output_path=review_note_output_path,
        )

    if review_note_result is not None:
        artifacts['run_manifest']['review_note'] = {
            'requested': True,
            'output': review_note_output_ref,
            'result': review_note_result,
        }
    else:
        artifacts['run_manifest']['review_note'] = {
            'requested': bool(args.notify_review_ready),
            'output': review_note_output_ref,
            'result': None,
        }

    write_json(run_manifest_path, artifacts['run_manifest'])

    if args.stdout_format == 'manifest':
        print(dumps_json(artifacts['run_manifest']))
        return

    print(dumps_json(build_cli_summary(artifacts['run_manifest'], review_note_result)))


if __name__ == '__main__':
    main()
