import heapq
class CycleError(Exception): pass
class Scheduler:
    def __init__(self): self.tasks={}
    def add(self,name,dependencies=()):
        if name in self.tasks: raise ValueError('duplicate task')
        self.tasks[name]=set(dependencies)
    def plan(self):
        pending={k:set(v) for k,v in self.tasks.items()}
        if any(dep not in pending for deps in pending.values() for dep in deps): raise KeyError('unknown task')
        ready=[k for k,v in pending.items() if not v]; heapq.heapify(ready)
        result=[]
        while ready:
            item=heapq.heappop(ready); result.append(item)
            for task,deps in pending.items():
                if item in deps:
                    deps.remove(item)
                    if not deps: heapq.heappush(ready,task)
        if len(result)!=len(pending): raise CycleError('dependency cycle')
        return result
