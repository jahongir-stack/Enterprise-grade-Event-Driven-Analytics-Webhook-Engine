import secrets,hmac,hashlib,base64
class Vault:
    """Demonstration construction; NOT a replacement for audited AEAD (AES-GCM)."""
    def __init__(self,key):
        if len(key)<32: raise ValueError('32-byte key required')
        self.enc=hashlib.sha256(b'enc'+key).digest(); self.mac=hashlib.sha256(b'mac'+key).digest()
    def _stream(self,nonce,length):
        return b''.join(hmac.new(self.enc,nonce+i.to_bytes(8,'big'),hashlib.sha256).digest()
                        for i in range((length+31)//32))[:length]
    def seal(self,plaintext):
        nonce=secrets.token_bytes(16); ciphertext=bytes(a^b for a,b in zip(plaintext,self._stream(nonce,len(plaintext))))
        tag=hmac.new(self.mac,nonce+ciphertext,hashlib.sha256).digest()
        return base64.urlsafe_b64encode(nonce+tag+ciphertext).decode()
    def open(self,token):
        raw=base64.urlsafe_b64decode(token); nonce,tag,ciphertext=raw[:16],raw[16:48],raw[48:]
        expected=hmac.new(self.mac,nonce+ciphertext,hashlib.sha256).digest()
        if not hmac.compare_digest(tag,expected): raise ValueError('integrity check failed')
        return bytes(a^b for a,b in zip(ciphertext,self._stream(nonce,len(ciphertext))))
