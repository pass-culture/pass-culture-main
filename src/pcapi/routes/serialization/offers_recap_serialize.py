from typing import Any

from pcapi.domain.identifier.identifier import Identifier
from pcapi.domain.pro_offers.paginated_offers_recap import OfferRecap
from pcapi.domain.pro_offers.paginated_offers_recap import OfferRecapStock
from pcapi.domain.pro_offers.paginated_offers_recap import OfferRecapVenue
from pcapi.domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap


def serialize_offers_recap_paginated(paginated_offers: PaginatedOffersRecap) -> dict[str, Any]:
    return {
        "offers": [_serialize_offer_paginated(offer) for offer in paginated_offers.offers],
        "page": paginated_offers.current_page,
        "page_count": paginated_offers.total_pages,
        "total_count": paginated_offers.total_offers,
    }


def _serialize_offer_paginated(offer: OfferRecap) -> dict:
    serialized_stocks = [_serialize_stock(offer.identifier, stock) for stock in offer.stocks]

    return {
        "hasBookingLimitDatetimesPassed": offer.has_booking_limit_datetimes_passed,
        "id": offer.identifier.scrambled,
        "isActive": offer.is_active,
        "isEditable": offer.is_editable,
        "isEvent": offer.is_event,
        "isThing": offer.is_thing,
        "name": offer.name,
        "stocks": serialized_stocks,
        "thumbUrl": offer.thumb_url,
        "type": offer.offer_type,
        "venue": _serialize_venue(offer.venue),
        "venueId": offer.venue.identifier.scrambled,
        "status": offer.status,
    }


def _serialize_stock(offer_identifier: Identifier, stock: OfferRecapStock) -> dict:
    return {
        "id": stock.identifier.scrambled,
        "offerId": offer_identifier.scrambled,
        "hasBookingLimitDatetimePassed": stock.has_booking_limit_datetime_passed,
        "remainingQuantity": stock.remaining_quantity,
    }


def _serialize_venue(venue: OfferRecapVenue) -> dict:
    return {
        "id": venue.identifier.scrambled,
        "isVirtual": venue.is_virtual,
        "managingOffererId": venue.managing_offerer_id.scrambled,
        "name": venue.name,
        "offererName": venue.offerer_name,
        "publicName": venue.public_name,
        "departementCode": venue.departement_code,
    }
