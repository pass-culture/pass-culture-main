from abc import ABC, abstractmethod

from domain.booking.booking import Booking


class EmailService(ABC):
    @abstractmethod
    def send_booking_recap_emails(self, booking: Booking) -> None:
        pass
