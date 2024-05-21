import logging
import random
import re

import pcapi.core.finance.factories as finance_factories
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.sandboxes.scripts.mocks.venue_mocks import MOCK_NAMES


logger = logging.getLogger(__name__)

DEFAULT_VENUE_IMAGES = 4
VENUE_IMAGE_INDEX_START_AT = 21


def add_default_image_to_venue(image_venue_counter: int, offerer: Offerer, venue: Venue) -> None:
    image_number = image_venue_counter + VENUE_IMAGE_INDEX_START_AT
    with open(
        f"./src/pcapi/sandboxes/thumbs/generic_pictures/Picture_0{image_number}.jpg",
        mode="rb",
    ) as file:
        offerers_api.save_venue_banner(
            user=offerer.UserOfferers[0].user,
            venue=venue,
            content=file.read(),
            image_credit="industrial sandbox picture provider",
        )


def create_data_venues(offerers_by_name: dict) -> dict[str, Venue]:
    logger.info("create_data_venues")

    venue_by_name = {}
    mock_index = 0

    iban_count = 0
    iban_prefix = "FR7630001007941234567890185"
    bic_prefix, bic_suffix = "QSDFGH8Z", 556
    application_id_prefix = "52"

    image_venue_counter = 0

    for offerer_index, (offerer_name, offerer) in enumerate(offerers_by_name.items()):
        geoloc_match = re.match(r"(.*)lat\:(.*) lon\:(.*)", offerer_name)

        venue_name = f"{MOCK_NAMES[mock_index % len(MOCK_NAMES)]} DATA"

        # create all possible cases:
        # offerer with or without iban / venue with or without iban
        iban: str | None = None
        bic: str | None = None
        if offerer.iban:
            if iban_count == 0:
                iban = iban_prefix
                bic = bic_prefix + str(bic_suffix)
                iban_count = 1
            elif iban_count == 2:
                iban_count = 3
        else:
            if iban_count in (0, 1):
                iban = iban_prefix
                bic = bic_prefix + str(bic_suffix)
                iban_count = 2
            elif iban_count == 3:
                iban_count = 0

        comment = None
        siret = f"{offerer.siren}{random.randint(11111,99999)}"

        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            bookingEmail="data@example.com",
            latitude=float(geoloc_match.group(2)),  # type: ignore[union-attr]
            longitude=float(geoloc_match.group(3)),  # type: ignore[union-attr]
            comment=comment,
            name=venue_name,
            siret=siret,
            venueTypeCode=offerers_models.VenueTypeCode.MUSEUM,
            pricing_point="self" if siret else None,
        )
        bank_account = finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(bankAccount=bank_account, venue=venue)

        if image_venue_counter < DEFAULT_VENUE_IMAGES:
            add_default_image_to_venue(image_venue_counter, offerer, venue)
            image_venue_counter += 1

        venue_by_name[venue_name] = venue

        if iban and venue.siret:
            finance_factories.BankInformationFactory(
                venue=venue,
                bic=bic,
                iban=iban,
                applicationId=application_id_prefix + str(offerer_index),
            )

        bic_suffix += 1
        mock_index += 1

    logger.info("created %d venues DATA", len(venue_by_name))

    return venue_by_name
