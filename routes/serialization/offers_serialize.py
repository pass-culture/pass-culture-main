from typing import Dict

from domain.offers import find_first_matching_booking_from_offer_by_user
from models import Offer, User
from routes.serialization.dictifier import as_dict
from utils.includes import OFFER_INCLUDES, \
    WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES


def serialize_offer(offer: Offer, current_user: User) -> Dict:
    dict_offer = as_dict(offer, includes=OFFER_INCLUDES)

    booking = find_first_matching_booking_from_offer_by_user(offer, current_user)
    if booking:
        dict_offer['firstMatchingBooking'] = as_dict(
            booking, includes=WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES)

    return dict_offer
