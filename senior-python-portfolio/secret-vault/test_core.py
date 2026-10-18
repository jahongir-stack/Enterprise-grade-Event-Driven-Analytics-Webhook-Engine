import unittest
from core import Vault
class Tests(unittest.TestCase):
    def test_roundtrip(self):
        v=Vault(b'a'*32); token=v.seal(b'hello'); self.assertEqual(v.open(token),b'hello')
