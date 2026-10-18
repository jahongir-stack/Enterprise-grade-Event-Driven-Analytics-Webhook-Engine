import time,threading
class OpenCircuit(Exception): pass
class Breaker:
    def __init__(self,threshold=3,cooldown=10,clock=None):
        self.threshold=threshold;self.cooldown=cooldown;self.clock=clock or time.monotonic
        self.failures=0;self.opened=None;self.lock=threading.RLock()
    def call(self,func,*args,**kwargs):
        with self.lock:
            if self.opened is not None:
                if self.clock()-self.opened<self.cooldown: raise OpenCircuit('temporarily unavailable')
                self.opened=None; self.failures=0
        try: result=func(*args,**kwargs)
        except Exception:
            with self.lock:
                self.failures+=1
                if self.failures>=self.threshold: self.opened=self.clock()
            raise
        with self.lock: self.failures=0; self.opened=None
        return result
