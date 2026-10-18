import hmac,hashlib,json
class AuditLog:
    def __init__(self,key):
        if not key: raise ValueError('key required')
        self.key=key; self.entries=[]
    def record(self,actor,action,data):
        previous=self.entries[-1]['signature'] if self.entries else 'GENESIS'
        body={'actor':actor,'action':action,'data':data,'previous':previous}
        serialized=json.dumps(body,sort_keys=True,separators=(',',':')).encode()
        signature=hmac.new(self.key,serialized,hashlib.sha256).hexdigest()
        self.entries.append({**json.loads(serialized),'signature':signature})
        return signature
    def verify(self):
        previous='GENESIS'
        for entry in self.entries:
            body={k:entry[k] for k in ('actor','action','data','previous')}
            if body['previous']!=previous: return False
            digest=hmac.new(self.key,json.dumps(body,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()
            if not hmac.compare_digest(digest,entry['signature']): return False
            previous=digest
        return True
