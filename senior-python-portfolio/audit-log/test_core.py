import unittest
from core import AuditLog
class Tests(unittest.TestCase):
    def test_tampering(self):
        a=AuditLog(b'demo-secret'); a.record('alice','login',{'ok':True})
        self.assertTrue(a.verify()); a.entries[0]['data']['ok']=False; self.assertFalse(a.verify())
