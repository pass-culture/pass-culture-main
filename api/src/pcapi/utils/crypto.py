from hashlib import md5

import bcrypt

from pcapi import settings


def _hash_password_with_bcrypt(clear_text: str) -> bytes:
    return bcrypt.hashpw(clear_text.encode("utf-8"), bcrypt.gensalt())


def _check_password_with_bcrypt(clear_text: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(clear_text.encode("utf-8"), hashed)


def _hash_password_with_md5(clear_text: str) -> bytes:
    if not settings.USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM:
        raise RuntimeError("This password hasher should not be used in this environment.")
    return md5(clear_text.encode("utf-8")).hexdigest().encode("utf-8")


def _check_password_with_md5(clear_text: str, hashed: bytes) -> bool:
    if not settings.USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM:
        raise RuntimeError("This password hasher should not be used in this environment.")
    # non constant-time comparison is fine, it's only used in tests
    return _hash_password_with_md5(clear_text) == hashed


def hash_password(clear_text: str) -> bytes:
    if settings.USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM:
        hasher = _hash_password_with_md5
    else:
        hasher = _hash_password_with_bcrypt
    return hasher(clear_text)


def check_password(clear_text: str, hashed: bytes) -> bool:
    if settings.USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM:
        checker = _check_password_with_md5
    else:
        checker = _check_password_with_bcrypt
    return checker(clear_text, hashed)
