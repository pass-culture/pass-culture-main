from hashlib import md5
from hashlib import sha3_512
from secrets import compare_digest
from secrets import token_hex

import bcrypt
from cryptography.fernet import Fernet

from pcapi import settings


def _hash_password_with_bcrypt(clear_text: str) -> bytes:
    return bcrypt.hashpw(clear_text.encode("utf-8"), bcrypt.gensalt())


def _check_password_with_bcrypt(clear_text: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(clear_text.encode("utf-8"), hashed)


def _hash_password_with_md5(clear_text: str) -> bytes:
    if not settings.USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM:
        raise RuntimeError("This password hasher should not be used in this environment.")
    return md5(clear_text.encode("utf-8")).hexdigest().encode("utf-8")


def _hash_password_with_sha3_512(clear_text: str, salt: bytes = b"") -> bytes:
    """Hash a password using SHA3-512. output format: $sha3_512$salt$hashed_password"""
    if not salt:
        salt = token_hex(16).encode("utf-8")
    hashed_password = sha3_512(clear_text.encode("utf-8") + salt).hexdigest().encode("utf-8")
    return b"$".join([b"$sha3_512", salt, hashed_password])


def _check_password_with_md5(clear_text: str, hashed: bytes) -> bool:
    if not settings.USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM:
        raise RuntimeError("This password hasher should not be used in this environment.")
    # non constant-time comparison is fine, it's only used in tests
    return _hash_password_with_md5(clear_text) == hashed


def _check_password_with_sha3_512(clear_text: str, hashed: bytes) -> bool:
    salt = hashed.decode().split("$")[2].encode("utf-8")
    return compare_digest(_hash_password_with_sha3_512(clear_text, salt), hashed)


def hash_password(clear_text: str) -> bytes:
    if settings.USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM:
        hasher = _hash_password_with_md5
    else:
        hasher = _hash_password_with_bcrypt
    try:
        return hasher(clear_text)
    except UnicodeEncodeError:
        raise ValueError("non-unicode characters are not allowed in passwords")


def hash_public_api_key(clear_text: str) -> bytes:
    if settings.USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM:
        return _hash_password_with_md5(clear_text)
    return _hash_password_with_sha3_512(clear_text)


def check_password(clear_text: str, hashed: bytes) -> bool:
    if settings.USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM:
        checker = _check_password_with_md5
    else:
        checker = _check_password_with_bcrypt
    return checker(clear_text, hashed)


def check_public_api_key(clear_text: str, hashed: bytes) -> bool:
    if settings.USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM:
        return _check_password_with_md5(clear_text, hashed)
    return _check_password_with_sha3_512(clear_text, hashed)


def encrypt(clear_text: str) -> str:
    fernet = Fernet(settings.SECRET_ENCRYPTION_KEY)
    encrypted_text = fernet.encrypt(clear_text.encode())
    return encrypted_text.decode()


def decrypt(encrypted_text: str) -> str:
    fernet = Fernet(settings.SECRET_ENCRYPTION_KEY)
    clear_text = fernet.decrypt(encrypted_text.encode())
    return clear_text.decode()
