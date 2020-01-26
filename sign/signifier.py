from collections import namedtuple

from Crypto.PublicKey import RSA

from .rsa import sign_message, verify_sign


class Signature:
    def __init__(self, public_key: bytearray, sign: bytearray):
        self.public_key = public_key
        self.sign = sign


class Signifier:
    def __init__(self, public_key: bytearray, private_key: bytearray):
        self._public_key = RSA.import_key(public_key)
        self._public_key_der = self._public_key.export_key('DER')
        self._private_key = RSA.import_key(private_key)

    @staticmethod
    def from_files(public_key_path, private_key_path):
        public_key = open(public_key_path).read()
        private_key = open(private_key_path).read()
        return Signifier(public_key, private_key)

    def sign(self, data: bytearray) -> Signature:
        return Signature(
            public_key=self._public_key_der,
            sign=sign_message(data, self._private_key)
        )

    @staticmethod
    def verify(data: bytearray, signature: Signature):
        return verify_sign(data, RSA.import_key(signature.public_key), signature.sign)
