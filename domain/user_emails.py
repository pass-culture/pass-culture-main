from typing import Callable, List

from emails.beneficiary_activation import get_activation_email_data
from emails.beneficiary_offer_cancellation import make_offerer_booking_recap_email_after_user_cancellation_data
from emails.offerer_booking_recap import get_offerer_booking_recap_email_data
from emails.pro_waiting_validation import make_pro_user_waiting_for_validation_data
from emails.user_reset_password import make_reset_password_email_data
from models import User, Stock, Booking, UserOfferer, Offerer, Venue
from repository import booking_queries
from repository.stock_queries import set_booking_recap_sent_and_save
from repository.user_queries import find_all_emails_of_user_offerers_admins
from utils.logger import logger
from utils.mailing import make_user_booking_recap_email, \
    make_offerer_driven_cancellation_email_for_user, \
    make_offerer_driven_cancellation_email_for_offerer, make_final_recap_email_for_stock_with_event, \
    make_validation_confirmation_email, make_batch_cancellation_email, \
    make_user_validation_email, \
    make_venue_validation_confirmation_email, compute_email_html_part_and_recipients, \
    ADMINISTRATION_EMAIL_ADDRESS


def send_final_booking_recap_email(stock: Stock, send_email: Callable[..., bool]) -> bool:
    stock_bookings = booking_queries.find_ongoing_bookings_by_stock(stock)
    if len(stock_bookings) == 0:
        logger.info("Not sending recap for  " + str(stock) + " as it has no bookings")
    email = make_final_recap_email_for_stock_with_event(stock)

    recipients = [ADMINISTRATION_EMAIL_ADDRESS]
    if stock.resolvedOffer.bookingEmail:
        recipients.append(stock.resolvedOffer.bookingEmail)

    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)

    successfully_sent = send_email(data=email)

    set_booking_recap_sent_and_save(stock)
    return successfully_sent


def send_booking_recap_emails(booking: Booking, send_email: Callable[..., bool]) -> bool:
    recipients = [ADMINISTRATION_EMAIL_ADDRESS]
    if booking.stock.resolvedOffer.bookingEmail:
        recipients.append(booking.stock.resolvedOffer.bookingEmail)

    email = get_offerer_booking_recap_email_data(booking, recipients)
    return send_email(data=email)


def send_booking_confirmation_email_to_user(booking: Booking, send_email: Callable[..., bool],
                                            is_cancellation: bool = False) -> bool:
    email = make_user_booking_recap_email(booking, is_cancellation)
    recipients = [booking.user.email]

    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)

    return send_email(data=email)


def send_user_driven_cancellation_email_to_user(booking: Booking, send_email: Callable[..., bool]) -> bool:
    email = make_user_booking_recap_email(booking, is_cancellation=True)
    recipients = [booking.user.email]

    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)

    return send_email(data=email)


def send_user_driven_cancellation_email_to_offerer(booking: Booking, send_email: Callable[..., bool]) -> bool:
    recipients = build_recipients_list(booking)
    mailjet_data = make_offerer_booking_recap_email_after_user_cancellation_data(booking, recipients)
    return send_email(data=mailjet_data)


def build_recipients_list(booking: Booking) -> str:
    recipients = []
    offerer_booking_email = booking.stock.resolvedOffer.bookingEmail
    if offerer_booking_email:
        recipients.append(offerer_booking_email)
    recipients.append(ADMINISTRATION_EMAIL_ADDRESS)
    return ", ".join(recipients)


def send_offerer_driven_cancellation_email_to_user(booking: Booking, send_email: Callable[..., bool]) -> bool:
    email = make_offerer_driven_cancellation_email_for_user(booking)
    recipients = [booking.user.email]
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    return send_email(data=email)


def send_offerer_driven_cancellation_email_to_offerer(booking: Booking, send_email: Callable[..., bool]) -> bool:
    offerer_email = booking.stock.resolvedOffer.bookingEmail
    recipients = []
    if offerer_email:
        recipients.append(offerer_email)
    recipients.append(ADMINISTRATION_EMAIL_ADDRESS)
    email = make_offerer_driven_cancellation_email_for_offerer(booking)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    return send_email(data=email)


def send_reset_password_email(user: User, send_email: Callable[..., bool], app_origin_url: str) -> bool:
    email = make_reset_password_email(user, app_origin_url)
    recipients = [user.email]
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    return send_email(data=email)


def send_reset_password_email_with_mailjet_template(user: User, send_email: Callable[..., bool]) -> bool:
    email = make_reset_password_email_data(user)
    return send_email(data=email)


def send_validation_confirmation_email(user_offerer: UserOfferer, offerer: Offerer,
                                       send_email: Callable[..., bool]) -> bool:
    offerer_id = _get_offerer_id(offerer, user_offerer)
    recipients = find_all_emails_of_user_offerers_admins(offerer_id)
    email = make_validation_confirmation_email(user_offerer, offerer)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    return send_email(data=email)


def send_batch_cancellation_emails_to_users(bookings: List[Booking], send_email: Callable[..., bool]) -> None:
    for booking in bookings:
        send_offerer_driven_cancellation_email_to_user(booking, send_email)


def send_batch_cancellation_email_to_offerer(bookings: List[Booking], cancellation_case: str,
                                             send_email: Callable[..., bool]) -> bool:
    booking = bookings[0] if bookings else None
    offerer_email = booking.stock.resolvedOffer.bookingEmail
    recipients = []
    if offerer_email:
        recipients.append(offerer_email)
    recipients.append(ADMINISTRATION_EMAIL_ADDRESS)
    email = make_batch_cancellation_email(bookings, cancellation_case)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    return send_email(data=email)


def send_cancellation_emails_to_user_and_offerer(booking: Booking, is_offerer_cancellation: bool,
                                                 is_user_cancellation: bool, send_email: Callable[..., bool]):
    if is_user_cancellation:
        send_user_driven_cancellation_email_to_user(booking, send_email)
        send_user_driven_cancellation_email_to_offerer(booking, send_email)
    if is_offerer_cancellation:
        send_offerer_driven_cancellation_email_to_user(booking, send_email)
        send_offerer_driven_cancellation_email_to_offerer(booking, send_email)


def send_venue_validation_confirmation_email(venue: Venue, send_email: Callable[..., bool]) -> bool:
    recipients = find_all_emails_of_user_offerers_admins(venue.managingOffererId)
    email = make_venue_validation_confirmation_email(venue)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    return send_email(data=email)


def send_user_validation_email(user: User, send_email: Callable[..., bool], app_origin_url: str, is_webapp) -> bool:
    email = make_user_validation_email(user, app_origin_url, is_webapp)
    return send_email(data=email)


def send_pro_user_waiting_for_validation_by_admin_email(user: User, send_email: Callable[..., bool],
                                                        offerer: Offerer) -> bool:
    email = make_pro_user_waiting_for_validation_data(user, offerer)
    return send_email(data=email)


def send_activation_email(user: User, send_email: Callable[..., bool]) -> bool:
    activation_email_data = get_activation_email_data(user)

    return send_email(activation_email_data)


def _get_offerer_id(offerer: Offerer, user_offerer: UserOfferer) -> int:
    if offerer is None:
        offerer_id = user_offerer.offerer.id
    else:
        offerer_id = offerer.id
    return offerer_id
