"""Trust features: boundary rules, read-only mode, "where were we", undo for deleted files, quiet hours, speech vocabulary."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / 'linux'))
import jev


def prefs(**kw): return patch.object(jev, 'pref', side_effect=lambda k, d: kw.get(k, d))


class Rules(unittest.TestCase):
    def test_boundaries_are_in_every_prompt_once(self):
        p = jev.system_prompt(jev.NEVER)
        self.assertEqual(p.count(jev.TRUST_RULES), 1)
        for phrase in ('malware', 'spies on or tracks another person', 'state the item and total', 'never pretend to be human', 'say what failed, why, and the one next step'):
            self.assertIn(phrase, jev.TRUST_RULES)


class ReadOnly(unittest.TestCase):
    def test_off_blocks_nothing(self):
        with prefs(): self.assertEqual(jev.readonly_block({'tool_name': 'Write'}, {}), '')

    def test_on_blocks_changes_and_allows_reading(self):
        with prefs(readOnly=True):
            for tool, inp in (('Write', {}), ('Edit', {}), ('NotebookEdit', {}), ('Bash', {'command': 'rm x'}), ('Bash', {'command': 'echo hi > file'})):
                self.assertEqual(jev.readonly_block({'tool_name': tool}, inp), jev.READONLY_WHY, (tool, inp))
            for tool, inp in (('Read', {}), ('Grep', {}), ('Glob', {}), ('WebSearch', {})):
                self.assertEqual(jev.readonly_block({'tool_name': tool}, inp), '', (tool, inp))
            me = __import__('shlex').quote(jev.ME)
            self.assertEqual(jev.readonly_block({'tool_name': 'Bash'}, {'command': f'python3 {me} --window'}), '')


class Resume(unittest.TestCase):
    def test_last_asks_oldest_first_and_empty_message(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, 'log.jsonl')
            self.assertIn('fresh start', jev.resume_report(5, path))
            with open(path, 'w') as f:
                for i in range(7): f.write(json.dumps({'at': f'2026-11-10T10:0{i}:00', 'task': f'task {i}', 'reply': f'done {i}'}) + '\n')
            lines = jev.resume_report(3, path).splitlines()
            self.assertEqual(len(lines), 3); self.assertIn('task 4', lines[0]); self.assertIn('done 6', lines[2])


class Undo(unittest.TestCase):
    def run_trash(self, data, *args): return subprocess.run([sys.executable, str(ROOT / 'linux' / 'bin' / 'trash'), *args], env={**os.environ, 'XDG_DATA_HOME': data}, capture_output=True, text=True).stdout.strip()

    def put(self, data, name, original, by='Jev'):
        t = os.path.join(data, 'Trash'); os.makedirs(os.path.join(t, 'files'), exist_ok=True); os.makedirs(os.path.join(t, 'info'), exist_ok=True)
        Path(t, 'files', name).write_text('x')
        Path(t, 'info', name + '.trashinfo').write_text(f'[Trash Info]\nPath={original}\nDeletionDate=2026-11-10T10:00:00\n' + (f'X-Deleted-By={by}\n' if by else ''))

    def test_restores_newest_match_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = os.path.join(d, 'a.txt'), os.path.join(d, 'b.txt')
            self.put(d, 'a (deleted by Jev).txt', a); time.sleep(0.02); self.put(d, 'b (deleted by Jev).txt', b)
            self.assertEqual(self.run_trash(d, '--undo'), f'Restored {b}'); self.assertTrue(os.path.exists(b))
            self.assertEqual(self.run_trash(d, '--undo', 'a'), f'Restored {a}')
            self.put(d, 'c (deleted by Jev).txt', a)   # a.txt exists again: must refuse
            self.assertIn('already exists', self.run_trash(d, '--undo'))
            self.assertEqual(self.run_trash(d, '--undo', 'nomatch'), 'Nothing of mine in the Trash to put back.')

    def test_ignores_items_the_user_trashed_themselves(self):
        with tempfile.TemporaryDirectory() as d:
            self.put(d, 'mine.txt', os.path.join(d, 'mine.txt'), by='')
            self.assertEqual(self.run_trash(d, '--undo'), 'Nothing of mine in the Trash to put back.')


class QuietAndVocab(unittest.TestCase):
    def test_quiet_window_crosses_midnight(self):
        import proactive
        at = lambda h, m: time.mktime((2026, 11, 10, h, m, 0, 0, 0, -1))
        for h, m, expect in ((23, 0, True), (3, 30, True), (6, 59, True), (7, 0, False), (12, 0, False), (21, 59, False), (22, 0, True)):
            self.assertEqual(proactive.quiet_now(at(h, m), '22:00', '07:00'), expect, (h, m))
        self.assertTrue(proactive.quiet_now(at(13, 0), '12:00', '14:00')); self.assertFalse(proactive.quiet_now(at(15, 0), '12:00', '14:00'))

    def test_nudge_is_held_in_quiet_hours_only_when_asked(self):
        import proactive
        state = os.path.join(tempfile.mkdtemp(), 's.json'); sig = lambda now: [('k', 'hello')]
        night = time.mktime((2026, 11, 10, 23, 30, 0, 0, 0, -1))
        self.assertIsNone(proactive.next_nudge(night, state, (sig,), quiet=('22:00', '07:00')))
        self.assertEqual(proactive.next_nudge(night, state, (sig,)), 'hello')   # old behaviour unchanged

    def test_quiet_window_reads_settings_and_rejects_bad_values(self):
        import proactive
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {'JEV_DIR': d}):
            self.assertEqual(proactive.quiet_window(), ('22:00', '07:00'))
            Path(d, 'settings.json').write_text(json.dumps({'quietFrom': '21:30', 'quietTo': '25:99'}))
            self.assertEqual(proactive.quiet_window(), ('21:30', '07:00'))

    def test_vocabulary_prompt(self):
        import models
        self.assertEqual(models.vocab_prompt('Saarthur, Kubernetes ,\nWhisper'), 'Saarthur, Kubernetes, Whisper')
        self.assertIsNone(models.vocab_prompt('')); self.assertIsNone(models.vocab_prompt(None))
        self.assertLessEqual(len(models.vocab_prompt(', '.join(['word'] * 200))), 220)


if __name__ == '__main__':
    unittest.main()
