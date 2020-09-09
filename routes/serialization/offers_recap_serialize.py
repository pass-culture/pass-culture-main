from typing import Dict, List

from domain.pro_offers.paginated_offers import PaginatedOffers
from models import OfferSQLEntity, StockSQLEntity
from utils.human_ids import humanize


def serialize_offers_recap_paginated(paginated_offers: PaginatedOffers) -> List[Dict]:
    return [_serialize_offer_paginated(offer) for offer in paginated_offers.offers]


def _serialize_offer_paginated(offer: OfferSQLEntity) -> Dict:
    serialized_stocks = _serialize_stocks(offer.stocks)

    return {
        "availabilityMessage": offer.availabilityMessage,
        "hasBookingLimitDatetimesPassed": offer.hasBookingLimitDatetimesPassed,
        "id": humanize(offer.id),
        "isActive": offer.isActive,
        "isEditable": offer.isEditable,
        "isFullyBooked": offer.isFullyBooked,
        "isEvent": offer.isEvent,
        "isThing": offer.isThing,
        "name": offer.name,
        "stocks": serialized_stocks,
        "thumbUrl": offer.thumbUrl,
        "type": offer.type,
        "venue": {
            "id": humanize(offer.venue.id),
            "isVirtual": offer.venue.isVirtual,
            "name": offer.venue.name,
            "publicName": offer.venue.publicName,
        },
        "venueId": humanize(offer.venueId),
    }


def _serialize_stocks(stocks: [StockSQLEntity]) -> List[Dict]:
    return [_serialize_stock(stock) for stock in stocks]


def _serialize_stock(stock: StockSQLEntity) -> Dict:
    return {
        "id": humanize(stock.id),
        "isEventExpired": stock.isEventExpired,
        "offerId": humanize(stock.offerId),
        "remainingQuantity": stock.remainingQuantity
    }
