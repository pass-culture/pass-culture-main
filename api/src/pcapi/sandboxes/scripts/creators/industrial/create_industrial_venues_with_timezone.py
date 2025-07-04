import logging

from pcapi.core.offerers import factories as offerers_factories
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


logger = logging.getLogger(__name__)


@log_func_duration
def create_industrial_venues_with_timezone() -> None:
    logger.info("create_industrial_venues_with_timezone")
    offerer = offerers_factories.OffererFactory.create(name="Structure avec différentes timezones")
    offerers_factories.UserOffererFactory.create(offerer=offerer, user__email="offerer_with_timezone@exemple.com")

    # The virtual venue (so it will be on Europe/Paris)
    offerers_factories.VirtualVenueFactory.create(managingOfferer=offerer)

    # America/Cayenne
    offerers_factories.VenueFactory.create(
        publicName="America/Cayenne",
        managingOfferer=offerer,
        timezone="America/Cayenne",
        departementCode="973",
        postalCode="97300",
    )

    # Indian/Reunion
    offerers_factories.VenueFactory.create(
        publicName="Indian/Reunion",
        managingOfferer=offerer,
        timezone="Indian/Reunion",
        departementCode="974",
        postalCode="97415",
    )

    # Pacific/Noumea
    offerers_factories.VenueFactory.create(
        publicName="Pacific/Noumea",
        managingOfferer=offerer,
        timezone="Pacific/Noumea",
        departementCode="988",
        postalCode="98800",
    )

    # Timezone with winter & summer time
    # Europe/Paris
    offerers_factories.VenueFactory.create(
        publicName="Europe/Paris",
        managingOfferer=offerer,
        timezone="Europe/Paris",
        departementCode="78",
        postalCode="78220",
    )

    # America/Miquelon
    offerers_factories.VenueFactory.create(
        publicName="America/Miquelon",
        managingOfferer=offerer,
        timezone="America/Miquelon",
        departementCode="975",
        postalCode="97500",
    )

    # Pacific/Pitcairn (Clipperton) has no inhabitants, so I don't create venue for it
