from collections import namedtuple

from Crypto.PublicKey import RSA

from .rsa import sign_message, verify_sign

Signature = namedtuple('Signature', ['public_key', 'sign'])


class Signifier:
    def __init__(self, public_key_path, private_key_path):
        return
        self._public_key = RSA.import_key(open(public_key_path).read())
        self._private_key = RSA.import_key(open(private_key_path).read())

    def sign(self, data: bytearray) -> Signature:
        return Signature(public_key=b'some key', sign=b'some sign')
        return Signature(public_key=self._public_key, sign=sign_message(data, self._private_key))

    @staticmethod
    def verify(data: bytearray, signature: Signature):
        return True
        return verify_sign(data, signature.public_key, signature.sign)
