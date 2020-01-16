import re

from sandboxes.scripts.mocks.venue_mocks import MOCK_NAMES
from tests.model_creators.generic_creators import create_venue, create_bank_information
from utils.logger import logger

OFFERERS_WITH_PHYSICAL_VENUE_REMOVE_MODULO = 3
OFFERERS_WITH_PHYSICAL_VENUE_WITH_SIRET_REMOVE_MODULO = OFFERERS_WITH_PHYSICAL_VENUE_REMOVE_MODULO * 2


def create_industrial_venues(offerers_by_name: dict) -> dict:
    logger.info('create_industrial_venues')

    venue_by_name = {}
    mock_index = 0

    iban_count = 0
    iban_prefix = 'FR7630001007941234567890185'
    bic_prefix, bic_suffix = 'QSDFGH8Z', 556

    for (offerer_index, (offerer_name, offerer)) in enumerate(offerers_by_name.items()):
        geoloc_match = re.match(r'(.*)lat\:(.*) lon\:(.*)', offerer_name)

        venue_name = MOCK_NAMES[mock_index%len(MOCK_NAMES)]

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
            if iban_count == 0 or iban_count == 1:
                iban = iban_prefix
                bic = bic_prefix + str(bic_suffix)
                iban_count = 2
            elif iban_count == 3:
                iban = None
                bic = None
                iban_count = 0

        if offerer_index%OFFERERS_WITH_PHYSICAL_VENUE_REMOVE_MODULO:

            if offerer_index%OFFERERS_WITH_PHYSICAL_VENUE_WITH_SIRET_REMOVE_MODULO:
                comment = None
                siret = '{}11111'.format(offerer.siren)
            else:
                comment = "Pas de siret car c'est comme cela."
                siret = None

            venue_by_name[venue_name] = create_venue(
                offerer,
                address=offerer.address,
                booking_email="fake@email.com",
                city=offerer.city,
                comment=comment,
                latitude=float(geoloc_match.group(2)),
                longitude=float(geoloc_match.group(3)),
                name=venue_name,
                postal_code=offerer.postalCode,
                siret=siret
            )

            if iban and venue_by_name[venue_name].siret:
                bank_information = create_bank_information(bic=bic, iban=iban,
                                                           id_at_providers=venue_by_name[venue_name].siret,
                                                           venue=venue_by_name[venue_name])
        bic_suffix += 1
        mock_index += 1

        virtual_venue_name= "{} (Offre numérique)".format(venue_name)
        venue_by_name[virtual_venue_name] = create_venue(
            offerer,
            is_virtual=True,
            name=virtual_venue_name,
            siret=None
        )

    Repository.save(*venue_by_name.values())

    logger.info('created {} venues'.format(len(venue_by_name)))

    return venue_by_name
