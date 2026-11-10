import json, os, sys, tempfile, unittest
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jev_x import agent, tools, llm, osctl


def tc(name, args, i='1'):
    return {'content': '', 'tool_calls': [{'id': i, 'type': 'function', 'function': {'name': name, 'arguments': json.dumps(args)}}]}


class Tools(unittest.TestCase):
    def test_shell_and_files(self):
        d = tempfile.mkdtemp(); p = os.path.join(d, 'a.txt')
        self.assertIn('wrote', tools.call('write_file', {'path': p, 'content': 'hi'}))
        self.assertEqual(tools.call('read_file', {'path': p}), 'hi')
        self.assertIn('a.txt', tools.call('list_dir', {'path': d}))
        self.assertIn('hello', tools.call('shell', {'cmd': 'echo hello'}))

    def test_catastrophic_blocked(self):
        for c in ('rm -rf /', 'rm -rf ~', 'mkfs.ext4 /dev/sda1', 'dd if=/dev/zero of=/dev/sda'):
            self.assertIn('blocked', tools.call('shell', {'cmd': c}), c)
        self.assertNotIn('blocked', tools.call('shell', {'cmd': 'rm -rf /tmp/jev-x-nonexistent'}))

    def test_errors_returned_not_raised(self):
        self.assertTrue(tools.call('read_file', {'path': '/no/such/file'}).startswith('error'))
        self.assertIn('unknown', tools.call('nope', {}))

    def test_clip(self):
        self.assertLess(len(tools.clip('x' * 5000)), 1700)


class Agent(unittest.TestCase):
    def test_loop_runs_tool_then_done(self):
        seq = [tc('shell', {'cmd': 'echo hi'}), tc('done', {'answer': 'finished'}, '2')]
        with mock.patch.object(llm, 'chat', side_effect=seq):
            ans, msgs = agent.run('t', cfg={**llm.DEFAULTS}, on_event=lambda e: None)
        self.assertEqual(ans, 'finished')
        self.assertEqual(msgs[2]['role'], 'tool'); self.assertIn('hi', msgs[2]['content'])

    def test_step_limit(self):
        with mock.patch.object(llm, 'chat', return_value=tc('windows', {})):
            ans, _ = agent.run('t', cfg={**llm.DEFAULTS, 'max_steps': 3}, on_event=lambda e: None)
        self.assertIn('step limit', ans)

    def test_bad_json_args_do_not_crash(self):
        bad = {'content': '', 'tool_calls': [{'id': '1', 'function': {'name': 'windows', 'arguments': '{oops'}}]}
        with mock.patch.object(llm, 'chat', side_effect=[bad, {'content': 'plain'}]):
            self.assertEqual(agent.run('t', cfg={**llm.DEFAULTS}, on_event=lambda e: None)[0], 'plain')


class Config(unittest.TestCase):
    def test_env_overrides(self):
        with mock.patch.dict(os.environ, {'JEV_X_BASE_URL': 'https://api.example/v1', 'JEV_X_MODEL': 'big'}):
            c = llm.load_config()
        self.assertEqual((c['base_url'], c['model']), ('https://api.example/v1', 'big'))

    def test_every_schema_has_handler(self):
        for s in tools.SCHEMAS:
            n = s['function']['name']
            if n != 'done': self.assertNotIn('unknown', tools.call(n, {}) if n in ('windows', 'clipboard_get') else 'x')

    def test_capabilities(self):
        self.assertIn(osctl.capabilities()['os'], ('Linux', 'Windows', 'Darwin'))


if __name__ == '__main__':
    unittest.main()
