import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt

BUFFER_SIZE = 1024 * 1024

user_info = ["Chase", "jxk10000", "SuperSecRetPassWord"]

in_file = open(user_info[1] + ".encrypted", 'rb')
out_file = open("decrypted.txt", 'wb')

salt = in_file.read(32)
key = scrypt(user_info[2], salt, key_len = 32, N = 2**18, r = 8, p = 1)

nonce = in_file.read(16)
cipher = AES.new(key, AES.MODE_GCM, nonce = nonce)

in_file_size = os.path.getsize(user_info[1] + ".encrypted")
encrypted_data_size = in_file_size - 32 - 16 - 16

for _ in range(int(encrypted_data_size / BUFFER_SIZE)):
    data = in_file.read(BUFFER_SIZE)
    decrypted_data = cipher.decrypt(data)
    out_file.write(decrypted_data)

data = in_file.read(int(encrypted_data_size % BUFFER_SIZE))
decrypted_data = cipher.decrypt(data)
out_file.write(decrypted_data)

tag = in_file.read(16)

try:
    cipher.verify(tag)

except ValueError as e:
    in_file.close()
    out_file.close()
    os.remove("decrypted.txt")
    raise e

in_file.close()
out_file.close()
