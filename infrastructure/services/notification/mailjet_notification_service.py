import os
from typing import Callable
from datetime import datetime

from domain.booking.booking import Booking
from domain.beneficiary_contact.beneficiary_contact import BeneficiaryContact
from domain.services.notification.notification_service import NotificationService
from domain.user_emails import send_booking_recap_emails, send_booking_confirmation_email_to_beneficiary, \
    send_booking_cancellation_emails_to_user_and_offerer
from infrastructure.repository.booking import booking_domain_converter
from utils.logger import logger
from utils.mailing import send_raw_email, create_contact, add_contact_informations, add_contact_to_list, MailServiceException
from domain.beneficiary_contact.beneficiary_contact_exceptions import AddNewBeneficiaryContactException


class MailjetNotificationService(NotificationService):
    def send_booking_recap(self, booking: Booking) -> None:
        try:
            send_booking_recap_emails(booking, send_raw_email)
        except MailServiceException as error:
            logger.error('Mail service failure', error)

    def send_booking_confirmation_to_beneficiary(self, booking: Booking) -> None:
        try:
            send_booking_confirmation_email_to_beneficiary(booking, send_raw_email)
        except MailServiceException as error:
            logger.error('Mail service failure', error)

    def send_booking_cancellation_emails_to_user_and_offerer(self,
                                                             booking: Booking,
                                                             is_offerer_cancellation: bool,
                                                             is_user_cancellation: bool,
                                                             send_email: Callable[..., bool]):
        booking_sql_entity = booking_domain_converter.to_model(booking)
        try:
            send_booking_cancellation_emails_to_user_and_offerer(booking_sql_entity,
                                                                 is_offerer_cancellation,
                                                                 is_user_cancellation,
                                                                 send_raw_email)
        except MailServiceException as error:
            logger.error('Mail service failure', error)


    def create_mailing_contact(self, beneficiary_contact: BeneficiaryContact) -> None:
        creation_response = create_contact(beneficiary_contact.email)

        status_code = creation_response.status_code
        if status_code != 201 and status_code != 400:
            raise AddNewBeneficiaryContactException('mailjet', creation_response.reason)

        date_of_birth = datetime.fromisoformat(beneficiary_contact.date_of_birth)
        date_of_birth_timestamp = int(datetime(date_of_birth.year, date_of_birth.month, date_of_birth.day).timestamp())
        update_response = add_contact_informations(beneficiary_contact.email, date_of_birth_timestamp, beneficiary_contact.department_code)

        status_code = update_response.status_code
        if status_code != 200 and status_code != 400:
            raise AddNewBeneficiaryContactException('mailjet', update_response.reason)


    def add_contact_to_eligible_soon_list(self, beneficiary_contact: BeneficiaryContact) -> None:
        list_id = os.environ.get('MAILJET_NOT_YET_ELIGIBLE_LIST_ID')
        add_to_list_response = add_contact_to_list(beneficiary_contact.email, list_id)

        status_code = add_to_list_response.status_code
        if status_code != 201 and status_code != 400:
            raise AddNewBeneficiaryContactException('mailjet', add_to_list_response.reason)
