from typing import List

from domain.users import check_user_is_not_admin
from models import Booking
from repository import user_queries, booking_queries


def get_all_bookings_by_pro_user(user_id: int) -> List[Booking]:
    user = user_queries.find_user_by_id(user_id)
    check_user_is_not_admin(user)

    bookings = booking_queries.find_by_pro_user_id(user_id)

    return bookings
