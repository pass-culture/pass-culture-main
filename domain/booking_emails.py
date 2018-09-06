from pprint import pformat

from repository.features import feature_send_mail_to_users_enabled
from utils.config import ENV
from utils.mailing import make_user_booking_recap_email, MailServiceException, \
    make_offerer_booking_recap_email_after_user_action, make_offerer_driven_cancellation_email_for_user


def send_user_driven_cancellation_email_to_user(booking, send_create_email):
    email = make_user_booking_recap_email(booking, is_cancellation=True)
    recipients = [booking.user.email]

    email['Html-part'], email['To'] = _edit_email_html_part_and_recipients(email['Html-part'], recipients)

    mail_result = send_create_email(data=email)
    _check_if_email_sent(mail_result)


def send_user_driven_cancellation_email_to_offerer(booking, send_create_email):
    email = make_offerer_booking_recap_email_after_user_action(booking, is_cancellation=True)
    recipients = [booking.stock.resolvedOffer.venue.bookingEmail]
    email['Html-part'], email['To'] = _edit_email_html_part_and_recipients(email['Html-part'], recipients)
    mail_result = send_create_email(data=email)
    _check_if_email_sent(mail_result)


def send_offerer_driven_cancellation_email_to_user(booking, send_create_email):
    email = make_offerer_driven_cancellation_email_for_user(booking)


def send_offerer_driven_cancellation_email_to_offerer(booking, send_create_email):
    pass


def _edit_email_html_part_and_recipients(email_html_part, recipients):
    if feature_send_mail_to_users_enabled():
        email_to = ", ".join(recipients)
    else:
        email_html_part = ('<p>This is a test (ENV=%s). In production, email would have been sent to : ' % ENV) \
                              + ", ".join(recipients) \
                              + '</p>' + email_html_part
        email_to = 'passculture-dev@beta.gouv.fr'
    return email_html_part, email_to


def _check_if_email_sent(mail_result):
    if mail_result.status_code != 200:
        raise MailServiceException("Email send failed: " + pformat(vars(mail_result)))
