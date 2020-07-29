from typing import Dict

from models import OfferSQLEntity, UserSQLEntity
from repository.booking_queries import find_first_matching_from_offer_by_user
from routes.serialization.dictifier import as_dict
from utils.includes import OFFER_INCLUDES, \
    WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES


def serialize_offer(offer: OfferSQLEntity, current_user: UserSQLEntity) -> Dict:
    dict_offer = as_dict(offer, includes=OFFER_INCLUDES)

    booking = find_first_matching_from_offer_by_user(offer.id, current_user.id)
    if booking:
        dict_offer['firstMatchingBooking'] = as_dict(
            booking, includes=WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES)

    return dict_offer
