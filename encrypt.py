from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt


user_info = ["Chase", "jxk10000", "SuperSecRetPassWord"]
ssn = 123456789

out_file = open(user_info[1] + '.encrypted', 'wb')

salt = get_random_bytes(32)
password = user_info[2]

key = scrypt(password, salt, key_len = 32, N = 2**18, r = 8, p = 1)
out_file.write(salt)

cipher = AES.new(key, AES.MODE_GCM)
out_file.write(cipher.nonce)

encrypted_data = cipher.encrypt(str(ssn).encode('utf-8'))
out_file.write(encrypted_data)

tag = cipher.digest()
out_file.write(tag)

out_file.close()
