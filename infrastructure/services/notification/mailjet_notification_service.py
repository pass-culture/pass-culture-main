from typing import Callable

from domain.booking.booking import Booking
from domain.services.notification.notification_service import NotificationService
from domain.user_emails import send_booking_recap_emails, send_booking_confirmation_email_to_beneficiary, \
    send_booking_cancellation_emails_to_user_and_offerer
from infrastructure.repository.booking import booking_domain_converter
from utils.logger import logger
from utils.mailing import send_raw_email, MailServiceException


class MailjetNotificationService(NotificationService):
    def send_booking_cancellation_emails_to_user_and_offerer(self,
                                                             booking: Booking,
                                                             is_offerer_cancellation: bool,
                                                             is_user_cancellation: bool,
                                                             send_email: Callable[..., bool]):
        booking_with_offerer_sql_entity = booking_domain_converter.to_model(booking)
        try:
            send_booking_cancellation_emails_to_user_and_offerer(booking_with_offerer_sql_entity,
                                                                 is_offerer_cancellation,
                                                                 is_user_cancellation,
                                                                 send_raw_email)
        except MailServiceException as error:
            logger.error('Mail service failure', error)

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
