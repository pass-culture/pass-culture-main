from pcapi.sandboxes.scripts.creators.big.create_big_offerer import create_big_offerer
from pcapi.sandboxes.scripts.creators.big.create_books import create_books


def save_big_sandbox() -> None:
    create_big_offerer()
    create_books(10000)
