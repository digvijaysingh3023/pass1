# from Crypto.Cipher import AES
# from Crypto.Util.Padding import pad,unpad
# import base64
# from Crypto.Protocol.KDF import PBKDF2
# from Crypto.Random import get_random_bytes
# import json
# # # AES 'pad' byte array to multiple of BLOCK_SIZE bytes

# # def pad(m):
# #     return m+chr(16-len(m)%16)*(16-len(m)%16)
# # def unpad(ct):
# #     return ct[:-ct[-1]]

# salt=b'\xb9{>\n)O&;\xc0\\\xd7C\xd9\xe6\x8e\x004\xd6\x8c\x0c\xb8\x83\xb2\x8f\xd7\x0f\x1a\xd7M\x12\xb4a'
# key = PBKDF2("password",salt,dkLen=32)
# def encrypt(dictionary, key):
#     # Convert dictionary to JSON string
#     json_data = json.dumps(dictionary)
#     cipher = AES.new(key, AES.MODE_CBC)
#     padded_data = pad(json_data.encode('ISO-8859-1'), AES.block_size)
#     ciphertext = cipher.encrypt(padded_data)
#     return  base64.b64encode(ciphertext)
# en = encrypt({
#     "err_des": {
#         "error": 0,
#         "pass": 1
#     },
#     "status": "Pending",
#     "time": "2024-01-19T17:57:31.825189Z",
#     "amount": 750,
#     "Email": "s.sanyal@iitg.ac.in"
# },key)
# # print(en)
# def decrypt(key, message):
#     messagebytes = base64.b64decode(message)

#     cipher = AES.new(key, AES.MODE_CBC)

#     decrypted_padded = cipher.decrypt(messagebytes)
#     decrypted = unpad(decrypted_padded, AES.block_size)


#     return (decrypted.decode('ISO-8859-1'))
# # print(decrypt(key,en))










import base64
import hashlib
import json
from Cryptodome.Cipher import AES  # from pycryptodomex v-3.10.4
from Cryptodome.Random import get_random_bytes

HASH_NAME = "SHA512"
IV_LENGTH = 12
ITERATION_COUNT = 65535
KEY_LENGTH = 32
SALT_LENGTH = 16
TAG_LENGTH = 16


def get_secret_key(password, salt):
    return hashlib.pbkdf2_hmac(
        HASH_NAME, password.encode(), salt, ITERATION_COUNT, KEY_LENGTH
    )
def encrypt(password, plain_message):
    salt = get_random_bytes(SALT_LENGTH) 
    iv = get_random_bytes(IV_LENGTH)
    plain_message=json.dumps(plain_message)
    secret = get_secret_key(password, salt)

    cipher = AES.new(secret, AES.MODE_GCM, iv)

    encrypted_message_byte, tag = cipher.encrypt_and_digest(
        plain_message.encode("utf-8")
    )
    cipher_byte = salt + iv + encrypted_message_byte + tag

    encoded_cipher_byte = base64.b64encode(cipher_byte)
    return bytes.decode(encoded_cipher_byte)

# en = encrypt("alcherpass24",{
#     "err_des": {
#         "error": 0,
#         "pass": 1
#     },
#     "status": "Pending",
#     "time": "2024-01-19T17:57:31.825189Z",
#     "amount": 750,
#     "Email": "s.sanyal@iitg.ac.in"
# })
# print(en)

# def decrypt(password, cipher_message):
#     decoded_cipher_byte = base64.b64decode(cipher_message)

#     salt = decoded_cipher_byte[:SALT_LENGTH]
#     # iv = decoded_cipher_byte[SALT_LENGTH : (SALT_LENGTH + IV_LENGTH)]
#     encrypted_message_byte = decoded_cipher_byte[
#         (SALT_LENGTH) : -TAG_LENGTH
#     ]
#     tag = decoded_cipher_byte[-TAG_LENGTH:]
#     secret = get_secret_key(password, salt)
#     cipher = AES.new(secret, AES.MODE_GCM)

#     decrypted_message_byte = cipher.decrypt_and_verify(encrypted_message_byte, tag)
#     return decrypted_message_byte.decode("utf-8")
# de = decrypt("alcherpass24", en)
# print(de)




outputFormat = "{:<25}:{}"
secret_key = "your_secure_key"
plain_text = "Your_plain_text"