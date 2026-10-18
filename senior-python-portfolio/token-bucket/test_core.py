import unittest
from core import Limiter
class Tests(unittest.TestCase):
    def test_isolation(self):
        now=[0]; l=Limiter(1,1,lambda:now[0]); self.assertTrue(l.take('a')['allowed'])
        self.assertFalse(l.take('a')['allowed']); self.assertTrue(l.take('b')['allowed'])
        now[0]=1; self.assertTrue(l.take('a')['allowed'])
