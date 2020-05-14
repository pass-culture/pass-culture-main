from abc import ABC, abstractmethod

from domain.booking.booking import Booking


class NotificationService(ABC):
    @abstractmethod
    def send_booking_recap(self, booking: Booking) -> None:
        pass

    @abstractmethod
    def send_booking_confirmation_to_beneficiary(self, booking: Booking) -> None:
        pass
