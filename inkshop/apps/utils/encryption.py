import binascii
import base64
import codecs
import hashlib
import logging
from Crypto.Cipher import AES
import random
import os
import traceback

from binascii import hexlify, unhexlify
from simplecrypt import encrypt as simple_encrypt
from simplecrypt import decrypt as simple_decrypt
from django.conf import settings


BS = 16
key = hashlib.sha256(settings.INKSHOP_ENCRYPTION_KEY.encode("utf-8")).digest()


def pad(s):
    s = "%s%s" % (s.decode("utf-8"), ((BS - len(s) % BS) * "~"))
    return s


def unpad(s):
    while s.endswith(str.encode("~")):
        s = s[:-1]
    return s


def encrypt(s):
    if settings.DISABLE_ENCRYPTION_FOR_TESTS:
        return s
    return hexlify(simple_encrypt(settings.INKSHOP_ENCRYPTION_KEY, s.encode('utf8'))).decode()


def decrypt(s):
    if settings.DISABLE_ENCRYPTION_FOR_TESTS:
        return s
    return simple_decrypt(settings.INKSHOP_ENCRYPTION_KEY, unhexlify(s)).decode('utf-8')


def normalize_lower_and_encrypt(s):
    return encrypt(s.strip().lower())


def normalize_and_encrypt(s):
    return encrypt(s.strip())


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
