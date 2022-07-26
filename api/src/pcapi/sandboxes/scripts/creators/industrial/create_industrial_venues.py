import logging
import random
import re

import pcapi.core.finance.factories as finance_factories
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueType
from pcapi.core.offerers.models import VenueTypeCode
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.sandboxes.scripts.mocks.venue_mocks import MOCK_NAMES


logger = logging.getLogger(__name__)


OFFERERS_WITH_PHYSICAL_VENUE_REMOVE_MODULO = 3
OFFERERS_WITH_PHYSICAL_VENUE_WITH_SIRET_REMOVE_MODULO = OFFERERS_WITH_PHYSICAL_VENUE_REMOVE_MODULO * 2

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


def create_industrial_venues(offerers_by_name: dict, venue_types: list[VenueType]) -> dict[str, Venue]:
    logger.info("create_industrial_venues")

    venue_by_name = {}
    mock_index = 0

    iban_count = 0
    iban_prefix = "FR7630001007941234567890185"
    bic_prefix, bic_suffix = "QSDFGH8Z", 556
    application_id_prefix = "12"

    label_to_code = {venue_type.name: venue_type.value for venue_type in VenueTypeCode}

    image_venue_counter = 0

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
                siret = f"{offerer.siren}11111"
            else:
                comment = "Pas de siret car c'est comme cela."
                siret = None

            # TODO: remove venue_type and label to code mapping when
            # the venue_type table has been finally replaced by the
            # VenueTypeCode enum
            venue_type = random.choice(venue_types)
            venue_type_code = VenueTypeCode[label_to_code.get(venue_type.label, "OTHER")]  # type: ignore [arg-type]

            venue = offerers_factories.VenueFactory(
                managingOfferer=offerer,
                bookingEmail="fake@example.com",
                latitude=float(geoloc_match.group(2)),  # type: ignore [union-attr]
                longitude=float(geoloc_match.group(3)),  # type: ignore [union-attr]
                comment=comment,
                name=venue_name,
                siret=siret,
                venueTypeId=venue_type.id,
                venueTypeCode=venue_type_code,
                isPermanent=True,
                businessUnit__name=offerer.name,
                pricing_point="self" if siret else None,
                reimbursement_point="self" if siret else None,
            )
            providers_factories.VenueProviderFactory(venue=venue)

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

        virtual_venue_name = "{} (Offre numérique)"
        venue_by_name[virtual_venue_name] = offerers_factories.VirtualVenueFactory(
            managingOfferer=offerer, name=virtual_venue_name.format(venue_name), businessUnit__name=offerer.name
        )

    # Venue Allocine
    venue_synchronized_with_allocine = offerers_factories.VenueFactory(
        name="Lieu synchro allociné",
        siret="21070034000016",
        businessUnit__name="Business Unit du Lieu synchro allociné",
        managingOfferer__name="Structure du lieu synchro allociné",
    )
    allocine_provider = providers_factories.AllocineProviderFactory(isActive=True)
    theater = providers_factories.AllocineTheaterFactory(siret=venue_synchronized_with_allocine.siret)
    pivot = providers_factories.AllocinePivotFactory(
        venue=venue_synchronized_with_allocine, theaterId=theater.theaterId, internalId=theater.internalId
    )
    allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(
        venue=venue_synchronized_with_allocine, provider=allocine_provider, venueIdAtOfferProvider=pivot.theaterId
    )
    providers_factories.AllocineVenueProviderPriceRuleFactory(allocineVenueProvider=allocine_venue_provider)
    venue_by_name[venue_synchronized_with_allocine.name] = venue_synchronized_with_allocine

    # FIXME (viconnex): understand why these properties are not set with right values in factories
    allocine_provider.isActive = True
    allocine_provider.enabledForPro = True

    # Venue Cine Office (CDS)
    venue_synchronized_with_cds = offerers_factories.VenueFactory(
        comment="Salle de cinéma",
        name="Lieu synchro Ciné Office",
        siret="21070034000018",
        businessUnit__name="Business Unit du Lieu synchro Ciné Office",
        managingOfferer__name="Structure du lieu synchro Ciné Office",
    )

    cds_provider = get_provider_by_local_class("CDSStocks")
    cds_provider.isActive = True  # type: ignore [assignment]
    cds_provider.enabledForPro = True

    cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
        venue=venue_synchronized_with_cds, provider=cds_provider, idAtProvider="cdsdemorc1"
    )
    providers_factories.CDSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot, accountId="cdsdemorc1")
    providers_factories.VenueProviderFactory(venue=venue_synchronized_with_cds, provider=cds_provider)

    venue_by_name[venue_synchronized_with_cds.name] = venue_synchronized_with_cds

    logger.info("created %d venues", len(venue_by_name))

    return venue_by_name
