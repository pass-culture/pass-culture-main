from pprint import pformat

from repository.features import feature_send_mail_to_users_enabled
from utils.config import ENV
from utils.mailing import make_user_booking_recap_email, MailServiceException


def send_user_driven_cancellation_email_to_user(booking, send_create_email):
    email = make_user_booking_recap_email(booking, is_cancellation=True)
    recipients = [booking.user.email]

    if feature_send_mail_to_users_enabled():
        email['To'] = ", ".join(recipients)
    else:
        email['Html-part'] = ('<p>This is a test (ENV=%s). In production, email would have been sent to : ' % ENV) \
                             + ", ".join(recipients) \
                             + '</p>' + email['Html-part']
        email['To'] = 'passculture-dev@beta.gouv.fr'

    mail_result = send_create_email(data=email)
    if mail_result.status_code != 200:
        raise MailServiceException("Email send failed: " + pformat(vars(mail_result)))