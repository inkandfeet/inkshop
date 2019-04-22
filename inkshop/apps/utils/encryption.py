import binascii
import base64
import codecs
import hashlib
import logging
# from Crypto.Cipher import AES
import random
import os
import traceback

from binascii import hexlify, unhexlify
# from simplecrypt import encrypt as simple_encrypt
# from simplecrypt import decrypt as simple_decrypt
from django.conf import settings

# Cryptography
# https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
from cryptography.fernet import Fernet, MultiFernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
password = settings.INKSHOP_ENCRYPTION_KEY.encode("utf-8")
salt = os.urandom(16)
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
    backend=default_backend()
)
key = Fernet(base64.urlsafe_b64encode(kdf.derive(password)))

# Future support for key rotation
# https://cryptography.io/en/latest/fernet/#cryptography.fernet.MultiFernet
# f = MultiFernet([key, ])
f = key


def encrypt(s):
    if not s:
        return None
    if settings.DISABLE_ENCRYPTION_FOR_TESTS:
        return s
    return f.encrypt(s.encode('utf-8')).decode()


def decrypt(s):
    if not s:
        return None
    if settings.DISABLE_ENCRYPTION_FOR_TESTS:
        return s
    return f.decrypt(s.encode('utf-8')).decode('utf-8')


def encrypt_bytes(s):
    if not s:
        return None
    if settings.DISABLE_ENCRYPTION_FOR_TESTS:
        return s
    return f.encrypt(s)


def decrypt_bytes(s):
    if not s:
        return None
    if settings.DISABLE_ENCRYPTION_FOR_TESTS:
        return s
    return f.decrypt(s)


def normalize_lower_and_encrypt(s):
    return encrypt(s.strip().lower())


def normalize_and_encrypt(s):
    return encrypt(s.strip())


def lookup_hash(s):
    h = hashlib.new('SHA512')
    h.update(str("%s%s" % (settings.HASHID_SALT, str(s).strip().lower())).encode('utf-8'))
    return h.hexdigest()


# From Will:
# https://github.com/skoczen/will/blob/master/will/backends/encryption/aes.py
# def encrypt(raw):
#     try:
#         enc = binascii.b2a_base64(raw, -1)
#         iv = binascii.b2a_hex(os.urandom(8))
#         cipher = AES.new(key, AES.MODE_CBC, iv)
#         enc = binascii.b2a_base64(cipher.encrypt(pad(enc)))
#         return "%s/%s" % (iv.decode("utf-8"), enc.decode("utf-8"))

#     except:
#         logging.critical("Error encrypting: \n%s" % traceback.format_exc())
#         return None


# def decrypt(raw_enc):
#     try:
#         iv = raw_enc[:BS]
#         enc = raw_enc[BS + 1:]
#         cipher = AES.new(key, AES.MODE_CBC, iv)
#         enc = unpad(cipher.decrypt(binascii.a2b_base64(enc)))
#         return binascii.a2b_base64(enc)
#     except (KeyboardInterrupt, SystemExit):
#         pass
#     except:
#         logging.critical("Error decrypting. ")
#         return binascii.a2b_base64(raw_enc)
