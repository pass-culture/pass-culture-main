from pcapi.sandboxes.scripts.creators.industrial.create_industrial_eac_data.create_offers import (
    create_national_programs_and_domains,
)
from pcapi.sandboxes.scripts.creators.industrial.create_role_permissions import create_roles_with_permissions
from pcapi.sandboxes.scripts.creators.tiny.create_user_with_venue import create_tiny_venue
from pcapi.sandboxes.scripts.getters.pro import create_adage_environment


def save_tiny_sandbox() -> None:
    create_roles_with_permissions()
    create_national_programs_and_domains()
    create_adage_environment()
    create_tiny_venue()
