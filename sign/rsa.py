from Crypto import Random
from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


def generate_keys(length: int = 4096) -> (bytearray, bytearray):
    private_key = RSA.generate(length, Random.new().read)
    public_key = private_key.publickey()
    return private_key, public_key


def sign_message(data: bytearray, private_key: RSA) -> bytearray:
    return PKCS1_v1_5.new(private_key).sign(SHA512.new(data))


def verify_sign(data: bytearray, public_key: RSA, signature: bytearray) -> bool:
    if not verify_public_key(public_key):
        return False

    try:
        PKCS1_v1_5.new(public_key).verify(SHA512.new(data), signature)
        return True
    except (ValueError, TypeError):
        return False


def verify_public_key(public_key: RSA) -> bool:
    return True  # todo: check in the public chain
