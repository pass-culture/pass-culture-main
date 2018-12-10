from models.pc_object import PcObject
from sandboxes.scripts.utils.storage_utils import store_public_object_from_sandbox_assets
from utils.logger import logger
from utils.test_utils import create_mediation

def create_handmade_mediations(offers_by_name):
    logger.info('create_handmade_mediations')

    mediations_by_name = {}

    mediations_by_name['Rencontre avec Franck Lepage / THEATRE LE GRAND REX PARIS'] = \
        create_mediation(
            offers_by_name['Rencontre avec Franck Lepage / THEATRE LE GRAND REX PARIS']
        )

    mediations_by_name['Ravage / THEATRE DE L ODEON'] = \
        create_mediation(
            offers_by_name['Ravage / THEATRE DE L ODEON']
        )

    mediations_by_name['Le temps des cerises en mode mixolydien / ASSOCIATION KWATA'] = \
        create_mediation(
            offers_by_name['Le temps des cerises en mode mixolydien / ASSOCIATION KWATA']
        )

    PcObject.check_and_save(*mediations_by_name.values())

    logger.info('created {} mediations'.format(len(mediations_by_name)))

    store_public_object_from_sandbox_assets(
        "thumbs",
        mediations_by_name['Rencontre avec Franck Lepage / THEATRE LE GRAND REX PARIS'],
        "FranckLepage"
    )

    store_public_object_from_sandbox_assets(
        "thumbs",
        mediations_by_name['Ravage / THEATRE DE L ODEON'],
        "Ravage"
    )

    store_public_object_from_sandbox_assets(
        "thumbs",
        mediations_by_name['Le temps des cerises en mode mixolydien / ASSOCIATION KWATA'],
        "LeTempsDesCerises"
    )

    return mediations_by_name
