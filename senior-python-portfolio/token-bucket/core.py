import threading,time
class Limiter:
    def __init__(self,rate,capacity,clock=None):
        if rate<=0 or capacity<=0: raise ValueError('positive values required')
        self.rate=rate; self.capacity=capacity; self.clock=clock or time.monotonic
        self.buckets={}; self.lock=threading.RLock()
    def take(self,tenant,cost=1):
        if cost<=0 or cost>self.capacity: raise ValueError('bad cost')
        with self.lock:
            now=self.clock(); tokens,last=self.buckets.get(tenant,(self.capacity,now))
            tokens=min(self.capacity,tokens+max(0,now-last)*self.rate)
            allowed=tokens>=cost
            if allowed: tokens-=cost
            self.buckets[tenant]=(tokens,now)
            return {'allowed':allowed,'remaining':tokens,'retry_after':0 if allowed else (cost-tokens)/self.rate}
