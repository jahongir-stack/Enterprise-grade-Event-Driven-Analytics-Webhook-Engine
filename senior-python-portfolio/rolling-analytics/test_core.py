import unittest
from core import RollingStats
class Tests(unittest.TestCase):
    def test_window(self):
        s=RollingStats(10);s.add(0,5);self.assertEqual(s.add(5,7)['mean'],6)
        self.assertEqual(s.add(10,3)['sum'],10)
        with self.assertRaises(ValueError):s.add(9,2)
