from pcapi.core.external_bookings.api import disable_external_bookings
from pcapi.sandboxes.scripts.creators.industrial import save_industrial_ci_sandbox
from pcapi.sandboxes.scripts.creators.industrial import save_industrial_sandbox
from pcapi.sandboxes.scripts.creators.test_cases import save_test_cases_sandbox


def save_sandbox() -> None:
    save_test_cases_sandbox()
    save_industrial_sandbox()
    disable_external_bookings()


def save_ci_sandbox() -> None:
    save_industrial_ci_sandbox()
    disable_external_bookings()
