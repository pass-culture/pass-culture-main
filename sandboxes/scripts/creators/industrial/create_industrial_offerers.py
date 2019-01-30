from models.pc_object import PcObject
from sandboxes.scripts.utils.offerer_mocks import MOCK_NAMES
from utils.logger import logger
from utils.test_utils import create_offerer

OFFERERS_WITH_IBAN_REMOVE_MODULO = 2

def create_industrial_offerers(
        locations,
        needs_validation=False,
        starting_index=0,
        starting_siren=222222222
):
    logger.info('create_industrial_offerers {}'.format(
        'not validated' if needs_validation else 'validated'
    ))

    incremented_siren = starting_siren

    offerers_by_name = {}

    # add a real offerer just for the inscription/validation API
    if not needs_validation:
        name = '784340093 lat:48.8 lon:1.48'
        offerers_by_name[name] = create_offerer(
            address="LIEU DIT CARTOUCHERIE",
            city="Paris 12",
            name="THEATRE DU SOLEIL",
            postal_code="75012",
            siren="784340093"
        )

    # loop on locations
    iban_prefix = 'FR7630001007941234567890185'
    bic_prefix, bic_suffix = 'QSDFGH8Z', 555
    for (location_index, location) in enumerate(locations):

        mock_index = location_index % len(MOCK_NAMES) + starting_index

        name = '{} lat:{} lon:{}'.format(
            incremented_siren,
            location['latitude'],
            location['longitude']
        )

        # create every OFFERERS_WITH_IBAN_REMOVE_MODULO an offerer with no iban
        if location_index%OFFERERS_WITH_IBAN_REMOVE_MODULO:
            iban = iban_prefix
            bic = bic_prefix + str(bic_suffix)
        else:
            iban = None
            bic = None

        offerer = create_offerer(
            address=location['address'].upper(),
            bic=bic,
            city=location['city'],
            iban=iban,
            name=MOCK_NAMES[mock_index],
            postal_code=location['postalCode'],
            siren=str(incremented_siren),
        )

        if needs_validation:
            offerer.generate_validation_token()

        offerers_by_name[name] = offerer

        incremented_siren += 1
        bic_suffix += 1

    PcObject.check_and_save(*offerers_by_name.values())

    logger.info('created {} offerers {}'.format(
        len(offerers_by_name),
        'not validated' if needs_validation else 'validated'
    ))

    return offerers_by_name
