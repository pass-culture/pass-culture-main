from base64 import b32decode
from base64 import b32encode
import binascii

import click

from pcapi.utils.blueprint import Blueprint


# This library creates IDs for use in our URLs,
# trying to achieve a balance between having a short
# length and being usable by humans
# We use base32, but replace O and I, which can be mistaken for 0 and 1
# by 8 and 9


blueprint = Blueprint(__name__, __name__)


class NonDehumanizableId(Exception):
    pass


def dehumanize(public_id: str | None) -> int | None:
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


def dehumanize_or_raise(public_id: str | None) -> int:
    dehumanized_public_id = dehumanize(public_id)
    if dehumanized_public_id is None:
        raise ValueError()
    return dehumanized_public_id


def humanize(integer: int | None) -> str | None:
    """Create a human-compatible ID from and integer"""
    if integer is None:
        return None
    b32 = b32encode(int_to_bytes(integer))
    return b32.decode("ascii").replace("O", "8").replace("I", "9").rstrip("=")


def dehumanize_ids_list(humanized_list: list[str | None]) -> list[int | None]:
    return list(map(dehumanize, humanized_list)) if humanized_list else []


def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, "big")


def int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, "big")


@blueprint.cli.command("humanize")
@click.argument("int_ids", nargs=-1, required=True, type=int)
def command_humanize(int_ids: tuple[int]):  # type: ignore [no-untyped-def]
    """Print humanized version of the requested identifier(s)."""
    for int_id in int_ids:
        print(humanize(int_id))


@blueprint.cli.command("dehumanize")
@click.argument("human_ids", nargs=-1, required=True, type=str)
def command_dehumanize(human_ids: tuple[str]):  # type: ignore [no-untyped-def]
    """Print integer value of the requested humanized identifier(s)."""
    for human_id in human_ids:
        print(dehumanize(human_id))
