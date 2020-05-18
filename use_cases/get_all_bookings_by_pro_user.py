from typing import List

from domain.booking_recap.booking_recap import BookingRecap
from domain.users import check_is_authorized_to_access_bookings_recap
from repository import user_queries, booking_queries


def get_all_bookings_by_pro_user(user_id: int, page: int = 0, per_page_limit=20) -> List[BookingRecap]:
    user = user_queries.find_user_by_id(user_id)
    check_is_authorized_to_access_bookings_recap(user)

    booking_recap = booking_queries.find_by_pro_user_id(user_id)

    return booking_recap
