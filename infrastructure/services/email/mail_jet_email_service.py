from domain.booking.booking import Booking
from domain.services.email.email_service import EmailService
from domain.user_emails import send_booking_recap_emails
from utils.logger import logger
from utils.mailing import send_raw_email, MailServiceException


class MailJetEmailService(EmailService):
    def send_booking_recap_emails(self, booking: Booking) -> None:
        try:
            send_booking_recap_emails(booking, send_raw_email)
        except MailServiceException as error:
            logger.error('Mail service failure', error)
