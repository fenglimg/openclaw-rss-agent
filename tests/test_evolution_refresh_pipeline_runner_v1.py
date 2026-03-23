import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(relative_path: str, module_name: str):
    module_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


payload_mod = load_module('scripts-v2/build_daily_payload_v2.py', 'build_daily_payload_v2_runner')
runner_mod = load_module('scripts-v2/run_evolution_refresh_pipeline_v1.py', 'run_evolution_refresh_pipeline_v1')


class EvolutionRefreshPipelineRunnerTests(unittest.TestCase):
    def build_payload(self):
        return payload_mod.build_payload(
            payload_mod.read(payload_mod.APPLIED),
            payload_mod.read(payload_mod.OPENCLAW),
            payload_mod.build_x_signal_lane(),
        )

    def build_artifacts(self):
        payload = self.build_payload()
        return runner_mod.build_refresh_pipeline_artifacts(
            payload,
            previous_current_state={},
            payload_path='test-output/evolution-refresh-payload-v1.json',
            pre_serve_memory_path='test-output/evolution-recommendation-memory-pre-serve-v1.json',
            post_serve_memory_path='test-output/evolution-recommendation-memory-post-serve-v1.json',
            current_state_path='test-output/evolution-recommendation-memory-current-state-v1.json',
            refresh_feed_path='test-output/evolution-refresh-feed-automation-v1.json',
            refresh_report_path='outputs/evolution-refresh-feed-automation-v1.md',
            run_manifest_path='test-output/evolution-refresh-run-v1.json',
            review_path='outputs/evolution-refresh-review-v1.md',
            item_limit=4,
        )

    def test_runner_uses_explicit_memory_lifecycle_semantics(self):
        artifacts = self.build_artifacts()

        pre_state = artifacts['pre_serve_memory']
        post_state = artifacts['post_serve_memory']
        current_state = artifacts['current_state']

        self.assertEqual(pre_state['lifecycle_stage'], 'pre-serve')
        self.assertEqual(post_state['lifecycle_stage'], 'post-serve')
        self.assertEqual(current_state['lifecycle_stage'], 'current-state')
        self.assertNotIn('source_payload', pre_state)
        self.assertEqual(pre_state['inputs']['payload']['title'], 'daily-payload-v2')
        self.assertEqual(post_state['inputs']['recommendation_state_in']['lifecycle_stage'], 'pre-serve')
        self.assertEqual(current_state['inputs']['recommendation_state_in']['lifecycle_stage'], 'post-serve')

    def test_runner_refresh_feed_uses_inputs_outputs_metadata(self):
        artifacts = self.build_artifacts()

        refresh_feed = artifacts['refresh_feed']
        run_manifest = artifacts['run_manifest']
        review_markdown = artifacts['review_markdown']

        self.assertNotIn('source_payload', refresh_feed)
        self.assertNotIn('memory_title', refresh_feed)
        self.assertEqual(refresh_feed['inputs']['payload']['title'], 'daily-payload-v2')
        self.assertEqual(refresh_feed['inputs']['recommendation_state_in']['lifecycle_stage'], 'pre-serve')
        self.assertEqual(refresh_feed['outputs']['recommendation_state_out']['lifecycle_stage'], 'post-serve')
        self.assertGreaterEqual(refresh_feed['summary']['selected_count'], 1)
        self.assertIn('pre-serve', review_markdown)
        self.assertIn('current-state', review_markdown)
        self.assertEqual(run_manifest['status'], 'review-ready')

    def test_runner_supports_silent_mode_without_review_ready_status(self):
        payload = self.build_payload()
        artifacts = runner_mod.build_refresh_pipeline_artifacts(
            payload,
            previous_current_state={},
            payload_path='test-output/evolution-refresh-payload-v1.json',
            pre_serve_memory_path='test-output/evolution-recommendation-memory-pre-serve-v1.json',
            post_serve_memory_path='test-output/evolution-recommendation-memory-post-serve-v1.json',
            current_state_path='test-output/evolution-recommendation-memory-current-state-v1.json',
            refresh_feed_path='test-output/evolution-refresh-feed-automation-v1.json',
            refresh_report_path='outputs/evolution-refresh-feed-automation-v1.md',
            run_manifest_path='test-output/evolution-refresh-run-v1.json',
            review_path='outputs/evolution-refresh-review-v1.md',
            item_limit=2,
            run_mode='silent',
            payload_strategy='reuse',
            notify_review_ready=False,
            review_note_output_path='test-output/discord-review-note-evolution-refresh-v1.json',
            tests_status='passed',
            recommend_review='no',
        )

        run_manifest = artifacts['run_manifest']

        self.assertEqual(run_manifest['status'], 'succeeded')
        self.assertEqual(run_manifest['execution']['mode'], 'silent')
        self.assertEqual(run_manifest['execution']['payload_strategy'], 'reuse')
        self.assertFalse(run_manifest['execution']['review_ready_note_requested'])
        self.assertEqual(run_manifest['execution']['tests_status'], 'passed')
        self.assertEqual(run_manifest['execution']['recommend_review'], 'no')

    def test_runner_helpers_resolve_review_note_behavior(self):
        self.assertEqual(runner_mod.resolve_run_status('review'), 'review-ready')
        self.assertEqual(runner_mod.resolve_run_status('silent'), 'succeeded')
        self.assertTrue(runner_mod.should_send_review_ready_note('review', True))
        self.assertFalse(runner_mod.should_send_review_ready_note('silent', True))
        self.assertEqual(runner_mod.resolve_recommend_review('review', 'auto'), 'yes')
        self.assertEqual(runner_mod.resolve_recommend_review('silent', 'auto'), 'no')


if __name__ == '__main__':
    unittest.main()
