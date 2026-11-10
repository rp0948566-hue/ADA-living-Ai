"""Private mode: blocks anything that sends data off the computer, and --privacy tells the truth about where words go."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import jev


def prefs(**kw): return patch.object(jev, 'pref', side_effect=lambda k, d: kw.get(k, d))


class Private(unittest.TestCase):
    def test_off_blocks_nothing(self):
        with prefs():
            self.assertEqual(jev.private_block('WebFetch', {'url': 'https://x.com'}), '')

    def test_on_blocks_web_connectors_and_network_shell(self):
        with prefs(privateMode=True):
            for tool, inp in (('WebFetch', {}), ('WebSearch', {}), ('mcp__slack__post', {}), ('Bash', {'command': 'python3 jev.py --search "x"'}),
                              ('Bash', {'command': 'curl https://x.com'}), ('Bash', {'command': 'jev/linux/bin/browser open https://x.com'})):
                self.assertEqual(jev.private_block(tool, inp), jev.PRIVATE_WHY, (tool, inp))

    def test_on_still_allows_local_work(self):
        with prefs(privateMode=True):
            for tool, inp in (('Bash', {'command': 'ls -la'}), ('Read', {'file_path': '/tmp/a'}), ('Bash', {'command': 'python3 jev.py --window'})):
                self.assertEqual(jev.private_block(tool, inp), '', (tool, inp))


class Report(unittest.TestCase):
    def test_cloud_local_and_remote_server(self):
        with prefs(): self.assertIn('cloud service; they leave this computer', jev.privacy_report())
        with prefs(apiBase='http://127.0.0.1:8089/v1'): self.assertIn('only to the model on this computer (127.0.0.1)', jev.privacy_report())
        with prefs(apiBase='https://api.deepseek.com/anthropic'): self.assertIn('api.deepseek.com, a server outside this computer', jev.privacy_report())

    def test_mode_is_stated(self):
        with prefs(privateMode=True): self.assertIn('Private mode is ON', jev.privacy_report())
        with prefs(): self.assertIn('Private mode is off', jev.privacy_report())

    def test_known_to_prompt_and_agents(self):
        self.assertIn('--privacy', jev.system_prompt(jev.NEVER))


if __name__ == '__main__':
    unittest.main()
