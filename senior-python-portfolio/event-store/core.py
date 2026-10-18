import json, hashlib, threading
class VersionConflict(Exception): pass
class EventStore:
    def __init__(self): self._events={}; self._lock=threading.RLock()
    def append(self, stream, expected, kind, payload):
        with self._lock:
            records=self._events.setdefault(stream,[])
            if len(records)!=expected: raise VersionConflict('stale version')
            previous=records[-1]['hash'] if records else 'GENESIS'
            serialized=json.dumps([previous,stream,kind,payload],sort_keys=True,allow_nan=False)
            event={'version':expected+1,'kind':kind,'payload':json.loads(json.dumps(payload)),
                   'hash':hashlib.sha256(serialized.encode()).hexdigest()}
            records.append(event); return event.copy()
    def read(self,stream): return json.loads(json.dumps(self._events.get(stream,[])))
    def verify(self,stream):
        previous='GENESIS'
        for event in self.read(stream):
            data=json.dumps([previous,stream,event['kind'],event['payload']],sort_keys=True,allow_nan=False)
            if event['hash']!=hashlib.sha256(data.encode()).hexdigest(): return False
            previous=event['hash']
        return True
