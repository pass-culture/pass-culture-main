from domain.booking.booking import Booking
from domain.services.notification.notification_service import NotificationService
from domain.user_emails import send_booking_recap_emails, send_booking_confirmation_email_to_beneficiary
from utils.logger import logger
from utils.mailing import send_raw_email, MailServiceException


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
