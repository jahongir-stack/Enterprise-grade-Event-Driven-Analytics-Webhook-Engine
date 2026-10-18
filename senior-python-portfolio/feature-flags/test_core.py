import unittest
from core import Flags
class Tests(unittest.TestCase):
    def test_targets(self):
        f=Flags(); f.set('beta',50,allow=['a'],deny=['b'])
        self.assertTrue(f.evaluate('beta','a')); self.assertFalse(f.evaluate('beta','b'))
        self.assertEqual(f.evaluate('beta','c'),f.evaluate('beta','c'))
