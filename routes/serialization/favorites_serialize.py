from typing import List

from repository.booking_queries import find_first_matching_from_offer_by_user
from models import Favorite, UserSQLEntity
from routes.serialization.dictifier import as_dict
from utils.includes import FAVORITE_INCLUDES, \
    WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES


def serialize_favorites(favorites: List[Favorite], current_user: UserSQLEntity) -> List:
    return [serialize_favorite(favorite, current_user) for favorite in favorites]


def serialize_favorite(favorite: Favorite, current_user: UserSQLEntity) -> dict:
    dict_favorite = as_dict(favorite, includes=FAVORITE_INCLUDES)

    booking = find_first_matching_from_offer_by_user(favorite.offer.id, current_user.id)
    if booking:
        dict_favorite['firstMatchingBooking'] = as_dict(
            booking, includes=WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES)

    return dict_favorite
