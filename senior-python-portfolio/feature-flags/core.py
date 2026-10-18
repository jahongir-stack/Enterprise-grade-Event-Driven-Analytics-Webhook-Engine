import hashlib
class Flags:
    def __init__(self): self.rules={}
    def set(self,name,percentage=0,enabled=True,allow=(),deny=(),salt='v1'):
        if not 0<=percentage<=100: raise ValueError('percentage out of range')
        self.rules[name]=(percentage,enabled,set(allow),set(deny),salt)
    def evaluate(self,name,user):
        if name not in self.rules: return False
        pct,enabled,allow,deny,salt=self.rules[name]
        if not enabled or user in deny: return False
        if user in allow: return True
        score=int.from_bytes(hashlib.sha256(f'{salt}:{name}:{user}'.encode()).digest()[:8],'big')/2**64*100
        return score<pct
