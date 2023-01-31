from .create_institutions import create_institutions
from .create_offers import create_offers
from .create_users_and_offerers import create_users_offerers
from .create_venues import create_venues


def create_eac_data() -> None:
    institutions = create_institutions()
    offerers = create_users_offerers()
    create_venues(offerers)
    create_offers(offerers=offerers, institutions=institutions)
