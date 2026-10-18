from core import Ledger
import unittest
class Tests(unittest.TestCase):
    def test_balanced_idempotent(self):
        a=Ledger(); a.open('cash'); a.open('capital')
        self.assertEqual(a.post('1',[('cash','20'),('capital','-20')])['cash'],20)
        self.assertEqual(a.post('1',[('cash','20'),('capital','-20')])['cash'],20)
        with self.assertRaises(ValueError): a.post('2',[('cash','3')])
