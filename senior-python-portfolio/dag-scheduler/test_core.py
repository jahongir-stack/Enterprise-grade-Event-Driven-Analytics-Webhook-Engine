import unittest
from core import Scheduler,CycleError
class Tests(unittest.TestCase):
    def test_order(self):
        s=Scheduler(); s.add('deploy',['build']); s.add('build',['test']); s.add('test')
        self.assertEqual(s.plan(),['test','build','deploy'])
    def test_cycle(self):
        s=Scheduler(); s.add('a',['b']); s.add('b',['a'])
        with self.assertRaises(CycleError): s.plan()
