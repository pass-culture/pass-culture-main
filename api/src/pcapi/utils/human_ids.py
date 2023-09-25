from base64 import b32encode

import click

from pcapi.utils.blueprint import Blueprint


# This library creates IDs for use in our URLs,
# trying to achieve a balance between having a short
# length and being usable by humans
# We use base32, but replace O and I, which can be mistaken for 0 and 1
# by 8 and 9


blueprint = Blueprint(__name__, __name__)


def humanize(integer: int | None) -> str | None:
    """Create a human-compatible ID from and integer"""
    if integer is None:
        return None
    b32 = b32encode(int_to_bytes(integer))
    return b32.decode("ascii").replace("O", "8").replace("I", "9").rstrip("=")


def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, "big")


@blueprint.cli.command("humanize")
@click.argument("int_ids", nargs=-1, required=True, type=int)
def command_humanize(int_ids: tuple[int]) -> None:
    """Print humanized version of the requested identifier(s)."""
    for int_id in int_ids:
        print(humanize(int_id))
