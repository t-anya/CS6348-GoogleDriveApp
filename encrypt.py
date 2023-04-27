from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt

def encryptToFile(userInfo, bankDetails):
    outFile = open(userInfo[1] + '.encrypted', 'wb')
    
    salt = get_random_bytes(32)
    password = userInfo[2]

    key = scrypt(password, salt, key_len = 32, N = 2**18, r = 8, p = 1)
    outFile.write(salt)

    cipher = AES.new(key, AES.MODE_GCM)
    outFile.write(cipher.nonce)

    data = str(bankDetails[0]) + ", " + str(bankDetails[1])

    encrypted_data = cipher.encrypt(data.encode('utf-8'))
    outFile.write(encrypted_data)

    tag = cipher.digest()
    outFile.write(tag)

    outFile.close()

    return (key, tag)

# Usage
# from encrypt import encryptToFile
uinfo = ["Chase", "jxk10000", "SuperSecRetPassWord"]
bdetails = [1110006668, 123456789]
key, tag = encryptToFile(uinfo, bdetails)
print(key)
print(tag)
