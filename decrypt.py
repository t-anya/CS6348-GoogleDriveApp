import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt

BUFFER_SIZE = 1024 * 1024

def decryptFromFile(userInfo):
    inFile = open(userInfo[1] + ".encrypted", 'rb')
    # outFile = open("decrypted.txt", 'wb')

    salt = inFile.read(32)
    key = scrypt(userInfo[2], salt, key_len = 32, N = 2**18, r = 8, p = 1)

    nonce = inFile.read(16)
    cipher = AES.new(key, AES.MODE_GCM, nonce = nonce)

    inFileSize = os.path.getsize(userInfo[1] + ".encrypted")
    encryptedDataSize = inFileSize - 32 - 16 - 16

    for _ in range(int(encryptedDataSize / BUFFER_SIZE)):
        data = inFile.read(BUFFER_SIZE)
        decryptedData = cipher.decrypt(data)
        # outFile.write(decryptedData)

    data = inFile.read(int(encryptedDataSize % BUFFER_SIZE))
    decryptedData = cipher.decrypt(data)
    # outFile.write(decryptedDdata)

    tag = inFile.read(16)
    
    stringData = decryptedData.decode()
    bankDetails = stringData.split(",")
    bankDetails = [int(x) for x in bankDetails]

    try:
        cipher.verify(tag)

    except ValueError as e:
        inFile.close()
        # out_file.close()
        # os.remove("decrypted.txt")
        raise e

    inFile.close()
    # out_file.close()
    return bankDetails

# Usage
# from decrypt import decryptFromFile

# uinfo = ["Chase", "jxk10000", "SuperSecRetPassWord"]
# bankAcc, ssn = decryptFromFile(uinfo)
# print(bankAcc)
# print(ssn)
