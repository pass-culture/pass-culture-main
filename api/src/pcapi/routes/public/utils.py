import base64
import binascii


class InvalidBase64Exception(Exception):
    pass


def get_bytes_from_base64_string(base64_string: str) -> bytes:
    """Return the bytes from a base64 string."""
    try:
        return base64.b64decode(base64_string.encode("utf-8"))
    except binascii.Error as error:
        raise InvalidBase64Exception() from error
