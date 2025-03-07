from pcapi.sandboxes.scripts.creators.industrial.create_industrial_eac_data.create_institutions import (
    create_institutions,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_eac_data.create_offers import create_offers
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_eac_data.create_users_and_offerers import (
    create_users_offerers,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_eac_data.create_venues import create_venues
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_eac_data.fill import fill_adage_playlists


def create_eac_data() -> None:
    institutions = create_institutions()
    offerers = create_users_offerers()
    create_venues(offerers)
    create_offers(offerers=offerers, institutions=institutions)

    fill_adage_playlists()
