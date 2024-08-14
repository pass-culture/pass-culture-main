from pcapi.core.external_bookings.api import disable_external_bookings
from pcapi.sandboxes.scripts.creators.e2e import save_e2e_sandbox
from pcapi.sandboxes.scripts.creators.e2e.create_e2e_mediations import prepare_mediations_folders
from pcapi.sandboxes.scripts.creators.test_cases import save_test_cases_sandbox


def save_sandbox() -> None:
    prepare_mediations_folders()
    save_test_cases_sandbox()
    save_e2e_sandbox()
    disable_external_bookings()
