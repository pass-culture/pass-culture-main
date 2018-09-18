from repository.booking_queries import find_all_ongoing_bookings_by_stock
from repository.features import feature_send_mail_to_users_enabled
from repository.stock_queries import set_booking_recap_sent_and_save
from repository.user_offerer_queries import find_user_offerer_email
from utils.config import ENV
from utils.logger import logger
from utils.mailing import make_user_booking_recap_email, \
    make_offerer_booking_recap_email_after_user_action, make_offerer_driven_cancellation_email_for_user, \
    make_offerer_driven_cancellation_email_for_offerer, make_final_recap_email_for_stock_with_event, \
    check_if_email_sent, make_reset_password_email, write_object_validation_email, make_validation_confirmation_email


def send_final_booking_recap_email(stock, send_create_email):
    stock_bookings = find_all_ongoing_bookings_by_stock(stock)
    if len(stock_bookings) == 0:
        logger.info("Not sending recap for  " + str(stock) + " as it has no bookings")
    email = make_final_recap_email_for_stock_with_event(stock)

    recipients = ['passculture@beta.gouv.fr']
    if stock.resolvedOffer.bookingEmail:
        recipients.append(stock.resolvedOffer.bookingEmail)

    email['Html-part'], email['To'] = _edit_email_html_part_and_recipients(email['Html-part'], recipients)

    mail_result = send_create_email(data=email)
    check_if_email_sent(mail_result)

    set_booking_recap_sent_and_save(stock)


def send_booking_recap_emails(booking, send_create_email):
    email = make_offerer_booking_recap_email_after_user_action(booking)

    recipients = ['passculture@beta.gouv.fr']
    if booking.stock.resolvedOffer.bookingEmail:
        recipients.append(booking.stock.resolvedOffer.bookingEmail)

    email['Html-part'], email['To'] = _edit_email_html_part_and_recipients(email['Html-part'], recipients)

    mail_result = send_create_email(data=email)
    check_if_email_sent(mail_result)


def send_booking_confirmation_email_to_user(booking, send_create_email, is_cancellation=False):
    email = make_user_booking_recap_email(booking, is_cancellation)
    recipients = [booking.user.email]

    email['Html-part'], email['To'] = _edit_email_html_part_and_recipients(email['Html-part'], recipients)

    mail_result = send_create_email(data=email)
    check_if_email_sent(mail_result)


def send_user_driven_cancellation_email_to_user(booking, send_create_email):
    email = make_user_booking_recap_email(booking, is_cancellation=True)
    recipients = [booking.user.email]

    email['Html-part'], email['To'] = _edit_email_html_part_and_recipients(email['Html-part'], recipients)

    mail_result = send_create_email(data=email)
    check_if_email_sent(mail_result)


def send_user_driven_cancellation_email_to_offerer(booking, send_create_email):
    email = make_offerer_booking_recap_email_after_user_action(booking, is_cancellation=True)
    recipients = [booking.stock.resolvedOffer.venue.bookingEmail]
    email['Html-part'], email['To'] = _edit_email_html_part_and_recipients(email['Html-part'], recipients)
    mail_result = send_create_email(data=email)
    check_if_email_sent(mail_result)


def send_offerer_driven_cancellation_email_to_user(booking, send_create_email):
    email = make_offerer_driven_cancellation_email_for_user(booking)
    recipients = [booking.user.email]
    email['Html-part'], email['To'] = _edit_email_html_part_and_recipients(email['Html-part'], recipients)
    mail_result = send_create_email(data=email)
    check_if_email_sent(mail_result)


def send_offerer_driven_cancellation_email_to_offerer(booking, send_create_email):
    offerer_email = booking.stock.resolvedOffer.venue.bookingEmail
    if offerer_email:
        recipients = [offerer_email]
        email = make_offerer_driven_cancellation_email_for_offerer(booking)
        email['Html-part'], email['To'] = _edit_email_html_part_and_recipients(email['Html-part'], recipients)
        mail_result = send_create_email(data=email)
        check_if_email_sent(mail_result)


def send_reset_password_email(user, send_create_email, app_origin_url):
    email = make_reset_password_email(user, app_origin_url)
    mail_result = send_create_email(data=email)
    check_if_email_sent(mail_result)


def send_validation_confirmation_email(user_offerer, offerer, send_create_email):
    recipients = [find_user_offerer_email(user_offerer.id)]
    email = make_validation_confirmation_email(user_offerer, offerer)
    email['Html-part'], email['To'] = _edit_email_html_part_and_recipients(email['Html-part'], recipients)
    mail_result = send_create_email(data=email)
    check_if_email_sent(mail_result)


def _edit_email_html_part_and_recipients(email_html_part, recipients):
    if feature_send_mail_to_users_enabled():
        email_to = ", ".join(recipients)
    else:
        email_html_part = ('<p>This is a test (ENV=%s). In production, email would have been sent to : ' % ENV) \
                          + ", ".join(recipients) \
                          + '</p>' + email_html_part
        email_to = 'passculture-dev@beta.gouv.fr'
    return email_html_part, email_to
