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


payload_mod = load_module('scripts-v2/build_daily_payload_v2.py', 'build_daily_payload_v2_refresh')
memory_mod = load_module('scripts-v2/build_recommendation_memory_v1.py', 'build_recommendation_memory_v1_refresh')
serving_mod = load_module('scripts-v2/recommendation_serving_v1.py', 'recommendation_serving_v1')


class EvolutionRefreshFeedTests(unittest.TestCase):
    def build_payload(self):
        applied = (ROOT / 'outputs/applied-ai-evolution-brief-v5.md').read_text(encoding='utf-8')
        openclaw = (ROOT / 'outputs/openclaw-evolution-brief-v15.md').read_text(encoding='utf-8')
        return payload_mod.build_payload(applied, openclaw)

    def test_refresh_feed_suppresses_same_event_same_angle(self):
        payload = self.build_payload()
        memory = memory_mod.build_memory(payload, {})
        refresh_feed, _ = serving_mod.build_refresh_feed(payload, memory, item_limit=6)

        visible_names = [item['name'] for item in refresh_feed['items']]
        suppressed = {item['name']: item for item in refresh_feed['suppressed_items']}

        self.assertIn('jarrodwatts/claude-hud', visible_names)
        self.assertIn('Proactive Agent', visible_names)
        self.assertIn('gsd-build/get-shit-done', suppressed)
        self.assertEqual(suppressed['gsd-build/get-shit-done']['suppression_reason'], 'cooldown:same-event+same-angle')
        self.assertTrue(suppressed['gsd-build/get-shit-done']['same_event'])
        self.assertTrue(suppressed['gsd-build/get-shit-done']['same_angle'])
        self.assertGreater(suppressed['gsd-build/get-shit-done']['repeat_penalty'], 0)

    def test_new_angle_can_break_repeat_gate(self):
        payload = self.build_payload()
        memory = memory_mod.build_memory(payload, {})

        for candidate in payload['feed']['candidate_objects']:
            if candidate['name'] == 'gsd-build/get-shit-done':
                candidate['recommended_action_reason'] = '今天先从执行纪律角度看，而不是继续把它当框架条目。'
                candidate['why_now'] = '这次不是重复框架理由，而是把它当成可立即试验的执行切面。'
                break

        refresh_feed, _ = serving_mod.build_refresh_feed(payload, memory, item_limit=6)
        visible_names = [item['name'] for item in refresh_feed['items']]

        self.assertIn('gsd-build/get-shit-done', visible_names)

    def test_refresh_updates_memory_with_cooldown(self):
        payload = self.build_payload()
        memory = memory_mod.build_memory(payload, {})
        refresh_feed, updated_memory = serving_mod.build_refresh_feed(payload, memory, item_limit=3)

        selected_ids = {item['canonical_id'] for item in refresh_feed['items']}
        records = {record['canonical_id']: record for record in updated_memory['records']}
        claude_hud = records['repo:jarrodwatts/claude-hud']

        self.assertIn('repo:jarrodwatts/claude-hud', selected_ids)
        self.assertEqual(claude_hud['last_served_surface'], 'refresh')
        self.assertEqual(claude_hud['suppression_reason'], 'refresh-cooldown')
        self.assertTrue(claude_hud['suppressed_until'])
        self.assertGreaterEqual(claude_hud['last_effective_serve_score'], 20)


if __name__ == '__main__':
    unittest.main()
