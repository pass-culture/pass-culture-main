""" human_ids """
from base64 import b32decode
from base64 import b32encode
import binascii


# This library creates IDs for use in our URLs,
# trying to achieve a balance between having a short
# length and being usable by humans
# We use base32, but replace O and I, which can be mistaken for 0 and 1
# by 8 and 9


class NonDehumanizableId(Exception):
    pass


def dehumanize(public_id: str) -> int:
    if public_id is None:
        return None
    missing_padding = len(public_id) % 8
    if missing_padding != 0:
        public_id += "=" * (8 - missing_padding)
    try:
        xbytes = b32decode(public_id.replace("8", "O").replace("9", "I"))
    except binascii.Error:
        raise NonDehumanizableId("id non dehumanizable")
    return int_from_bytes(xbytes)


def humanize(integer: int) -> str:
    """Create a human-compatible ID from and integer"""
    if integer is None:
        return None
    b32 = b32encode(int_to_bytes(integer))
    return b32.decode("ascii").replace("O", "8").replace("I", "9").rstrip("=")


def dehumanize_ids_list(humanized_list: list[str]) -> list[int]:
    return list(map(dehumanize, humanized_list)) if humanized_list else []


def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, "big")


def int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, "big")
