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


payload_mod = load_module('scripts-v2/build_daily_payload_v2.py', 'build_daily_payload_v2')
package_mod = load_module('scripts-v2/build_daily_news_package_v1.py', 'build_daily_news_package_v1')
render_mod = load_module('scripts-v2/render_daily_report_news_zh_v3.py', 'render_daily_report_news_zh_v3')


class DailyNewsPipelineV3Tests(unittest.TestCase):
    def build_payload(self):
        applied = (ROOT / 'outputs/applied-ai-evolution-brief-v5.md').read_text(encoding='utf-8')
        openclaw = (ROOT / 'outputs/openclaw-evolution-brief-v15.md').read_text(encoding='utf-8')
        return payload_mod.build_payload(applied, openclaw)

    def test_upgraded_items_surface_into_priority(self):
        payload = self.build_payload()
        priority_names = [item['name'] for item in payload['summary']['priority']]
        self.assertIn('jarrodwatts/claude-hud', priority_names)
        self.assertIn('Proactive Agent', priority_names)

        claude_hud = next(item for item in payload['summary']['priority'] if item['name'] == 'jarrodwatts/claude-hud')
        proactive = next(item for item in payload['summary']['priority'] if item['name'] == 'Proactive Agent')

        self.assertTrue(claude_hud['changed_today'])
        self.assertTrue(proactive['changed_today'])
        self.assertEqual(claude_hud['freshness']['label'], '今日升级')
        self.assertEqual(proactive['freshness']['label'], '今日升级')

    def test_payload_consumes_x_contract_and_mock_signals(self):
        payload = self.build_payload()
        x_lane = payload['x_signal_lane']

        self.assertEqual(x_lane['mode'], 'mock-watchlist')
        self.assertEqual(x_lane['artifact_counts']['author_signals'], 4)
        self.assertGreaterEqual(x_lane['matched_item_count'], 3)
        self.assertIn('jarrodwatts/claude-hud', x_lane['matched_items'])

        claude_hud = next(item for item in payload['summary']['priority'] if item['name'] == 'jarrodwatts/claude-hud')
        gog = next(item for item in payload['summary']['follow'] if item['name'] == 'Gog')

        self.assertTrue(claude_hud['x_signal']['matched'])
        self.assertTrue(claude_hud['x_signal']['repeat_convergence'])
        self.assertIn('builder_alpha', claude_hud['x_signal']['authors'])
        self.assertIn('圈内冒头信号', claude_hud['today_signal'])

        self.assertTrue(gog['x_signal']['matched'])
        self.assertIn('skeptic_delta', gog['x_signal']['risk_note'])
        self.assertIn('弱风险备注', gog['change_note'])

    def test_news_package_balances_front_page(self):
        payload = self.build_payload()
        package = package_mod.build_news_package(payload)
        lead_tracks = [item['track'] for item in package['sections']['lead']]

        self.assertEqual(len(package['sections']['lead']), 2)
        self.assertEqual(len(set(lead_tracks)), 2)
        self.assertTrue(package['desk']['front_page_balance']['balanced'])
        self.assertGreaterEqual(len(package['desk']['quick_alerts']), 2)
        self.assertGreaterEqual(package['desk']['x_signal_lane']['matched_item_count'], 3)
        self.assertIn('jarrodwatts/claude-hud', package['desk']['x_signal_lane']['matched_items'])

    def test_render_reads_like_daily_news(self):
        payload = self.build_payload()
        package = package_mod.build_news_package(payload)
        report = render_mod.render_report(package)

        self.assertIn('## X 信号层', report)
        self.assertIn('## 一眼看完今天', report)
        self.assertIn('## 今日头条', report)
        self.assertIn('今天发生了什么', report)
        self.assertIn('作者信号', report)
        self.assertIn('风险备注', report)
        self.assertIn('为什么今天值得提', report)
        self.assertIn('builder_alpha', report)
        self.assertIn('skeptic_delta', report)
        self.assertIn('## 快讯雷达', report)
        self.assertIn('## 官方基线', report)


if __name__ == '__main__':
    unittest.main()
