from typing import List

from pcapi.domain.booking_recap.booking_recap import BookingRecap


class BookingsRecapPaginated:
    def __init__(self,
                 bookings_recap: List[BookingRecap],
                 page: int,
                 pages: int,
                 total: int,
                 ):
        self.bookings_recap = bookings_recap
        self.page = page
        self.pages = pages
        self.total = total
