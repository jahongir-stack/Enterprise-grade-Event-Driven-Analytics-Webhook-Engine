import heapq, itertools, time
class Queue:
    def __init__(self,clock=None,max_attempts=3):
        self.clock=clock or time.monotonic; self.max_attempts=max_attempts
        self._heap=[]; self._seq=itertools.count(); self.jobs={}; self.handlers={}
    def register(self,name,callback): self.handlers[name]=callback
    def submit(self,key,handler,payload):
        if handler not in self.handlers: raise KeyError(handler)
        if key in self.jobs:
            if self.jobs[key]['payload']!=payload: raise ValueError('conflicting key')
            return
        self.jobs[key]={'handler':handler,'payload':payload,'tries':0,'status':'pending'}
        heapq.heappush(self._heap,(self.clock(),next(self._seq),key))
    def tick(self):
        if not self._heap or self._heap[0][0]>self.clock(): return False
        _,_,key=heapq.heappop(self._heap); job=self.jobs[key]
        try:
            job['tries']+=1; self.handlers[job['handler']](job['payload']); job['status']='done'
        except Exception as exc:
            job['error']=str(exc)
            if job['tries']>=self.max_attempts: job['status']='dead'
            else: heapq.heappush(self._heap,(self.clock()+2**(job['tries']-1),next(self._seq),key))
        return True
