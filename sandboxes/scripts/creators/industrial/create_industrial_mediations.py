from models.pc_object import PcObject
from sandboxes.scripts.utils.select import remove_every
from sandboxes.scripts.utils.storage_utils import store_public_object_from_sandbox_assets
from utils.logger import logger
from tests.model_creators.generic_creators import create_mediation

OFFERS_WITH_MEDIATION_REMOVE_MODULO = 5

def create_industrial_mediations(offers_by_name):
    logger.info('create_industrial_mediations')

    mediations_by_name = {}

    offer_items = list(offers_by_name.items())
    offer_items_with_mediation = remove_every(offer_items, OFFERS_WITH_MEDIATION_REMOVE_MODULO)
    for (offer_with_mediation_name, offer_with_mediation) in offer_items_with_mediation:
        mediations_by_name[offer_with_mediation_name] = create_mediation(offer_with_mediation)

    PcObject.save(*mediations_by_name.values())

    logger.info('created {} mediations'.format(len(mediations_by_name)))

    for mediation in mediations_by_name.values():
        store_public_object_from_sandbox_assets(
            "thumbs",
            mediation,
            mediation.offer.type
        )

    return mediations_by_name
