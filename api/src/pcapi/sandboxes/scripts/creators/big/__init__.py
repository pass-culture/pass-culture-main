from pcapi.sandboxes.scripts.creators.big.create_big_offerer import create_big_offerer
from pcapi.sandboxes.scripts.creators.big.create_books import create_books
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_eac_data.create_offers import (
    create_national_programs_and_domains,
)


def save_big_sandbox() -> None:
    create_national_programs_and_domains()
    create_big_offerer()
    create_books(10000)
