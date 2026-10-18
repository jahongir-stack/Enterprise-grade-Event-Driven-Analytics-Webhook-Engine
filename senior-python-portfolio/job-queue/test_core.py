import unittest
from core import Queue
class Tests(unittest.TestCase):
    def test_retry(self):
        now=[0]; q=Queue(lambda:now[0],2); q.register('x',lambda _: 1/0); q.submit('id','x',{})
        self.assertTrue(q.tick()); self.assertFalse(q.tick()); now[0]=1; self.assertTrue(q.tick())
        self.assertEqual(q.jobs['id']['status'],'dead')
