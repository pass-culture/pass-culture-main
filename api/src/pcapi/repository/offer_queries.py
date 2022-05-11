from pcapi.core.offers.models import Offer


def get_offer_by_id(offer_id: int):  # type: ignore [no-untyped-def]
    return Offer.query.get(offer_id)


def get_offers_by_product_id(product_id: int) -> list[Offer]:
    return Offer.query.filter_by(productId=product_id).all()


def get_paginated_active_offer_ids(limit: int, page: int) -> list[int]:
    query = (
        Offer.query.with_entities(Offer.id)
        .filter(Offer.isActive.is_(True))
        .order_by(Offer.id)
        .offset(page * limit)
        .limit(limit)
    )
    return [offer_id for offer_id, in query]


def get_paginated_offer_ids_by_venue_id(venue_id: int, limit: int, page: int) -> list[int]:
    query = (
        Offer.query.with_entities(Offer.id)
        .filter(Offer.venueId == venue_id)
        .order_by(Offer.id)
        .offset(page * limit)
        .limit(limit)
    )
    return [offer_id for offer_id, in query]
