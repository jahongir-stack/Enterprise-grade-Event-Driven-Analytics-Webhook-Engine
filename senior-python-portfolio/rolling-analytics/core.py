from collections import deque
class RollingStats:
    def __init__(self,window):
        if window<=0: raise ValueError('positive window required')
        self.window=window;self.values=deque();self.total=0.;self.last=None
    def add(self,timestamp,value):
        if self.last is not None and timestamp<self.last: raise ValueError('out of order')
        self.last=timestamp;self.values.append((timestamp,float(value)));self.total+=float(value)
        self._expire(timestamp);return self.snapshot()
    def _expire(self,now):
        while self.values and self.values[0][0]<=now-self.window:
            self.total-=self.values.popleft()[1]
    def snapshot(self):
        n=len(self.values)
        return {'count':n,'sum':self.total,'mean':self.total/n if n else None}
