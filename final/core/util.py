from base64 import b64encode, b64decode
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import json

def sign(secret_key: str, timestamp: float):
  try: 
    rsakey = RSA.importKey(secret_key)
  except ValueError as err:
    print(err)
    sys.exit(1)
  signer = PKCS1_v1_5.new(rsakey)
  digest = SHA256.new()
  digest.update(str(timestamp).encode())
  sign = signer.sign(digest)
  return b64encode(sign).decode()

def verify(pubkey, timestamp, signature_b64):
  key = RSA.importKey(pubkey)
  signature = b64decode(signature_b64)
  h = SHA256.new(str(timestamp).encode())
  verifier = PKCS1_v1_5.new(key)
  if verifier.verify(h, signature):
    print('The signature is authentic')
    return True
  else:
    print('The signature is not authentic')
    return False