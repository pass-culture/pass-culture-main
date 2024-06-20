from pcapi.core.external_bookings.api import disable_external_bookings
from pcapi.sandboxes.scripts.creators.industrial import save_industrial_sandbox
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_mediations import prepare_mediations_folders
from pcapi.sandboxes.scripts.creators.test_cases import save_test_cases_sandbox


def save_sandbox() -> None:
    prepare_mediations_folders()
    save_test_cases_sandbox()
    save_industrial_sandbox()
    disable_external_bookings()
