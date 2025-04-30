import logging

from pcapi.core.categories.subcategories import ALL_SUBCATEGORIES
from pcapi.core.logging import log_elapsed
from pcapi.core.offerers import models as offerer_models
import pcapi.core.offers.models as offers_models
from pcapi.models import db


logger = logging.getLogger(__name__)

MAX_OFFERS_TO_REINDEX = 10_000


def get_relevant_offers_to_index() -> set[int]:
    offer_ids_to_reindex = set()

    offer_ids_to_reindex.update(get_offers_for_each_subcategory(10))
    offer_ids_to_reindex.update(get_offers_with_gtl(1000))
    offer_ids_to_reindex.update(get_offers_for_each_gtl_level_1(10))
    offer_ids_to_reindex.update(
        get_random_offers(MAX_OFFERS_TO_REINDEX - len(offer_ids_to_reindex), offer_ids_to_reindex)
    )
    return offer_ids_to_reindex


def get_offers_for_each_subcategory(size_per_subcategory: int) -> set[int]:
    result = set()

    for subcategory in ALL_SUBCATEGORIES:
        query = (
            db.session.query(offers_models.Offer)
            .outerjoin(offers_models.Stock)
            .outerjoin(offers_models.FutureOffer)
            .join(offerer_models.Venue)
            .join(offerer_models.Offerer)
            .filter(
                offers_models.Offer.is_eligible_for_search,
                offers_models.Offer.subcategoryId == subcategory.id,
            )
            .with_entities(offers_models.Offer.id)
            .limit(size_per_subcategory)
        )
        with log_elapsed(logger, f"offers for subcategory {subcategory.id}"):
            result.update({offer_id for (offer_id,) in query})
    return result


def get_offers_with_gtl(size: int) -> set[int]:
    query = (
        db.session.query(offers_models.Offer)
        .outerjoin(offers_models.Stock)
        .outerjoin(offers_models.FutureOffer)
        .outerjoin(offers_models.Product)
        .filter(
            offers_models.Product.extraData["gtl_id"].is_not(None),
            offers_models.Offer.is_eligible_for_search,
        )
        .with_entities(offers_models.Offer.id)
        .limit(size)
    )
    with log_elapsed(logger, "offers with GTL"):
        result = {offer_id for (offer_id,) in query}
    return result


def get_offers_for_each_gtl_level_1(size_per_gtl: int) -> set[int]:
    result = set()
    for i in range(1, 14):
        query = (
            db.session.query(offers_models.Offer)
            .outerjoin(offers_models.Stock)
            .outerjoin(offers_models.FutureOffer)
            .outerjoin(offers_models.Product)
            .filter(
                offers_models.Product.extraData["gtl_id"].astext.startswith(str(i).zfill(2)),
                offers_models.Offer.is_eligible_for_search,
            )
            .with_entities(offers_models.Offer.id)
            .limit(size_per_gtl)
        )
        with log_elapsed(logger, "offers for each GTL level 1"):
            result.update({offer_id for (offer_id,) in query})
    return result


def get_random_offers(size: int, excluded_offer_ids: set[int]) -> set[int]:
    query = (
        db.session.query(offers_models.Offer)
        .outerjoin(offers_models.Stock)
        .outerjoin(offers_models.FutureOffer)
        .filter(
            offers_models.Offer.is_eligible_for_search,
            offers_models.Offer.id.not_in(excluded_offer_ids),
        )
        .with_entities(offers_models.Offer.id)
        .limit(size)
    )
    with log_elapsed(logger, "random offers to complete the dataset"):
        result = {offer_id for (offer_id,) in query}
    return result
