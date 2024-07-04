import logging

from pcapi.core.offerers import factories as offerers_factories


logger = logging.getLogger(__name__)


def create_industrial_venues_with_timezone() -> None:
    logger.info("create_industrial_venues_with_timezone")
    offerer = offerers_factories.OffererFactory(name="Structure avec différentes timezones")
    offerers_factories.UserOffererFactory(offerer=offerer, user__email="offerer_with_timezone@exemple.com")

    # The virtual venue (so it will be on Europe/Paris)
    offerers_factories.VirtualVenueFactory(managingOfferer=offerer)

    # America/Cayenne
    offerers_factories.VenueFactory(
        publicName="America/Cayenne",
        managingOfferer=offerer,
        timezone="America/Cayenne",
        departementCode="973",
        postalCode="97300",
    )

    # Indian/Reunion
    offerers_factories.VenueFactory(
        publicName="Indian/Reunion",
        managingOfferer=offerer,
        timezone="Indian/Reunion",
        departementCode="974",
        postalCode="97415",
    )

    # Pacific/Noumea
    offerers_factories.VenueFactory(
        publicName="Pacific/Noumea",
        managingOfferer=offerer,
        timezone="Pacific/Noumea",
        departementCode="988",
        postalCode="98800",
    )

    # Timezone with winter & summer time
    # Europe/Paris
    offerers_factories.VenueFactory(
        publicName="Europe/Paris",
        managingOfferer=offerer,
        timezone="Europe/Paris",
        departementCode="78",
        postalCode="78220",
    )

    # America/Miquelon
    offerers_factories.VenueFactory(
        publicName="America/Miquelon",
        managingOfferer=offerer,
        timezone="America/Miquelon",
        departementCode="975",
        postalCode="97500",
    )

    # Pacific/Pitcairn (Clipperton) has no inhabitants, so I don't create venue for it
