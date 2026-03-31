from pcapi.sandboxes.scripts.creators.industrial.create_bookings_scale import create_bookings_scale_sandbox
from pcapi.sandboxes.scripts.creators.industrial.create_role_permissions import create_roles_with_permissions
from pcapi.sandboxes.scripts.getters.pro import create_adage_environment


def save_sandbox() -> None:
    create_roles_with_permissions()
    create_adage_environment()
    create_bookings_scale_sandbox()
