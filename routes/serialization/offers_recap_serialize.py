from typing import Dict, List

from domain.identifier.identifier import Identifier
from domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap, OfferRecap, OfferRecapStock, OfferRecapVenue
from utils.human_ids import humanize


def serialize_offers_recap_paginated(paginated_offers: PaginatedOffersRecap) -> List[Dict]:
    return [_serialize_offer_paginated(offer) for offer in paginated_offers.offers]


def _serialize_offer_paginated(offer: OfferRecap) -> Dict:
    serialized_stocks = [_serialize_stock(offer.identifier, stock) for stock in offer.stocks]

    return {
        "hasBookingLimitDatetimesPassed": offer.has_booking_limit_datetimes_passed,
        "id": offer.identifier.humanize(),
        "isActive": offer.is_active,
        "isEditable": offer.is_editable,
        "isEvent": offer.is_event,
        "isThing": offer.is_thing,
        "name": offer.name,
        "stocks": serialized_stocks,
        "thumbUrl": offer.thumb_url,
        "type": offer.offer_type,
        "venue": _serialize_venue(offer.venue),
        "venueId": offer.venue.identifier.humanize(),
    }


def _serialize_stock(offer_identifier: Identifier, stock: OfferRecapStock) -> Dict:
    return {
        "id": stock.identifier.humanize(),
        "offerId": offer_identifier.humanize(),
        "remainingQuantity": stock.remaining_quantity
    }


def _serialize_venue(venue: OfferRecapVenue) -> Dict:
    return {
        "id": venue.identifier.humanize(),
        "isVirtual": venue.is_virtual,
        "managingOffererId": venue.managing_offerer_id.humanize(),
        "name": venue.name,
        "publicName": venue.public_name,
    }
