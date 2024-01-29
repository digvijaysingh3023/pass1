from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
import base64
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import json
# # AES 'pad' byte array to multiple of BLOCK_SIZE bytes

# def pad(m):
#     return m+chr(16-len(m)%16)*(16-len(m)%16)
# def unpad(ct):
#     return ct[:-ct[-1]]

salt=b'\xb9{>\n)O&;\xc0\\\xd7C\xd9\xe6\x8e\x004\xd6\x8c\x0c\xb8\x83\xb2\x8f\xd7\x0f\x1a\xd7M\x12\xb4a'
key = PBKDF2("password",salt,dkLen=32)
def encrypt(dictionary, key):
    # Convert dictionary to JSON string
    json_data = json.dumps(dictionary)
    cipher = AES.new(key, AES.MODE_CBC)
    padded_data = pad(json_data.encode('ISO-8859-1'), AES.block_size)
    ciphertext = cipher.encrypt(padded_data)
    return  base64.b64encode(ciphertext)
en = encrypt({
    "err_des": {
        "error": 0,
        "pass": 1
    },
    "status": "Pending",
    "time": "2024-01-19T17:57:31.825189Z",
    "amount": 750,
    "Email": "s.sanyal@iitg.ac.in"
},key)
# print(en)
def decrypt(key, message):
    messagebytes = base64.b64decode(message)

    cipher = AES.new(key, AES.MODE_CBC)

    decrypted_padded = cipher.decrypt(messagebytes)
    decrypted = unpad(decrypted_padded, AES.block_size)


    return (decrypted.decode('ISO-8859-1'))
# print(decrypt(key,en))