import hashlib
import random

num = random.randint(0, 10000000)
proof = 0
hash = hashlib.sha256(f'{proof + num}'.encode()).hexdigest()

while hash[:10] >= "0000030000":
  proof += 1
  hash = hashlib.sha256(f'{proof + num}'.encode()).hexdigest()

print('proof done!')
print(proof)