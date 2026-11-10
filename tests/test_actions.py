"""Audit log: every gate decision is recorded privately and can be read back in plain words."""
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import jev


class Actions(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory(); self.path = os.path.join(self.dir.name, 'sub', 'actions.jsonl')

    def tearDown(self): self.dir.cleanup()

    def test_records_allowed_and_blocked_with_reason(self):
        jev.audit({'tool_name': 'Bash'}, {'command': 'git status'}, True, '', self.path)
        jev.audit({'tool_name': 'Bash'}, {'command': 'rm -rf ~/x'}, False, 'Not allowed.', self.path)
        rows = [json.loads(l) for l in open(self.path)]
        self.assertEqual([(r['tool'], r['what'], r['ok']) for r in rows], [('Bash', 'git status', True), ('Bash', 'rm -rf ~/x', False)])
        report = jev.actions_report(10, self.path)
        self.assertIn('ran  Bash: git status', report); self.assertIn('BLOCKED  Bash: rm -rf ~/x  (Not allowed.)', report)

    def test_file_is_private_and_url_or_query_is_the_subject(self):
        jev.audit({'tool_name': 'WebFetch'}, {'url': 'https://example.com'}, True, '', self.path)
        self.assertEqual(stat.S_IMODE(os.stat(self.path).st_mode), 0o600)
        self.assertIn('https://example.com', jev.actions_report(1, self.path))

    def test_empty_and_unreadable_say_so_and_never_raise(self):
        self.assertEqual(jev.actions_report(5, self.path), 'No actions recorded yet.')
        jev.audit({'tool_name': 'X'}, {}, True, '', '/proc/forbidden/actions.jsonl')   # must not raise

    def test_big_log_keeps_the_newest_lines(self):
        os.makedirs(os.path.dirname(self.path))
        with open(self.path, 'w') as f:
            f.write(('x' * 100 + '\n') * 60000)
        jev.audit({'tool_name': 'Bash'}, {'command': 'last'}, True, '', self.path)
        lines = open(self.path).read().splitlines()
        self.assertLessEqual(len(lines), 2001); self.assertIn('"last"', lines[-1])

    def test_helper_is_known_to_agents_and_the_prompt(self):
        self.assertIn('--actions', jev.system_prompt(jev.NEVER))


if __name__ == '__main__':
    unittest.main()
