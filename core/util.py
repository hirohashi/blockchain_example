from base64 import b64encode
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import json

def sign(secret_key: str, timestamp: float):
  try: 
    rsakey = RSA.importKey(secret_key) # 秘密鍵のインポート
  except ValueError as err:
    print(err)
    sys.exit(1)
  signer = PKCS1_v1_5.new(rsakey) # Public-Key Cryptography Standards #1 (RSA)
  digest = SHA256.new() 
  digest.update(str(timestamp).encode()) # timestampをsha256でハッシュ化
  sign = signer.sign(digest) # 秘密鍵でハッシュを暗号化
  return b64encode(sign).decode() # Base64を行い，文字列にデコードして返す