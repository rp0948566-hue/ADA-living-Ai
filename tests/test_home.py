"""Home Assistant helper against a local fake server: list, state, call, and the failure messages."""
import json
import shlex
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import sys
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import jev

STATES = [{'entity_id': 'light.kitchen', 'state': 'off', 'attributes': {'friendly_name': 'Kitchen light'}},
          {'entity_id': 'climate.hall', 'state': 'heat', 'attributes': {'friendly_name': 'Hall thermostat', 'temperature': 20}}]
CALLS = []


class Fake(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _send(self, code, body):
        data = json.dumps(body).encode(); self.send_response(code); self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(data))); self.end_headers(); self.wfile.write(data)

    def do_GET(self):
        if self.headers.get('Authorization') != 'Bearer good': return self._send(401, {})
        if self.path == '/api/states': return self._send(200, STATES)
        found = [s for s in STATES if self.path == '/api/states/' + s['entity_id']]
        self._send(200, found[0]) if found else self._send(404, {})

    def do_POST(self):
        if self.headers.get('Authorization') != 'Bearer good': return self._send(401, {})
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        CALLS.append((self.path, body)); self._send(200, [])


class Home(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(('127.0.0.1', 0), Fake); cls.base = f'http://127.0.0.1:{cls.server.server_port}'
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls): cls.server.shutdown(); cls.server.server_close()

    def run_home(self, *args, token='good'): return jev.home(list(args), base=self.base, token=token)

    def test_not_set_up_says_where_to_set_it(self):
        self.assertIn('Settings → Smart home', jev.home(['list'], base='', token=''))

    def test_list_filters_by_words_and_state_reports_attributes(self):
        self.assertEqual(self.run_home('list').count('\n'), 1)
        self.assertEqual(self.run_home('list', 'kitchen'), 'light.kitchen  off  Kitchen light')
        self.assertIn('No matching devices.', self.run_home('list', 'garage'))
        self.assertIn('climate.hall: heat', self.run_home('state', 'climate.hall')); self.assertIn('"temperature": 20', self.run_home('state', 'climate.hall'))

    def test_call_posts_service_with_entity_and_extra_json(self):
        out = self.run_home('call', 'light.turn_on', 'light.kitchen', '{"brightness": 120}')
        self.assertIn('Done: light.turn_on on light.kitchen', out)
        self.assertEqual(CALLS[-1], ('/api/services/light/turn_on', {'entity_id': 'light.kitchen', 'brightness': 120}))

    def test_errors_are_plain_words(self):
        self.assertIn('wrong token?', self.run_home('list', token='bad'))
        self.assertIn('unknown entity or service?', self.run_home('state', 'light.nope'))
        self.assertIn('Cannot reach Home Assistant', jev.home(['list'], base='http://127.0.0.1:1', token='good'))
        self.assertIn('Use: --home', self.run_home('call', 'turn_on'))   # no domain
        self.assertIn('Use: --home', self.run_home())

    def test_bad_extra_json_does_not_raise(self):
        self.assertTrue(self.run_home('call', 'light.turn_on', 'light.kitchen', '{bad'))

    def test_a_call_is_never_a_trusted_read_helper(self):
        self.assertIn('--home', jev.system_prompt(jev.NEVER))
        me = shlex.quote(jev.ME)
        self.assertTrue(jev.agent_read_command(f'python3 {me} --window'))   # control: the check works with this path
        self.assertFalse(jev.agent_read_command(f'python3 {me} --home call light.turn_on light.kitchen'))


if __name__ == '__main__':
    unittest.main()
