import logging

from pcapi.core.offerers import factories as offerers_factories
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


logger = logging.getLogger(__name__)


@log_func_duration
def create_industrial_venues_with_timezone() -> None:
    logger.info("create_industrial_venues_with_timezone")
    offerer = offerers_factories.OffererFactory.create(name="Structure avec différentes timezones")
    offerers_factories.UserOffererFactory.create(offerer=offerer, user__email="offerer_with_timezone@exemple.com")

    # America/Cayenne
    offerers_factories.VenueFactory.create(
        publicName="America/Cayenne",
        managingOfferer=offerer,
        offererAddress__address__timezone="America/Cayenne",
        offererAddress__address__departmentCode="973",
        offererAddress__address__postalCode="97300",
    )

    # Indian/Reunion
    offerers_factories.VenueFactory.create(
        publicName="Indian/Reunion",
        managingOfferer=offerer,
        offererAddress__address__timezone="Indian/Reunion",
        offererAddress__address__departmentCode="974",
        offererAddress__address__postalCode="97415",
    )

    # Pacific/Noumea
    offerers_factories.VenueFactory.create(
        publicName="Pacific/Noumea",
        managingOfferer=offerer,
        offererAddress__address__timezone="Pacific/Noumea",
        offererAddress__address__departmentCode="988",
        offererAddress__address__postalCode="98800",
    )

    # Timezone with winter & summer time
    # Europe/Paris
    offerers_factories.VenueFactory.create(
        publicName="Europe/Paris",
        managingOfferer=offerer,
        offererAddress__address__timezone="Europe/Paris",
        offererAddress__address__departmentCode="78",
        offererAddress__address__postalCode="78220",
    )

    # America/Miquelon
    offerers_factories.VenueFactory.create(
        publicName="America/Miquelon",
        managingOfferer=offerer,
        offererAddress__address__timezone="America/Miquelon",
        offererAddress__address__departmentCode="975",
        offererAddress__address__postalCode="97500",
    )

    # Pacific/Pitcairn (Clipperton) has no inhabitants, so I don't create venue for it
