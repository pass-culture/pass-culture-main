import logging
import random
import re

import pcapi.core.finance.factories as finance_factories
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.providers import factories as providers_factories
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.sandboxes.scripts.mocks.accessibility_mocks import ACCESSIBILITY_MOCK
from pcapi.sandboxes.scripts.mocks.venue_mocks import MOCK_NAMES


logger = logging.getLogger(__name__)


OFFERERS_WITH_PHYSICAL_VENUE_REMOVE_MODULO = 3
OFFERERS_WITH_PHYSICAL_VENUE_WITH_SIRET_REMOVE_MODULO = OFFERERS_WITH_PHYSICAL_VENUE_REMOVE_MODULO * 2
OFFERERS_WITH_A_SECOND_VENUE_WITH_SIRET_MODULO = 4

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


def create_industrial_venues(offerers_by_name: dict) -> dict[str, Venue]:
    logger.info("create_industrial_venues")

    venue_by_name = {}
    mock_index = 0
    mock_accessibility_index = 0

    iban_count = 0
    iban_prefix = "FR7630001007941234567890185"
    bic_prefix, bic_suffix = "QSDFGH8Z", 556
    application_id_prefix = "12"

    image_venue_counter = 0

    for offerer_index, (offerer_name, offerer) in enumerate(offerers_by_name.items()):
        geoloc_match = re.match(r"(.*)lat\:(.*) lon\:(.*)", offerer_name)
        latitude = float(geoloc_match.group(2)) if geoloc_match else None
        longitude = float(geoloc_match.group(3)) if geoloc_match else None

        venue_name = MOCK_NAMES[mock_index % len(MOCK_NAMES)]
        venue_accessibility = ACCESSIBILITY_MOCK[mock_accessibility_index % len(ACCESSIBILITY_MOCK)]

        # create all possible cases:
        # offerer with or without iban / venue with or without iban
        iban = None
        bic = None
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

        if offerer_index % OFFERERS_WITH_PHYSICAL_VENUE_REMOVE_MODULO == 0:
            venue = None
        else:
            if offerer_index % OFFERERS_WITH_PHYSICAL_VENUE_WITH_SIRET_REMOVE_MODULO:
                comment = None
                siret = f"{offerer.siren}11111"
            else:
                comment = "Pas de siret car c'est comme cela."
                siret = None

            bank_account = None
            if iban and siret:
                bank_account = finance_factories.BankAccountFactory(
                    offerer=offerer, iban=iban, bic=bic, dsApplicationId=application_id_prefix + str(offerer_index)
                )

            venue = offerers_factories.VenueFactory(
                managingOfferer=offerer,
                bookingEmail=f"booking-email@offerer{offerer.id}.example.com",
                latitude=latitude,
                longitude=longitude,
                comment=comment,
                name=venue_name,
                siret=siret,
                venueTypeCode=random.choice(offerers_models.PERMENANT_VENUE_TYPES),
                pricing_point="self" if siret else None,
                bank_account=bank_account,
            )
            offerers_factories.AccessibilityProviderFactory(venue=venue, externalAccessibilityData=venue_accessibility)

            if offerer.validationStatus == ValidationStatus.NEW:
                offerers_factories.VenueRegistrationFactory(venue=venue)

            if image_venue_counter < DEFAULT_VENUE_IMAGES:
                add_default_image_to_venue(image_venue_counter, offerer, venue)
                image_venue_counter += 1

            venue_by_name[venue_name] = venue

            # Create a second physical venue to enable removing SIRET on the first one
            if offerer_index % OFFERERS_WITH_A_SECOND_VENUE_WITH_SIRET_MODULO == 0:
                second_venue_name = f"{venue_name} Bis"
                second_venue = offerers_factories.VenueFactory(
                    managingOfferer=offerer,
                    bookingEmail=f"booking-email@offerer{offerer.id}.example.com",
                    latitude=latitude,
                    longitude=longitude,
                    comment=None,
                    name=second_venue_name,
                    siret=f"{offerer.siren}22222",
                    venueTypeCode=random.choice(offerers_models.PERMENANT_VENUE_TYPES),
                    pricing_point="self",
                )
                second_bank_account = finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
                offerers_factories.VenueBankAccountLinkFactory(bankAccount=second_bank_account, venue=second_venue)
                venue_by_name[second_venue_name] = second_venue
            mock_accessibility_index += 1

        bic_suffix += 1
        mock_index += 1

        virtual_venue_name = "{} (Offre numérique)"
        venue_by_name[virtual_venue_name] = offerers_factories.VirtualVenueFactory(
            managingOfferer=offerer,
            name=virtual_venue_name.format(venue_name),
            pricing_point=venue,
        )

    # Venue Allocine

    allocine_offerer = offerers_factories.OffererFactory(name="Structure du lieu synchro allociné")
    offerers_factories.UserOffererFactory(offerer=allocine_offerer, user__email="api@example.com")
    venue_synchronized_with_allocine = offerers_factories.VenueFactory(
        name="Lieu synchro allociné",
        siret="21070034000016",
        pricing_point="self",
        managingOfferer=allocine_offerer,
        venueTypeCode=offerers_models.VenueTypeCode.MOVIE,
    )
    bank_account = finance_factories.BankAccountFactory(offerer=venue_synchronized_with_allocine.managingOfferer)
    offerers_factories.VenueBankAccountLinkFactory(bankAccount=bank_account, venue=venue_synchronized_with_allocine)
    allocine_provider = providers_factories.AllocineProviderFactory(isActive=True)
    theater = providers_factories.AllocineTheaterFactory(siret=venue_synchronized_with_allocine.siret)
    pivot = providers_factories.AllocinePivotFactory(
        venue=venue_synchronized_with_allocine, theaterId=theater.theaterId, internalId=theater.internalId
    )
    providers_factories.AllocineVenueProviderFactory(
        venue=venue_synchronized_with_allocine, provider=allocine_provider, venueIdAtOfferProvider=pivot.theaterId
    )
    venue_by_name[venue_synchronized_with_allocine.name] = venue_synchronized_with_allocine

    logger.info("created %d venues", len(venue_by_name))

    return venue_by_name
