"""Discovery with -s tests imports modules directly; initialize scratch config first."""
from tests import config
import jev
import unittest


class ConfigTests(unittest.TestCase):
    def test_import_uses_scratch_config(self):
        self.assertEqual(jev.DIR, config.name)
