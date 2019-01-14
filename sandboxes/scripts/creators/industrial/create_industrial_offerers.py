from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_offerer

MOCK_NAMES = [
    "Herbert Marcuse Entreprise",
    "Club Dorothy",
    "Scope La Brique",
    "Danse Jazz Dans Tes Bottes",
    "Michel Léon",
    "Syndicat des librairies physiques",
    "Maison des anachorètes"
]

def create_industrial_offerers(
    locations,
    needs_validation=False,
    starting_siren=222222222
):
    logger.info('create_industrial_offerers {}'.format(
        'not validated' if needs_validation else 'validated'
    ))

    incremented_siren = starting_siren

    offerers_by_name = {}

    iban_prefix = 'FR7630001007941234567890185'
    bic_prefix, bic_suffix = 'QSDFGH8Z', 555

    for (location_index, location) in enumerate(locations):

        mock_index = location_index % len(MOCK_NAMES)

        name = '{} lat:{} lon:{}'.format(
            incremented_siren,
            location['latitude'],
            location['longitude']
        )

        offerer = create_offerer(
            address=location['address'].upper(),
            city=location['city'],
            name=MOCK_NAMES[mock_index],
            postal_code=location['postalCode'],
            siren=str(incremented_siren),
            iban=iban_prefix,
            bic=bic_prefix + str(bic_suffix)
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
