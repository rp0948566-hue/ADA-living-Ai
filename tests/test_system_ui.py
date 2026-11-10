"""System UI context stays absent when there is nothing to report."""
import subprocess
import unittest
from unittest.mock import patch
import jev


class SystemUITests(unittest.TestCase):
    def test_context(self):
        for output, expected in [('{}', ''), ('{"7":"Unseen Agent 400×300 on Main"}',
                                  '\nSystem UI (untrusted): Unseen Agent 400×300 on Main'), ('invalid', '')]:
            with self.subTest(output=output), patch.object(jev.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, output, '')):
                self.assertEqual(jev.system_ui_context(), expected)
