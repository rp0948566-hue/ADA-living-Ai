"""Handoff target lifecycle, with fake workers and native window guards only."""
import io
import json
import os
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

import jev
from tests import test_agents


class FormTargetTests(unittest.TestCase):
    setUp = test_agents.AgentTests.setUp
    prepare = test_agents.AgentTests.prepare
    def test_native_form_handoff_keeps_exact_window_through_remap_and_action(self):
        source = Path(self.root.name, 'source'); source.mkdir()
        target = {'app': 'Form Fixture', 'pid': 123, 'windowID': '42',
                  'window': 'Form', 'windowFrame': [0, 0, 800, 600]}
        (source / 'hands.json').write_text(json.dumps({**target, 'nodes': [{'label': 'Answer', 'value': 'fixture value'}]}))
        (source / 'hands.json.windows').write_text(json.dumps({'123': ['43']}))
        with patch.dict(os.environ, {'JEV_HANDS_STATE': str(source / 'hands.json')}), \
             patch.object(jev, 'browser_adapter', return_value=''), \
             patch.object(jev, 'osa', return_value='Other window') as osa:
            page = jev.work_page(ask=str(source))
        self.assertEqual(page.get('target'), target)
        osa.assert_not_called()  # no front-window rediscovery, or wait, for an already mapped form
        with patch.object(jev, 'browser_adapter', return_value=''), patch.object(jev, 'osa') as osa:
            self.assertEqual(jev.work_page(app=target['app'], ask=str(source)), page)
            osa.assert_not_called()
        row = self.prepare('WAIT fill the form', request='fill the form', app=target['app'], page=page)
        self.manager.start(row['id'])
        present = ['42', '43']; phase = ['Page']; writes = []; pins = []

        def native(args, **kwargs):
            pin = kwargs['env'].get('JEV_HANDS_WINDOW'); pins.append(pin)
            valid = pin in present
            check = {'args': args[2:], 'labels': ['Answer'], 'pid': 123}
            process = Mock(args=args, returncode=0 if valid else 1)
            process.poll.return_value = process.returncode
            process.stdout = io.StringIO(json.dumps(check) + '\n' if valid else '')
            def communicate(answer=None, **unused):
                if not valid: return 'window closed or changed', ''
                if args[2] == 'see':
                    Path(kwargs['env']['JEV_HANDS_STATE']).write_text(json.dumps({**target, 'window': phase[0]}))
                if args[2] == 'type' and answer == 'y\n': writes.append((pin, phase[0]))
                return phase[0], ''
            process.communicate.side_effect = communicate
            return process

        with patch.dict(os.environ, {'JEV_AGENT': row['id'], 'JEV_ASK': row['directory'],
                                     'JEV_HANDS_STATE': str(Path(row['directory'], 'hands.json')),
                                     'JEV_FRONT': 'Other Fixture'}), \
             patch.object(jev.subprocess, 'Popen', side_effect=native), \
             patch.object(jev.select, 'select', side_effect=lambda reads, *unused: (reads, [], [])), \
             patch.object(jev.subprocess, 'run') as lookup:
            for name in ('Page', 'Next page', 'Sheet'):
                phase[0] = name
                self.assertEqual(jev.hands_map(target['app'])['windowID'], '42')
                self.assertEqual(jev.hands_call(['read', target['app']]).returncode, 0)
                _, result = jev.hands_action(['type', 'Answer', 'fixture value'], lambda _: True)
                self.assertEqual(result.returncode, 0)
            Path(row['directory'], 'hands.json').write_text(json.dumps({**target, 'windowID': '43'}))
            present.remove('42')  # the other window remains, but must never be substituted
            self.assertIsNone(jev.hands_map(target['app']))
            _, result = jev.hands_action(['type', 'Answer', 'fixture value'], lambda _: True)
            self.assertNotEqual(result.returncode, 0)
            lookup.assert_not_called()
        self.assertEqual(writes, [('42', name) for name in ('Page', 'Next page', 'Sheet')])
        self.assertEqual(set(pins), {'42'})

