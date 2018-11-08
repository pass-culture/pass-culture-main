from models.pc_object import PcObject
from sandboxes.scripts.utils.storage_utils import store_public_object_from_sandbox_assets
from utils.logger import logger
from utils.test_utils import create_mediation

def create_grid_event_stocks(offers_by_name):
    mediations_by_name = {}

    for offer in offers_by_name.values():
        mediation = create_mediation(offer)

    PcObject.check_and_save(*mediations_by_name.values())

    for mediation in mediations_by_name.values():
        store_public_object_from_sandbox_assets(
            "thumbs",
            mediation,
            mediation.offer.eventOrThing.type
        )

    return mediations_by_name
