from pcapi.core.categories.subcategories_v2 import ALL_SUBCATEGORIES
from pcapi.core.offerers import models as offerer_models
import pcapi.core.offers.models as offers_models


def get_relevant_offers_to_index() -> set[int]:
    offer_ids_to_reindex = set()
    offer_ids_to_reindex.update(get_offers_for_each_subcategory(10))
    offer_ids_to_reindex.update(get_offers_with_gtl(1000))
    offer_ids_to_reindex.update(get_offers_for_each_gtl_level_1(10))
    offer_ids_to_reindex.update(get_offers_with_visa_number(100))
    offer_ids_to_reindex.update(get_random_offers(5000 - len(offer_ids_to_reindex), offer_ids_to_reindex))
    return offer_ids_to_reindex


def get_offers_for_each_subcategory(size_per_subcategory: int) -> set[int]:
    query = offers_models.Offer.query.join(offers_models.Stock).filter(False).with_entities(offers_models.Offer.id)
    for subcategory in ALL_SUBCATEGORIES:
        query = query.union(
            offers_models.Offer.query.join(offers_models.Stock)
            .join(offerer_models.Venue)
            .join(offerer_models.Offerer)
            .filter(
                offers_models.Offer.is_eligible_for_search.is_(True),  # type: ignore [attr-defined]
                offers_models.Offer.subcategoryId == subcategory.id,
            )
            .with_entities(offers_models.Offer.id)
            .limit(size_per_subcategory)
        )
    return {offer_id for offer_id, in query}


def get_offers_with_gtl(size: int) -> set[int]:
    query = (
        offers_models.Offer.query.join(offers_models.Stock)
        .filter(
            offers_models.Offer.extraData["gtl_id"].is_not(None),
            offers_models.Offer.is_eligible_for_search.is_(True),  # type: ignore [attr-defined]
        )
        .with_entities(offers_models.Offer.id)
        .limit(size)
    )
    return {offer_id for offer_id, in query}


def get_offers_for_each_gtl_level_1(size_per_gtl: int) -> set[int]:
    query = offers_models.Offer.query.join(offers_models.Stock).filter(False).with_entities(offers_models.Offer.id)
    for i in range(1, 14):
        query = query.union(
            offers_models.Offer.query.join(offers_models.Stock)
            .filter(
                offers_models.Offer.extraData["gtl_id"].astext.startswith(str(i).zfill(2)),
                offers_models.Offer.is_eligible_for_search.is_(True),  # type: ignore [attr-defined]
            )
            .with_entities(offers_models.Offer.id)
            .limit(size_per_gtl)
        )
    return {offer_id for offer_id, in query}


def get_offers_with_visa_number(size: int) -> set[int]:
    query = (
        offers_models.Offer.query.join(offers_models.Stock)
        .filter(
            offers_models.Offer.extraData["visa_number"].is_not(None),
            offers_models.Offer.is_eligible_for_search.is_(True),  # type: ignore [attr-defined]
        )
        .with_entities(offers_models.Offer.id)
        .limit(size)
    )
    return {offer_id for offer_id, in query}


def get_random_offers(size: int, excluded_offer_ids: set[int]) -> set[int]:
    query = (
        offers_models.Offer.query.join(offers_models.Stock)
        .filter(
            offers_models.Offer.is_eligible_for_search.is_(True),  # type: ignore [attr-defined]
            offers_models.Offer.id.not_in(excluded_offer_ids),
        )
        .with_entities(offers_models.Offer.id)
        .limit(size)
    )
    return {offer_id for offer_id, in query}
