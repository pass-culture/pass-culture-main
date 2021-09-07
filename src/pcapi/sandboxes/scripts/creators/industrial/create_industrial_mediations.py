import logging

from pcapi.model_creators.generic_creators import create_mediation
from pcapi.repository import repository
from pcapi.sandboxes.scripts.utils.select import remove_every
from pcapi.sandboxes.scripts.utils.storage_utils import store_public_object_from_sandbox_assets


logger = logging.getLogger(__name__)


OFFERS_WITH_MEDIATION_REMOVE_MODULO = 5


def create_industrial_mediations(offers_by_name):
    logger.info("create_industrial_mediations")

    mediations_with_asset = {}
    mediations_by_name = {}

    offer_items = list(offers_by_name.items())
    offer_items_with_mediation = remove_every(offer_items, OFFERS_WITH_MEDIATION_REMOVE_MODULO)
    for (offer_with_mediation_name, offer_with_mediation) in offer_items_with_mediation:
        mediations_by_name[offer_with_mediation_name] = create_mediation(offer_with_mediation)

    repository.save(*mediations_by_name.values())

    for mediation in mediations_by_name.values():
        mediations_with_asset[mediation.id] = store_public_object_from_sandbox_assets(
            "thumbs", mediation, mediation.offer.subcategoryId
        )

    repository.save(*mediations_with_asset.values())

    logger.info("created %d mediations", len(mediations_by_name))
