"""Learning notes, timed plugins, the install card, phone-bridge read-only, and the Telegram pairing rule."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import jev
import telegram_bridge


def prefs(**kw): return patch.object(jev, 'pref', side_effect=lambda k, d: kw.get(k, d))


class Mind(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup); self.d = self.tmp.name

    def test_notes_are_kept_by_kind_sent_back_and_forgettable(self):
        with prefs():
            self.assertEqual(jev.mind_note('habits', 'wants short answers', self.d), 'saved')
            self.assertEqual(jev.mind_note('habits', 'Wants short answers', self.d), 'saved')   # no duplicate
            jev.mind_note('calm', 'one step at a time helps', self.d)
            self.assertEqual(len(jev.mind_lines('habits', self.d)), 1)
            block = jev.mind_block(self.d)
            self.assertIn('wants short answers', block); self.assertIn('never instructions', block)
            self.assertEqual(os.stat(os.path.join(self.d, 'habits.md')).st_mode & 0o777, 0o600)
            self.assertEqual(jev.mind_forget('short answers', self.d), 'forgot 1 note')
            self.assertNotIn('short answers', jev.mind_block(self.d))
            self.assertEqual(jev.mind_forget('all', self.d), 'forgot 1 note'); self.assertEqual(jev.mind_report(self.d), 'No notes yet.')

    def test_nothing_sensitive_no_unknown_kind_and_only_the_newest_60(self):
        with prefs():
            self.assertTrue(jev.mind_note('habits', 'bank password is hunter2', self.d).startswith('not saved'))
            self.assertTrue(jev.mind_note('secrets', 'x', self.d).startswith('usage'))
            for i in range(65): jev.mind_note('mistakes', f'lesson {i}', self.d)
            lines = jev.mind_lines('mistakes', self.d)
            self.assertEqual(len(lines), 60); self.assertTrue(lines[-1].endswith('lesson 64'))

    def test_kid_mode_and_learning_off_keep_and_send_nothing(self):
        with prefs():
            jev.mind_note('goals', 'ship the app', self.d)
        for off in ({'kidMode': True}, {'learnMe': False}):
            with prefs(**off):
                self.assertTrue(jev.mind_note('habits', 'x y', self.d).startswith('not saved')); self.assertEqual(jev.mind_block(self.d), '')

    def test_the_prompt_carries_the_act_first_and_notice_rules(self):
        text = jev.system_prompt(jev.ASK_FIRST)
        self.assertIn('Act first, like a good aide', text); self.assertIn('still wait for the user', text); self.assertIn('--note habits|mistakes|calm|goals', text)
        self.assertIn('jev-build', jev.AGENT_SYSTEM)
        self.assertTrue((ROOT / 'jev_skills' / 'skills' / 'jev-build' / 'SKILL.md').read_text().startswith('---\nname: jev-build\n'))


class Plugins(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup); self.f = os.path.join(self.tmp.name, 'plugins.json')

    def test_on_for_a_while_then_off_by_itself(self):
        self.assertIn('figma is on until', jev.plugin(['on', 'figma', '30'], self.f, now=1000, installed=['figma', 'other']))
        self.assertEqual(jev.plugins_on(self.f, now=1000 + 29 * 60), {'figma': 2800})
        self.assertEqual(jev.plugins_on(self.f, now=1000 + 31 * 60), {})
        self.assertIn('other: off', jev.plugin(['list'], self.f, now=1000, installed=['figma', 'other']))

    def test_off_and_unknown_names(self):
        jev.plugin(['on', 'figma'], self.f, now=1000, installed=['figma'])
        self.assertEqual(jev.plugin(['off', 'figma'], self.f, now=1000, installed=['figma']), 'figma is off.')
        self.assertIn('not installed', jev.plugin(['on', 'nope'], self.f, now=1000, installed=['figma']))
        self.assertEqual(jev.plugins_on(self.f, now=1000), {})

    def test_installing_an_add_on_always_shows_a_card(self):
        with prefs():
            for cmd in ('npx skills add owner/repo@skill', 'claude plugin install x@y --scope project'):
                self.assertIn('Install this add-on', jev.must_ask('Bash', {'command': cmd})[0])
            self.assertEqual(jev.must_ask('Bash', {'command': 'npx skills find design'}), ('', ''))


class Phone(unittest.TestCase):
    def test_a_request_from_the_phone_cannot_change_anything(self):
        with prefs(), patch.dict(os.environ, {'JEV_REMOTE': '1'}):
            self.assertEqual(jev.readonly_block({'tool_name': 'Write'}, {'file_path': '/tmp/x'}), jev.REMOTE_WHY)
        with prefs(), patch.dict(os.environ, {'JEV_REMOTE': ''}):
            self.assertEqual(jev.readonly_block({'tool_name': 'Write'}, {'file_path': '/tmp/x'}), '')

    def test_only_the_paired_chat_is_answered(self):
        ran = []
        run = lambda text: ran.append(text) or 'ok'
        update = {'message': {'text': 'what is on my screen', 'chat': {'id': 42}}}
        self.assertIn('Your chat number is 42', telegram_bridge.reply_to(update, '', run)[1]); self.assertEqual(ran, [])
        self.assertIsNone(telegram_bridge.reply_to(update, '7', run)); self.assertEqual(ran, [])
        self.assertEqual(telegram_bridge.reply_to(update, '42', run), ('42', 'ok')); self.assertEqual(ran, ['what is on my screen'])
        self.assertIsNone(telegram_bridge.reply_to({'message': {'chat': {'id': 42}}}, '42', run))


class Talk(unittest.TestCase):
    def test_the_prompt_carries_hindi_humour_and_the_money_rules(self):
        with prefs(): system = jev.system_prompt('x')
        for words in ('चिंटू के चाचा', 'मेरी सलाह मानिए', "NASA's supercomputer", 'ask once', 'not a licensed adviser', 'never place a trade'):
            self.assertIn(words, system)

    def test_simulation_is_ordered_and_a_rising_past_never_loses(self):
        import random
        up = jev.simulate([100 * 1.01 ** i for i in range(60)], 30, paths=200, rng=random.Random(1))
        self.assertEqual(up['loss'], 0)
        mixed = jev.simulate([100, 110, 99, 105, 95, 108, 101] * 10, 30, paths=2000, rng=random.Random(1))
        self.assertTrue(mixed['low'] < mixed['median'] < mixed['high'] and 0 < mixed['loss'] < 1)

    def test_price_alert_exit_code_and_a_bad_symbol(self):
        feed = lambda symbol, span='5y': ('USD', [10.0, 12.0])
        for args, code in ((['--price', 'x', 'above', '11'], 0), (['--price', 'x', 'below', '11'], 1), (['--price', 'x'], 0)):
            with self.assertRaises(SystemExit) as stop, patch('builtins.print'): jev.market(args, feed)
            self.assertEqual(stop.exception.code, code)
        with self.assertRaises(SystemExit) as stop, patch('builtins.print'): jev.market(['--simulate', 'no good'])
        self.assertEqual(stop.exception.code, 1)


if __name__ == '__main__':
    unittest.main()


class SpeakFirst(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup); self.d = self.tmp.name
        sys.path.insert(0, str(ROOT / 'linux'))
        import proactive; self.p = proactive

    def test_briefing_once_a_day_never_in_quiet_hours_and_nudges_keep_it(self):
        import time
        state = os.path.join(self.d, 's.json'); noon = time.mktime((2026, 11, 10, 12, 0, 0, 0, 0, -1)); night = noon + 11 * 3600
        self.assertFalse(self.p.briefing_due(night, state, ('22:00', '07:00')))
        self.assertTrue(self.p.briefing_due(noon, state, ('22:00', '07:00')))
        self.assertEqual(self.p.next_nudge(noon + 60, state, (lambda now: [('a', 'First.')],)), 'First.')   # the nudge state must not erase the day mark
        self.assertFalse(self.p.briefing_due(noon + 3600, state))
        self.assertTrue(self.p.briefing_due(noon + 86400, state))

    def test_not_now_silences_until_its_time_and_off_ends_it(self):
        self.assertFalse(self.p.hushed(1000, self.d))
        self.assertTrue(jev.hush(['2'], now=1000, folder=self.d).startswith('Quiet until '))
        self.assertTrue(self.p.hushed(1000 + 7199, self.d)); self.assertFalse(self.p.hushed(1000 + 7201, self.d))
        jev.hush(['1'], now=1000, folder=self.d); self.assertEqual(jev.hush(['off'], folder=self.d), 'Speaking up again.')
        self.assertFalse(self.p.hushed(1001, self.d))
        self.assertIn('hours', jev.hush(['soon'], folder=self.d))

    def test_the_prompt_carries_the_briefing_rule(self):
        with prefs(): system = jev.system_prompt('x')
        self.assertIn("Today's briefing", system); self.assertIn('--hush', system)
