from models.pc_object import PcObject
from sandboxes.scripts.utils.storage_utils import store_public_object_from_sandbox_assets
from utils.logger import logger
from utils.test_utils import create_mediation

def create_grid_mediations(offers_by_name):
    logger.info('create_grid_mediations')
    
    mediations_by_name = {}

    for (offer_name, offer) in offers_by_name.items():
        mediations_by_name[offer_name] = create_mediation(offer)

    PcObject.check_and_save(*mediations_by_name.values())

    for mediation in mediations_by_name.values():
        store_public_object_from_sandbox_assets(
            "thumbs",
            mediation,
            mediation.offer.eventOrThing.type
        )

    return mediations_by_name
