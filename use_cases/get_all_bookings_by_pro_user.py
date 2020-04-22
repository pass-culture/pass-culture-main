from typing import List

from domain.booking_recap.booking_recap import BookingRecap
from domain.users import check_user_is_not_admin
from repository import user_queries, booking_queries


def get_all_bookings_by_pro_user(user_id: int) -> List[BookingRecap]:
    user = user_queries.find_user_by_id(user_id)
    check_user_is_not_admin(user)

    booking_recap = booking_queries.find_by_pro_user_id(user_id)

    return booking_recap
