import logging
import random
import re

from pcapi.core.offerers.factories import VenueProviderFactory
from pcapi.core.offerers.models import VenueType
from pcapi.core.offers.factories import BankInformationFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.offers.factories import VirtualVenueFactory
from pcapi.sandboxes.scripts.mocks.venue_mocks import MOCK_NAMES


logger = logging.getLogger(__name__)


OFFERERS_WITH_PHYSICAL_VENUE_REMOVE_MODULO = 3
OFFERERS_WITH_PHYSICAL_VENUE_WITH_SIRET_REMOVE_MODULO = OFFERERS_WITH_PHYSICAL_VENUE_REMOVE_MODULO * 2


def create_industrial_venues(offerers_by_name: dict, venue_types: list[VenueType]) -> dict:
    logger.info("create_industrial_venues")

    venue_by_name = {}
    mock_index = 0

    iban_count = 0
    iban_prefix = "FR7630001007941234567890185"
    bic_prefix, bic_suffix = "QSDFGH8Z", 556
    application_id_prefix = "12"

    for (offerer_index, (offerer_name, offerer)) in enumerate(offerers_by_name.items()):
        random.shuffle(venue_types)
        geoloc_match = re.match(r"(.*)lat\:(.*) lon\:(.*)", offerer_name)

        venue_name = MOCK_NAMES[mock_index % len(MOCK_NAMES)]

        # create all possible cases:
        # offerer with or without iban / venue with or without iban
        if offerer.iban:
            if iban_count == 0:
                iban = iban_prefix
                bic = bic_prefix + str(bic_suffix)
                iban_count = 1
            elif iban_count == 2:
                iban = None
                bic = None
                iban_count = 3
        else:
            if iban_count in (0, 1):
                iban = iban_prefix
                bic = bic_prefix + str(bic_suffix)
                iban_count = 2
            elif iban_count == 3:
                iban = None
                bic = None
                iban_count = 0

        if offerer_index % OFFERERS_WITH_PHYSICAL_VENUE_REMOVE_MODULO:
            if offerer_index % OFFERERS_WITH_PHYSICAL_VENUE_WITH_SIRET_REMOVE_MODULO:
                comment = None
                siret = "{}11111".format(offerer.siren)
            else:
                comment = "Pas de siret car c'est comme cela."
                siret = None

            venue = VenueFactory(
                managingOfferer=offerer,
                bookingEmail="fake@example.com",
                latitude=float(geoloc_match.group(2)),
                longitude=float(geoloc_match.group(3)),
                comment=comment,
                name=venue_name,
                siret=siret,
                venueTypeId=venue_types[0].id,
            )
            VenueProviderFactory(venue=venue)

            venue_by_name[venue_name] = venue

            if iban and venue.siret:
                BankInformationFactory(
                    venue=venue, bic=bic, iban=iban, applicationId=application_id_prefix + str(offerer_index)
                )

        bic_suffix += 1
        mock_index += 1

        virtual_venue_name = "{} (Offre numérique)"
        venue_by_name[virtual_venue_name] = VirtualVenueFactory(
            managingOfferer=offerer, name=virtual_venue_name.format(venue_name)
        )

    logger.info("created %d venues", len(venue_by_name))

    return venue_by_name
