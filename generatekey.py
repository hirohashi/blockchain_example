from Crypto.PublicKey import RSA

privatekey = RSA.generate(2048)
f = open('key.pem', 'wb')
f.write(privatekey.exportKey('PEM'))
f.close()

f = open('key.pem.pub', 'wb')
f.write(privatekey.publickey().exportKey('PEM'))
f.close()