from binascii import hexlify
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.SecretSharing import Shamir

# Generate a random key
key = get_random_bytes(16)

# Split the key into 3 shares, requiring at least 2 to reconstruct
shares = Shamir.split(2, 3, key)

# Print the shares in printable hexadecimal format
for idx, share in shares:
    print(f"Index #{idx}: {share.hex()}")

# Encrypt the file using the key
with open("D:\Spring23\CS6348\Project\clear.txt", "rb") as fi, open("D:\Spring23\CS6348\Project\enc.txt", "wb") as fo:
    cipher = AES.new(key, AES.MODE_EAX)
    ct, tag = cipher.encrypt(fi.read()), cipher.digest()
    fo.write(cipher.nonce + tag + ct)
