from pcapi.domain.favorite.favorite import FavoriteDomain
from pcapi.routes.serialization.serializer import serialize
from pcapi.utils.human_ids import humanize


def serialize_favorites(favorites: list[FavoriteDomain]) -> list:
    return [serialize_favorite(favorite) for favorite in favorites]


def serialize_favorite(favorite: FavoriteDomain) -> dict:
    offer = favorite.offer
    venue = offer.venue
    humanized_offer_id = humanize(offer.id)
    humanized_venue_id = humanize(venue.id)

    stocks = [
        {
            "beginningDatetime": stock.beginningDatetime,
            "id": humanize(stock.id),
            "offerId": humanized_offer_id,
            "price": stock.price,
        }
        for stock in offer.stocks
    ]

    serialized_favorite = {
        "id": humanize(favorite.identifier),
        "offerId": humanized_offer_id,
        "mediationId": (humanize(favorite.mediation.id) if favorite.mediation else None),
        "offer": {
            "dateRange": serialize(offer.dateRange),
            "hasBookingLimitDatetimesPassed": offer.hasBookingLimitDatetimesPassed,
            "id": humanized_offer_id,
            "isActive": offer.isActive,
            "name": offer.name,
            "offerType": offer.offerType,
            "stocks": stocks,
            "subcategoryId": offer.subcategoryId,
            "venue": {"id": humanized_venue_id, "latitude": venue.latitude, "longitude": venue.longitude},
            "venueId": humanized_venue_id,
        },
        "thumbUrl": favorite.thumb_url,
    }

    if favorite.is_booked:
        serialized_favorite["booking"] = {
            "id": humanize(favorite.booking_identifier),
            "stockId": humanize(favorite.booked_stock_identifier),
            "quantity": favorite.booking_quantity,
        }

    return serialized_favorite
