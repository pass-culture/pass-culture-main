from models.pc_object import PcObject
from sandboxes.scripts.utils.storage_utils import store_public_object_from_sandbox_assets
from utils.logger import logger
from utils.test_utils import create_mediation

def create_scratch_mediations(offers_by_name):
    logger.info('create_scratch_mediations')

    mediations_by_name = {}

    mediations_by_name['Rencontre avec Franck Lepage / LE GRAND REX PARIS'] = create_mediation(
        offers_by_name['Rencontre avec Franck Lepage / LE GRAND REX PARIS']
    )


    mediations_by_name['Ravage / THEATRE DE L ODEON'] = create_mediation(
        offers_by_name['Ravage / THEATRE DE L ODEON']
    )

    PcObject.check_and_save(*mediations_by_name.values())

    for mediation in mediations_by_name.values():
        store_public_object_from_sandbox_assets(
            "thumbs",
            mediation,
            mediation.offer.eventOrThing.type
        )

    return mediations_by_name
