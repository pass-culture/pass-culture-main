from abc import ABC, abstractmethod
from typing import List

from domain.booking.booking import Booking


class BookingRepository(ABC):
    @abstractmethod
    def find_active_bookings_by_user_id(self, user_id: int) -> List[Booking]:
        pass

    @abstractmethod
    def save(self, booking: Booking) -> Booking:
        pass
