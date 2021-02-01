from datetime import datetime

from pcapi import settings
from pcapi.core import mails
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.domain.beneficiary_contact.beneficiary_contact import BeneficiaryContact
from pcapi.domain.beneficiary_contact.beneficiary_contact_exceptions import AddNewBeneficiaryContactException
from pcapi.domain.services.notification.notification_service import NotificationService
from pcapi.domain.user_emails import send_booking_cancellation_emails_to_user_and_offerer
from pcapi.domain.user_emails import send_booking_confirmation_email_to_beneficiary
from pcapi.domain.user_emails import send_booking_recap_emails
from pcapi.utils.logger import logger
from pcapi.utils.mailing import MailServiceException


class MailjetNotificationService(NotificationService):
    def send_booking_recap(self, booking: Booking) -> None:
        try:
            send_booking_recap_emails(booking)
        except MailServiceException as error:
            logger.exception("Could not send booking recap emails: %s", error)

    def send_booking_confirmation_to_beneficiary(self, booking: Booking) -> None:
        try:
            send_booking_confirmation_email_to_beneficiary(booking)
        except MailServiceException as error:
            logger.exception("Could not send booking confirmation email to beneficiary: %s", error)

    def send_booking_cancellation_emails_to_user_and_offerer(
        self,
        booking: Booking,
        reason: BookingCancellationReasons,
    ):
        try:
            send_booking_cancellation_emails_to_user_and_offerer(booking, reason)
        except MailServiceException as error:
            logger.exception("Could not send booking cancellation emails to user and offerer: %s", error)

    def create_mailing_contact(self, beneficiary_contact: BeneficiaryContact) -> None:
        creation_response = mails.create_contact(beneficiary_contact.email)

        status_code = creation_response.status_code
        if status_code not in (201, 400):
            raise AddNewBeneficiaryContactException("mailjet", creation_response.reason)

        birth_date = datetime.fromisoformat(beneficiary_contact.date_of_birth)
        update_response = mails.update_contact(
            beneficiary_contact.email, birth_date=birth_date, department=beneficiary_contact.department_code
        )

        status_code = update_response.status_code
        if status_code not in (200, 400):
            raise AddNewBeneficiaryContactException("mailjet", update_response.reason)

    def add_contact_to_eligible_soon_list(self, beneficiary_contact: BeneficiaryContact) -> None:
        list_id = settings.MAILJET_NOT_YET_ELIGIBLE_LIST_ID
        add_to_list_response = mails.add_contact_to_list(beneficiary_contact.email, list_id)

        status_code = add_to_list_response.status_code
        if status_code not in (201, 400):
            raise AddNewBeneficiaryContactException("mailjet", add_to_list_response.reason)
