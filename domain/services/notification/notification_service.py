from abc import ABC, abstractmethod

from domain.booking.booking import Booking


class NotificationService(ABC):
    @abstractmethod
    def send_booking_recap_emails(self, booking: Booking) -> None:
        pass

    @abstractmethod
    def send_booking_confirmation_email_to_beneficiary(self, booking: Booking) -> None:
        pass
