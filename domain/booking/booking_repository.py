from abc import ABC, abstractmethod
from typing import List

from domain.booking.booking import Booking


class BookingRepository(ABC):
    @abstractmethod
    def find_active_bookings_by_user_id(self, user_id: int) -> List[Booking]:
        pass

    @abstractmethod
    def find_not_cancelled_booking_by(self, offer_id: int, user_id: int) -> Booking:
        pass

    @abstractmethod
    def save(self, booking: Booking) -> Booking:
        pass

    @abstractmethod
    def find_booking_with_offerer(self, booking_id):
        pass
