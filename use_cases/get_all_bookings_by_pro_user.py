from domain.booking_recap.bookings_recap_paginated import BookingsRecapPaginated
from domain.users import check_is_authorized_to_access_bookings_recap
from repository import user_queries, booking_queries


def get_all_bookings_by_pro_user(user_id: int, page: int = 0) -> BookingsRecapPaginated:
    user = user_queries.find_user_by_id(user_id)
    check_is_authorized_to_access_bookings_recap(user)

    booking_recap = booking_queries.find_by_pro_user_id(user_id=user_id, page=page)

    return booking_recap
