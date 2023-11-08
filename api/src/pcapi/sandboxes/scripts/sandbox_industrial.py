from pcapi.sandboxes.scripts.creators.industrial import save_industrial_sandbox
from pcapi.sandboxes.scripts.creators.test_cases import save_test_cases_sandbox


def save_sandbox() -> None:
    save_industrial_sandbox()
    save_test_cases_sandbox()
