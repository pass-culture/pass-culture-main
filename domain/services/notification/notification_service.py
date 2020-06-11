from abc import ABC, abstractmethod
from typing import Callable

from domain.booking.booking import Booking
from domain.booking.booking_with_offerer.booking_with_offerer import BookingWithOfferer


class NotificationService(ABC):
    @abstractmethod
    def send_booking_recap(self, booking: Booking) -> None:
        pass

    @abstractmethod
    def send_booking_confirmation_to_beneficiary(self, booking: Booking) -> None:
        pass

    @abstractmethod
    def send_booking_cancellation_emails_to_user_and_offerer(self,
                                                             booking: BookingWithOfferer,
                                                             is_offerer_cancellation: bool,
                                                             is_user_cancellation: bool,
                                                             send_email: Callable[..., bool]):
        pass
