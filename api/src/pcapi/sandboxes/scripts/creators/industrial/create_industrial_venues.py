import logging
import random
import re

from pcapi.core.offerers.models import VENUE_TYPE_CODE_MAPPING
from pcapi.core.offerers.models import VenueType
from pcapi.core.offerers.models import VenueTypeCode
from pcapi.core.offers.factories import BankInformationFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.offers.factories import VirtualVenueFactory
from pcapi.core.providers import factories as providers_factories
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

    label_to_code = {label: code for code, label in VENUE_TYPE_CODE_MAPPING.items()}

    for (offerer_index, (offerer_name, offerer)) in enumerate(offerers_by_name.items()):
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

            # TODO: remove venue_type and label to code mapping when
            # the venue_type table has been finally replaced by the
            # VenueTypeCode enum
            venue_type = random.choice(venue_types)
            venue_type_code = VenueTypeCode[label_to_code.get(venue_type.label, "OTHER")]

            venue = VenueFactory(
                managingOfferer=offerer,
                bookingEmail="fake@example.com",
                latitude=float(geoloc_match.group(2)),
                longitude=float(geoloc_match.group(3)),
                comment=comment,
                name=venue_name,
                siret=siret,
                venueTypeId=venue_type.id,
                venueTypeCode=venue_type_code,
                isPermanent=True,
                businessUnit__name=offerer.name,
            )
            providers_factories.VenueProviderFactory(venue=venue)

            venue_by_name[venue_name] = venue

            if iban and venue.siret:
                BankInformationFactory(
                    venue=venue, bic=bic, iban=iban, applicationId=application_id_prefix + str(offerer_index)
                )

        bic_suffix += 1
        mock_index += 1

        virtual_venue_name = "{} (Offre numérique)"
        venue_by_name[virtual_venue_name] = VirtualVenueFactory(
            managingOfferer=offerer, name=virtual_venue_name.format(venue_name), businessUnit__name=offerer.name
        )

    venue_synchronized_with_allocine = VenueFactory(
        name="Lieu synchro allociné", siret="87654321", businessUnit__name="Business Unit du Lieu synchro allociné"
    )
    allocine_provider = providers_factories.AllocineProviderFactory(isActive=True)
    pivot = providers_factories.AllocinePivotFactory(siret=venue_synchronized_with_allocine.siret)
    venue_provider = providers_factories.AllocineVenueProviderFactory(
        venue=venue_synchronized_with_allocine, provider=allocine_provider, venueIdAtOfferProvider=pivot.theaterId
    )
    providers_factories.AllocineVenueProviderPriceRuleFactory(allocineVenueProvider=venue_provider)
    venue_by_name[venue_synchronized_with_allocine.name] = venue_synchronized_with_allocine

    # FIXME (viconnex): understand why these properties are not set with right values in factories
    allocine_provider.isActive = True
    allocine_provider.enabledForPro = True

    logger.info("created %d venues", len(venue_by_name))

    return venue_by_name
