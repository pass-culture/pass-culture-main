from pcapi.domain.pro_offers.offers_recap import OfferRecap
from pcapi.domain.pro_offers.offers_recap import OfferRecapStock
from pcapi.domain.pro_offers.offers_recap import OfferRecapVenue
from pcapi.domain.pro_offers.offers_recap import OffersRecap
from pcapi.utils.human_ids import humanize


def serialize_offers_recap_paginated(paginated_offers: OffersRecap) -> list[dict]:
    return [_serialize_offer_paginated(offer) for offer in paginated_offers.offers]


def _serialize_offer_paginated(offer: OfferRecap) -> dict:
    serialized_stocks = [_serialize_stock(offer.id, stock) for stock in offer.stocks]

    return {
        "hasBookingLimitDatetimesPassed": offer.has_booking_limit_datetimes_passed,
        "id": humanize(offer.id),
        "isActive": offer.is_active,
        "isEditable": offer.is_editable,
        "isEvent": offer.is_event,
        "isThing": offer.is_thing,
        "productIsbn": offer.product_isbn,
        "name": offer.name,
        "stocks": serialized_stocks,
        "thumbUrl": offer.thumb_url,
        "subcategoryId": offer.subcategoryId,
        "venue": _serialize_venue(offer.venue),
        "venueId": humanize(offer.venue.id),
        "status": offer.status,
    }


def _serialize_stock(offer_id: int, stock: OfferRecapStock) -> dict:
    return {
        "id": humanize(stock.id),
        "offerId": humanize(offer_id),
        "hasBookingLimitDatetimePassed": stock.has_booking_limit_datetime_passed,
        "remainingQuantity": stock.remaining_quantity,
        "beginningDatetime": stock.beginning_datetime,
    }


def _serialize_venue(venue: OfferRecapVenue) -> dict:
    return {
        "id": humanize(venue.id),
        "isVirtual": venue.is_virtual,
        "managingOffererId": humanize(venue.managing_offerer_id),
        "name": venue.name,
        "offererName": venue.offerer_name,
        "publicName": venue.public_name,
        "departementCode": venue.departement_code,
    }
