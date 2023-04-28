from binascii import unhexlify
from Crypto.Cipher import AES
from Crypto.Protocol.SecretSharing import Shamir

# Prompt the user to enter the shares
shares = []
for x in range(2):
    in_str = input("Enter index and share separated by comma: ")
    idx, share = [str(s).strip() for s in in_str.split(",")]
    shares.append((int(idx), bytes.fromhex(share)))

# Print the shares that were entered
for idx, share in shares:
    print(f"Index #{idx}: {share.hex()}")

# Combine the shares to reconstruct the key
key = Shamir.combine(shares)

# Decrypt the file using the key
with open("D:\Spring23\CS6348\Project\enc.txt", "rb") as fi:
    nonce, tag = [fi.read(16) for x in range(2)]
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    try:
        result = cipher.decrypt(fi.read())
        cipher.verify(tag)
        with open("D:\Spring23\CS6348\Project\clear2.txt", "wb") as fo:
            fo.write(result)
        print ("Success")
    except ValueError:
        print("The shares were incorrect")