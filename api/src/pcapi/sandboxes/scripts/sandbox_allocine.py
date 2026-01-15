from pcapi.sandboxes.scripts.creators.allocine import save_allocine_sandbox
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_eac_data.create_offers import (
    create_national_programs_and_domains,
)


def save_sandbox() -> None:
    create_national_programs_and_domains()
    save_allocine_sandbox()
