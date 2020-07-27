from typing import Dict, List

from models import Favorite, UserSQLEntity, BookingSQLEntity, StockSQLEntity
from routes.serialization.serializer import serialize
from utils.human_ids import humanize


def serialize_favorites(favorites: List[Favorite], current_user: UserSQLEntity) -> List:
    return [serialize_favorite(favorite, current_user) for favorite in favorites]


def serialize_favorite(favorite: Favorite, current_user: UserSQLEntity) -> Dict:
    offer = favorite.offer
    venue = offer.venue
    humanized_offer_id = humanize(offer.id)
    humanized_venue_id = humanize(venue.id)

    stocks = [{'beginningDatetime': stock.beginningDatetime, 'id': humanize(stock.id), 'offerId': humanized_offer_id} for stock in offer.stocks]

    serialized_favorite = {
        'id': humanize(favorite.id),
        'offerId': humanized_offer_id,
        'mediationId': humanize(favorite.mediationId),
        'offer': {
            'dateRange': serialize(offer.dateRange),
            'hasBookingLimitDatetimesPassed': offer.hasBookingLimitDatetimesPassed,
            'id': humanized_offer_id,
            'isActive': offer.isActive,
            'isFullyBooked': offer.isFullyBooked,
            'name': offer.name,
            'offerType': offer.offerType,
            'product': {
                'thumbUrl': offer.product.thumbUrl
            },
            'stocks': stocks,
            'venue': {
                'id': humanized_venue_id,
                'latitude': venue.latitude,
                'longitude': venue.longitude
            },
            'venueId': humanized_venue_id,
        },
        'thumbUrl': favorite.thumbUrl
    }

    user_booking = _get_user_booking_if_exists(current_user, offer.stocks)

    if user_booking:
        serialized_favorite['firstMatchingBooking'] = {
            'id': humanize(user_booking.id),
            'isCancelled': user_booking.isCancelled,
            'isUsed': user_booking.isUsed,
            'stockId': humanize(user_booking.stockId)
        }

    return serialized_favorite


def _get_user_booking_if_exists(current_user: UserSQLEntity, stocks: [StockSQLEntity]) -> BookingSQLEntity:
    user_booking = None
    for stock in stocks:
        user_booking = next((booking for booking in stock.bookings if booking.userId == current_user.id), None)
    return user_booking
