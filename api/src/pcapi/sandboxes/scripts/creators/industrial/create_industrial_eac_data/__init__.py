from pcapi.sandboxes.scripts.creators.industrial.create_industrial_eac_data.create_institutions import (
    create_institutions,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_eac_data.create_institutions import (
    create_institutions_with_deposits_by_period,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_eac_data.create_offers import create_eac_offers
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_eac_data.create_offers import (
    create_eac_offers_by_period,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_eac_data.create_users_and_offerers import (
    create_eac_users_offerers,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_eac_data.create_venues import create_eac_venues
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_eac_data.fill import fill_adage_playlists
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


@log_func_duration
def create_eac_data() -> None:
    institutions = create_institutions()
    deposits = create_institutions_with_deposits_by_period()

    offerers = create_eac_users_offerers()
    create_eac_venues(offerers)

    create_eac_offers(offerers=offerers, institutions=institutions)
    create_eac_offers_by_period(offerers=offerers, deposits=deposits)

    fill_adage_playlists()
