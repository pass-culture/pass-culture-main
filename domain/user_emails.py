from typing import Callable

from models import User
from repository.booking_queries import find_all_ongoing_bookings_by_stock
from repository.stock_queries import set_booking_recap_sent_and_save
from repository.user_queries import find_all_emails_of_user_offerers_admins
from utils.logger import logger
from utils.mailing import make_user_booking_recap_email, \
    make_offerer_booking_recap_email_after_user_action, make_offerer_driven_cancellation_email_for_user, \
    make_offerer_driven_cancellation_email_for_offerer, make_final_recap_email_for_stock_with_event, \
    save_email_information_if_send_create_failed, make_reset_password_email, make_validation_confirmation_email, make_batch_cancellation_email, \
    make_user_validation_email, make_venue_validation_confirmation_email, compute_email_html_part_and_recipients, \
    make_activation_notification_email


def send_final_booking_recap_email(stock, send_create_email):
    stock_bookings = find_all_ongoing_bookings_by_stock(stock)
    if len(stock_bookings) == 0:
        logger.info("Not sending recap for  " + str(stock) + " as it has no bookings")
    email = make_final_recap_email_for_stock_with_event(stock)

    recipients = ['support.passculture@beta.gouv.fr']
    if stock.resolvedOffer.bookingEmail:
        recipients.append(stock.resolvedOffer.bookingEmail)

    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)

    mail_result = send_create_email(data=email)
    save_email_information_if_send_create_failed(mail_result, email)

    set_booking_recap_sent_and_save(stock)


def send_booking_recap_emails(booking, send_create_email):
    email = make_offerer_booking_recap_email_after_user_action(booking)

    recipients = ['support.passculture@beta.gouv.fr']
    if booking.stock.resolvedOffer.bookingEmail:
        recipients.append(booking.stock.resolvedOffer.bookingEmail)

    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)

    mail_result = send_create_email(data=email)
    save_email_information_if_send_create_failed(mail_result, email)


def send_booking_confirmation_email_to_user(booking, send_create_email, is_cancellation=False):
    email = make_user_booking_recap_email(booking, is_cancellation)
    recipients = [booking.user.email]

    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)

    mail_result = send_create_email(data=email)
    save_email_information_if_send_create_failed(mail_result, email)


def send_user_driven_cancellation_email_to_user(booking, send_create_email):
    email = make_user_booking_recap_email(booking, is_cancellation=True)
    recipients = [booking.user.email]

    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)

    mail_result = send_create_email(data=email)
    save_email_information_if_send_create_failed(mail_result, email)


def send_user_driven_cancellation_email_to_offerer(booking, send_create_email):
    email = make_offerer_booking_recap_email_after_user_action(booking, is_cancellation=True)
    recipients = []
    offerer_booking_email = booking.stock.resolvedOffer.bookingEmail
    if offerer_booking_email:
        recipients.append(offerer_booking_email)
    recipients.append('support.passculture@beta.gouv.fr')
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    mail_result = send_create_email(data=email)
    save_email_information_if_send_create_failed(mail_result, email)


def send_offerer_driven_cancellation_email_to_user(booking, send_create_email):
    email = make_offerer_driven_cancellation_email_for_user(booking)
    recipients = [booking.user.email]
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    mail_result = send_create_email(data=email)
    save_email_information_if_send_create_failed(mail_result, email)


def send_offerer_driven_cancellation_email_to_offerer(booking, send_create_email):
    offerer_email = booking.stock.resolvedOffer.bookingEmail
    recipients = []
    if offerer_email:
        recipients.append(offerer_email)
    recipients.append('support.passculture@beta.gouv.fr')
    email = make_offerer_driven_cancellation_email_for_offerer(booking)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    mail_result = send_create_email(data=email)
    save_email_information_if_send_create_failed(mail_result, email)


def send_reset_password_email(user, send_create_email, app_origin_url):
    email = make_reset_password_email(user, app_origin_url)
    recipients = [user.email]
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    mail_result = send_create_email(data=email)
    save_email_information_if_send_create_failed(mail_result, email)


def send_validation_confirmation_email(user_offerer, offerer, send_create_email):
    offerer_id = _get_offerer_id(offerer, user_offerer)
    recipients = find_all_emails_of_user_offerers_admins(offerer_id)
    email = make_validation_confirmation_email(user_offerer, offerer)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    mail_result = send_create_email(data=email)
    save_email_information_if_send_create_failed(mail_result, email)


def send_batch_cancellation_emails_to_users(bookings, send_create_email):
    for booking in bookings:
        send_offerer_driven_cancellation_email_to_user(booking, send_create_email)


def send_batch_cancellation_email_to_offerer(bookings, cancellation_case, send_create_email):
    booking = bookings[0] if bookings else None
    offerer_email = booking.stock.resolvedOffer.bookingEmail
    recipients = []
    if offerer_email:
        recipients.append(offerer_email)
    recipients.append('support.passculture@beta.gouv.fr')
    email = make_batch_cancellation_email(bookings, cancellation_case)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    mail_result = send_create_email(data=email)
    save_email_information_if_send_create_failed(mail_result, email)


def send_cancellation_emails_to_user_and_offerer(booking, is_offerer_cancellation, is_user_cancellation,
                                                 send_create_email):
    if is_user_cancellation:
        send_user_driven_cancellation_email_to_user(booking, send_create_email)
        send_user_driven_cancellation_email_to_offerer(booking, send_create_email)
    if is_offerer_cancellation:
        send_offerer_driven_cancellation_email_to_user(booking, send_create_email)
        send_offerer_driven_cancellation_email_to_offerer(booking, send_create_email)


def send_venue_validation_confirmation_email(venue, send_create_email):
    recipients = find_all_emails_of_user_offerers_admins(venue.managingOffererId)
    email = make_venue_validation_confirmation_email(venue)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    mail_result = send_create_email(data=email)
    save_email_information_if_send_create_failed(mail_result, email)


def send_user_validation_email(user, send_create_email, app_origin_url, is_webapp):
    email = make_user_validation_email(user, app_origin_url, is_webapp)
    mail_result = send_create_email(data=email)
    save_email_information_if_send_create_failed(mail_result, email)


def send_activation_notification_email(user: User, send_create_email: Callable) -> None:
    email = make_activation_notification_email(user)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], [user.email])
    mail_result = send_create_email(data=email)
    save_email_information_if_send_create_failed(mail_result, email)


def _get_offerer_id(offerer, user_offerer):
    if offerer is None:
        offerer_id = user_offerer.offerer.id
    else:
        offerer_id = offerer.id
    return offerer_id
