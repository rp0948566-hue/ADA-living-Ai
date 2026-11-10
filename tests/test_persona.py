"""Jev's single personality, its agent work rules, and the agents' copy of every installed Claude Code plugin."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import jev


class Personality(unittest.TestCase):
    def test_always_in_the_prompt_once(self):
        self.assertEqual(jev.system_prompt(jev.NEVER).count(jev.PERSONALITY), 1)

    def test_safe_and_quiet_about_saving(self):
        self.assertIn('never threaten', jev.PERSONALITY)
        self.assertIn('Never mention tokens', jev.AGENT_SYSTEM)

    def test_agents_build_real_software(self):
        for word in ('Rust', 'TypeScript', 'Flutter', 'README', 'tests'):
            self.assertIn(word, jev.AGENT_SYSTEM)


class AgentPlugins(unittest.TestCase):
    def test_switched_off_plugin_gives_skills_not_servers(self):
        with tempfile.TemporaryDirectory() as root:
            home = Path(root); claude = home / '.claude'; (claude / 'plugins').mkdir(parents=True)
            plugins = {}
            for name in ('on', 'off'):
                p = home / name; (p / 'skills' / name).mkdir(parents=True)
                (p / 'skills' / name / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: d\n---\nx\n')
                (p / '.mcp.json').write_text(json.dumps({'mcpServers': {'srv': {'command': name}}}))
                plugins[f'{name}@m'] = [{'scope': 'user', 'installPath': str(p)}]
            (claude / 'settings.json').write_text(json.dumps({'enabledPlugins': {'on@m': True, 'off@m': False}}))
            (claude / 'plugins' / 'installed_plugins.json').write_text(json.dumps({'plugins': plugins}))
            ask = home / 'ask'; ask.mkdir()
            with patch.object(jev, 'HOME', str(home)):
                flags = jev.user_agent_tools(str(ask))
            plugin_root = Path(flags[flags.index('--plugin-dir') + 1])
            skills = {s.name for s in plugin_root.glob('*/skills/*')}
            self.assertEqual(skills, {'on', 'off', 'jev-build', 'jev-money'})
            servers = json.loads((ask / 'user-mcp.json').read_text())
            self.assertEqual([v['command'] for v in servers.values()], ['on'])


if __name__ == '__main__':
    unittest.main()
