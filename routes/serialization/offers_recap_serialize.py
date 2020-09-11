from typing import Dict, List

from domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap, OfferRecap, Stock, Venue
from utils.human_ids import humanize


def serialize_offers_recap_paginated(paginated_offers: PaginatedOffersRecap) -> List[Dict]:
    return [_serialize_offer_paginated(offer) for offer in paginated_offers.offers]


def _serialize_offer_paginated(offer: OfferRecap) -> Dict:
    serialized_stocks = [_serialize_stock(stock) for stock in offer.stocks]

    return {
        "availabilityMessage": offer.availability_message,
        "hasBookingLimitDatetimesPassed": offer.has_booking_limit_datetimes_passed,
        "id": humanize(offer.identifier),
        "isActive": offer.is_active,
        "isEditable": offer.is_editable,
        "isFullyBooked": offer.is_fully_booked,
        "isEvent": offer.is_event,
        "isThing": offer.is_thing,
        "name": offer.name,
        "stocks": serialized_stocks,
        "thumbUrl": offer.thumb_url,
        "type": offer.offer_type,
        "venue": _serialize_venue(offer.venue),
        "venueId": humanize(offer.venue.identifier),
    }


def _serialize_stock(stock: Stock) -> Dict:
    return {
        "id": humanize(stock.identifier),
        "isEventExpired": stock.is_event_expired,
        "offerId": humanize(stock.offer_id),
        "remainingQuantity": stock.remaining_quantity
    }


def _serialize_venue(venue: Venue) -> Dict:
    return {
        "id": humanize(venue.identifier),
        "isVirtual": venue.is_virtual,
        "name": venue.name,
        "publicName": venue.public_name,
    }
