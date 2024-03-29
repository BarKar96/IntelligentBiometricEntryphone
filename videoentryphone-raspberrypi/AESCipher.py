import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher:

    def __init__(self):
        self.bs = 16
        

    def setKey(self,sharedSecret):
        self.key = hashlib.sha256(sharedSecret.encode()).digest()
        
    def encrypt(self, message):
        message = self._pad(message)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        temp = bytes(message, encoding="utf8")
        return base64.b64encode(iv + cipher.encrypt(temp)).decode('utf-8')

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


#z = AESCipher("12")
#a = z.encrypt("bartek")
#g = z.decrypt("dF+EHHYrBi32suqEn3JTrBNqZXsJT9PDA1JvwfjMiKY=")
#print(g)