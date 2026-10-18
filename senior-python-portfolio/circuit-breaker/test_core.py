import unittest
from core import Breaker,OpenCircuit
class Tests(unittest.TestCase):
    def test_open_and_recover(self):
        now=[0]; b=Breaker(1,2,lambda:now[0])
        with self.assertRaises(ZeroDivisionError): b.call(lambda:1/0)
        with self.assertRaises(OpenCircuit): b.call(lambda:1)
        now[0]=2; self.assertEqual(b.call(lambda:9),9)
