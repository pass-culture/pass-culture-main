from pcapi.domain.pro_offers.offers_recap import OfferRecap
from pcapi.domain.pro_offers.offers_recap import OfferRecapStock
from pcapi.domain.pro_offers.offers_recap import OfferRecapVenue
from pcapi.domain.pro_offers.offers_recap import OffersRecap


def serialize_offers_recap_paginated(paginated_offers: OffersRecap) -> list[dict]:
    return [_serialize_offer_paginated(offer) for offer in paginated_offers.offers]


def _serialize_offer_paginated(offer: OfferRecap) -> dict:
    serialized_stocks = [_serialize_stock(offer.id, stock) for stock in offer.stocks]

    return {
        "hasBookingLimitDatetimesPassed": offer.has_booking_limit_datetimes_passed,
        "nonHumanizedId": offer.id,
        "isActive": offer.is_active,
        "isEditable": offer.is_editable,
        "isEvent": offer.is_event,
        "isThing": offer.is_thing,
        "isEducational": False,
        "productIsbn": offer.product_ean,
        "name": offer.name,
        "stocks": serialized_stocks,
        "thumbUrl": offer.thumb_url,
        "subcategoryId": offer.subcategoryId,
        "venue": _serialize_venue(offer.venue),
        "status": offer.status,
        "isShowcase": offer.is_showcase,
    }


def _serialize_stock(offer_id: int, stock: OfferRecapStock) -> dict:
    return {
        "nonHumanizedId": stock.id,
        "hasBookingLimitDatetimePassed": stock.has_booking_limit_datetime_passed,
        "remainingQuantity": stock.remaining_quantity,
        "beginningDatetime": stock.beginning_datetime,
        "bookingQuantity": stock.dnBookedQuantity,
    }


def _serialize_venue(venue: OfferRecapVenue) -> dict:
    return {
        "nonHumanizedId": venue.id,
        "isVirtual": venue.is_virtual,
        "name": venue.name,
        "offererName": venue.offerer_name,
        "publicName": venue.public_name,
        "departementCode": venue.departement_code,
    }
