from abc import ABC
from abc import abstractmethod
from typing import Callable

from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.domain.beneficiary_contact.beneficiary_contact import BeneficiaryContact


class NotificationService(ABC):
    @abstractmethod
    def send_booking_recap(self, booking: Booking) -> None:
        pass

    @abstractmethod
    def send_booking_confirmation_to_beneficiary(self, booking: Booking) -> None:
        pass

    @abstractmethod
    def send_booking_cancellation_emails_to_user_and_offerer(
        self,
        booking: Booking,
        reason: BookingCancellationReasons,
        send_email: Callable[..., bool],
    ) -> None:
        pass

    @abstractmethod
    def create_mailing_contact(self, beneficiary_contact: BeneficiaryContact) -> None:
        pass

    @abstractmethod
    def add_contact_to_eligible_soon_list(self, beneficiary_contact: BeneficiaryContact) -> None:
        pass
