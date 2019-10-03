from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64decode

key = RSA.importKey(open('key.pem.pub').read())
timestamp = 1569397068.997015
signature_b64 = "OBvNwUtv5/6TKQDl8BKIZ6aB5Y3dG9hUJA9gtY3OjVHGI0T2YhkeezDKGbQBe2frigBrXjq1vgAB0I4pUyLnxY78U9bMJkbNyJlfDHkNxZJMm8/ouyEiliUkrVw60oNezWDLk9Fqb2jqhAEyIQbm1/1ihcx58Vw0jHMXbPsZaDeawXL14yKDGBoCBqE7ogZOFRmFGGAlWaMCV4CbsfV2coJ3p1gGU2VitVxMM1fcINU8da/oQLmYi4ggbJPnWxxaJ6lJihFI1ERp8+09xzw+RfzmM3gUGlO5OBnRgU3LNCYr4OQ/FD7BRL1MHwSG7vFELCfkxiaNOKlMxejIoY2WCw=="
signature = b64decode(signature_b64)

h = SHA256.new(str(timestamp).encode())
verifier = PKCS1_v1_5.new(key)
if verifier.verify(h, signature):
  print('The signature is authentic')
else:
  print('The signature is not authentic')