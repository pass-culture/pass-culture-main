from abc import ABC, abstractmethod
from typing import Dict

from pcapi.domain.booking.booking import Booking
from sqlalchemy.orm import Query


class BookingRepository(ABC):
    @abstractmethod
    def get_expenses_by_user_id(self, user_id: int) -> Dict:
        pass

    @abstractmethod
    def find_not_cancelled_booking_by(self, offer_id: int, user_id: int) -> Booking:
        pass

    @abstractmethod
    def save(self, booking: Booking) -> Booking:
        pass

    @abstractmethod
    def find_booking_by_id_and_beneficiary_id(self, booking_id: int, beneficiary_id: int) -> Booking:
        pass
