import secrets

from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_offerer

def create_handmade_offerers():
    logger.info('create_handmade_offerers')

    offerers_by_name = {}

    offerers_by_name['LE GRAND REX PARIS'] = create_offerer(
        address="1 BD POISSONNIERE",
        city="Paris",
        name="LE GRAND REX PARIS",
        postal_code="75002",
        siren="507633576"
    )

    offerers_by_name['THEATRE DE L ODEON'] = create_offerer(
        address="6 RUE GROLEE",
        city="Lyon",
        name="THEATRE DE L ODEON",
        postal_code="69002",
        siren="750505703"
    )

    offerers_by_name['THEATRE DU SOLEIL'] = create_offerer(
        address="LIEU DIT CARTOUCHERIE",
        city="Paris 12",
        name="THEATRE DU SOLEIL",
        postal_code="75012",
        siren="784340093"
    )

    offerers_by_name['KWATA'] = create_offerer(
        address="16 AVENUE PASTEUR",
        city="Cayenne",
        name="KWATA",
        postal_code="97335",
        siren="399244474"
    )

    offerers_by_name['NOUVEAU THEATRE DE MONTREUIL'] = create_offerer(
        address="63 RUE VICTOR HUGO",
        city="Montreuil",
        name="NOUVEAU THEATRE DE MONTREUIL",
        postal_code="93100",
        siren="323339762",
        validation_token=secrets.token_urlsafe(20)
    )

    offerers_by_name['LA MARBRERIE'] = create_offerer(
        address="21 RUE ALEXIS LEPERE",
        city="Montreuil",
        name="LA MARBRERIE",
        postal_code="93100",
        siren="812182491"
    )

    offerers_by_name['PASS CULTURE'] = create_offerer(
        address="3 rue de Valois",
        city="Paris",
        name="pass Culture",
        postal_code="75002",
        siren="123456789"
    )

    PcObject.check_and_save(*offerers_by_name.values())

    logger.info('created {} offerers'.format(len(offerers_by_name)))

    return offerers_by_name
