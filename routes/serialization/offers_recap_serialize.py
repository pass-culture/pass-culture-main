from typing import Dict, List

from domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap, OfferRecap, OfferRecapStock, OfferRecapVenue
from utils.human_ids import humanize


def serialize_offers_recap_paginated(paginated_offers: PaginatedOffersRecap) -> List[Dict]:
    return [_serialize_offer_paginated(offer) for offer in paginated_offers.offers]


def _serialize_offer_paginated(offer: OfferRecap) -> Dict:
    serialized_stocks = [_serialize_stock(offer.identifier, stock) for stock in offer.stocks]

    return {
        "hasBookingLimitDatetimesPassed": offer.has_booking_limit_datetimes_passed,
        "id": humanize(offer.identifier),
        "isActive": offer.is_active,
        "isEditable": offer.is_editable,
        "isEvent": offer.is_event,
        "isThing": offer.is_thing,
        "name": offer.name,
        "stocks": serialized_stocks,
        "thumbUrl": offer.thumb_url,
        "type": offer.offer_type,
        "venue": _serialize_venue(offer.venue),
        "venueId": humanize(offer.venue.identifier),
    }


def _serialize_stock(offer_identifier: int, stock: OfferRecapStock) -> Dict:
    return {
        "id": humanize(stock.identifier),
        "offerId": humanize(offer_identifier),
        "remainingQuantity": stock.remaining_quantity
    }


def _serialize_venue(venue: OfferRecapVenue) -> Dict:
    return {
        "id": humanize(venue.identifier),
        "isVirtual": venue.is_virtual,
        "managingOffererId": humanize(venue.managing_offerer_id),
        "name": venue.name,
        "publicName": venue.public_name,
    }
