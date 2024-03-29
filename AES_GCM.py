import os
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import scrypt
import json
from GoogleDr_api import authenticate_google_drive, read_file, rewrite_file,get_file_id_by_name,get_folder_id

def generateKey(password, salt):
    key = scrypt(password, salt, key_len = 32, N = 2**18, r = 8, p = 1)
    return key

def encryptDriveFile(plainText, password,fileName, folder_name, tags):
    salt = get_random_bytes(16)
    key = generateKey(password, salt)
    cipher = AES.new(key, AES.MODE_GCM)
    cipherText, authTag = cipher.encrypt_and_digest(plainText.encode('utf-8'))

    encrypted_data = {
        'salt': base64.b64encode(salt).decode('utf-8'),
        'nonce': base64.b64encode(cipher.nonce).decode('utf-8'),
        'authTag': base64.b64encode(authTag).decode('utf-8'),
        'cipherText': base64.b64encode(cipherText).decode('utf-8'),
        'tags': tags
    }
    encrypted_data_str = json.dumps(encrypted_data)

    drive_service = authenticate_google_drive()
    folder_id = get_folder_id(drive_service, folder_name)
    file_id = get_file_id_by_name(drive_service, fileName, parent_id=folder_id)
    rewrite_file(drive_service, file_id, encrypted_data_str, mime_type='text/plain')
    print(read_file(drive_service, file_id))


def encryptToFile(plainText, password,fileName, tags):
    salt = get_random_bytes(16)
    key = generateKey(password, salt)
    cipher = AES.new(key, AES.MODE_GCM)
    cipherText, authTag = cipher.encrypt_and_digest(plainText.encode('utf-8'))

    encrypted_data = {
        'salt': base64.b64encode(salt).decode('utf-8'),
        'nonce': base64.b64encode(cipher.nonce).decode('utf-8'),
        'authTag': base64.b64encode(authTag).decode('utf-8'),
        'cipherText': base64.b64encode(cipherText).decode('utf-8'),
        'tags': tags
    }

    with open(fileName, 'w') as f:
        json.dump(encrypted_data, f)

def decryptFromFile(password, fileName, tag=None):
    #download from drive - todo
    with open(fileName, 'r') as f:
        encrypted_data = json.load(f)

    salt = base64.b64decode(encrypted_data['salt'])
    nonce = base64.b64decode(encrypted_data['nonce'])
    authTag = base64.b64decode(encrypted_data['authTag'])
    cipherText = base64.b64decode(encrypted_data['cipherText'])
    tags = encrypted_data['tags']

    key = generateKey(password, salt)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

    try:
        plainText = cipher.decrypt_and_verify(cipherText, authTag)
        decrypted_data = plainText.decode('utf-8')
    except ValueError:
        return -1

    if tag is not None:
        decrypted_tags = json.loads(decrypted_data)
        if tag not in decrypted_tags:
            return -2
        return decrypted_tags[tag]
    else:
        return decrypted_data


def decryptFromDriveFile(password, fileName,folder_name, tag=None):
    drive_service = authenticate_google_drive()
    folder_id = get_folder_id(drive_service, folder_name)
    file_id = get_file_id_by_name(drive_service, fileName, parent_id=folder_id)
    file_content = read_file(drive_service, file_id)

    print(file_content)
    print(type(file_content))
    
    encrypted_data = json.loads(file_content)

    salt = base64.b64decode(encrypted_data['salt'])
    nonce = base64.b64decode(encrypted_data['nonce'])
    authTag = base64.b64decode(encrypted_data['authTag'])
    cipherText = base64.b64decode(encrypted_data['cipherText'])
    tags = encrypted_data['tags']

    key = generateKey(password, salt)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

    try:
        plainText = cipher.decrypt_and_verify(cipherText, authTag)
        decrypted_data = plainText.decode('utf-8')
    except ValueError:
        return -1

    if tag is not None:
        decrypted_tags = json.loads(decrypted_data)
        if tag not in decrypted_tags:
            return -2
        return decrypted_tags[tag]
    else:
        return decrypted_data

# Usage

# uinfo = ["Chase", "jxk10000", "SuperSecRetPassWord"]
# bdetails = ["1110009988", "123456789"]

# pwd = uinfo[2]
# ptext = json.dumps({"Social-Security": bdetails[1], "Bank-Acc": bdetails[0]})
# fname = uinfo[1] + ".encrypted"

# Encrypt data with tags
# encryptToFile(ptext, pwd, fname, tags=["Social-Security", "Bank-Acc"])

# Decrypt and retrieve specific tag
# print("Trying to decrypt ssn...")
# dtext = decryptFromFile(pwd, fname, tag="Social-Security")
# print(dtext)

# Decrypt and retrieve specific tag
# print("Trying to decrypt bank acc...")
# dtext = decryptFromFile(pwd, fname, tag="Bank-Acc")
# print(dtext)
 
# Decrypt and retrieve all tags
# print("All data...")
# dtext_all = decryptFromFile(pwd, fname)
# dtext_all = json.loads(dtext_all)
# print(type(dtext_all))
# print(dtext_all)

