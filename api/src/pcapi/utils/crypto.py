from hashlib import md5

import bcrypt

from pcapi import settings


def _hash_password_with_bcrypt(clear_text: str) -> bytes:
    return bcrypt.hashpw(clear_text.encode("utf-8"), bcrypt.gensalt())


def _check_password_with_bcrypt(clear_text: str, hashed: str) -> bool:
    return bcrypt.checkpw(clear_text.encode("utf-8"), hashed)  # type: ignore [arg-type]


def _hash_password_with_md5(clear_text: str) -> bytes:
    if not settings.IS_DEV:
        raise RuntimeError("This password hasher should not be used outside tests.")
    return md5(clear_text.encode("utf-8")).hexdigest().encode("utf-8")


def _check_password_with_md5(clear_text: str, hashed: str) -> bool:
    if not settings.IS_DEV:
        raise RuntimeError("This password hasher should not be used outside tests.")
    # non constant-time comparison because it's test-only
    return _hash_password_with_md5(clear_text) == hashed


def hash_password(clear_text: str) -> bytes:
    hasher = _hash_password_with_md5 if settings.IS_DEV else _hash_password_with_bcrypt
    return hasher(clear_text)


def check_password(clear_text: str, hashed: str) -> bool:
    checker = _check_password_with_md5 if settings.IS_DEV else _check_password_with_bcrypt
    return checker(clear_text, hashed)
