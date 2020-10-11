from abc import ABC, abstractmethod
from typing import Callable

from pcapi.core.bookings.models import BookingSQLEntity
from pcapi.domain.beneficiary_contact.beneficiary_contact import BeneficiaryContact


class NotificationService(ABC):
    @abstractmethod
    def send_booking_recap(self, booking: BookingSQLEntity) -> None:
        pass

    @abstractmethod
    def send_booking_confirmation_to_beneficiary(self, booking: BookingSQLEntity) -> None:
        pass

    @abstractmethod
    def send_booking_cancellation_emails_to_user_and_offerer(self,
                                                             booking: BookingSQLEntity,
                                                             is_offerer_cancellation: bool,
                                                             is_user_cancellation: bool,
                                                             send_email: Callable[..., bool]):
        pass

    @abstractmethod
    def create_mailing_contact(self, beneficiary_contact: BeneficiaryContact) -> None:
        pass

    @abstractmethod
    def add_contact_to_eligible_soon_list(self, beneficiary_contact: BeneficiaryContact) -> None:
        pass
