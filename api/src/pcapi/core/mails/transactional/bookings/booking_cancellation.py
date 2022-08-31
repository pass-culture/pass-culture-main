from flask import render_template

from pcapi.core import mails
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.repository import find_ongoing_bookings_by_stock
from pcapi.core.mails import models
from pcapi.core.mails.transactional.bookings.booking_cancellation_by_beneficiary import (
    send_booking_cancellation_by_beneficiary_email,
)
from pcapi.core.mails.transactional.bookings.booking_cancellation_by_beneficiary_to_pro import (
    send_booking_cancellation_by_beneficiary_to_pro_email,
)
from pcapi.core.mails.transactional.bookings.booking_cancellation_by_pro_to_beneficiary import (
    send_booking_cancellation_by_pro_to_beneficiary_email,
)
from pcapi.utils.date import format_datetime
from pcapi.utils.mailing import get_event_datetime


def send_booking_cancellation_emails_to_user_and_offerer(
    booking: Booking,
    reason: BookingCancellationReasons,
) -> bool:
    if reason == BookingCancellationReasons.BENEFICIARY and booking.individualBooking is not None:
        send_booking_cancellation_by_beneficiary_email(booking.individualBooking)
        return send_booking_cancellation_by_beneficiary_to_pro_email(booking)
    if reason == BookingCancellationReasons.OFFERER:
        send_booking_cancellation_by_pro_to_beneficiary_email(booking)
        return send_booking_cancellation_confirmation_by_pro_to_pro_email(booking)
    if reason == BookingCancellationReasons.FRAUD:
        return send_booking_cancellation_by_beneficiary_to_pro_email(booking)
    return True


def send_booking_cancellation_confirmation_by_pro_to_pro_email(booking: Booking) -> bool:
    offerer_booking_email = booking.stock.offer.bookingEmail
    if not offerer_booking_email:
        return True
    email = get_booking_cancellation_confirmation_by_pro_email_data(booking)
    return mails.send(recipients=[offerer_booking_email], data=email)


def get_booking_cancellation_confirmation_by_pro_email_data(
    booking: Booking,
) -> models.SendinblueTransactionalWithoutTemplateEmailData:
    stock_name = booking.stock.offer.name
    venue = booking.venue
    user_name = booking.userName
    user_email = booking.email
    email_subject = "Confirmation de votre annulation de réservation pour {}, proposé par {}".format(
        stock_name, venue.name
    )
    ongoing_stock_bookings = find_ongoing_bookings_by_stock(booking.stock.id)
    stock_date_time = None
    booking_is_on_event = booking.stock.beginningDatetime is not None
    if booking_is_on_event:
        date_in_tz = get_event_datetime(booking.stock)
        stock_date_time = format_datetime(date_in_tz)
    email_html = render_template(
        "mails/offerer_recap_email_after_offerer_cancellation.html",
        booking_is_on_event=booking_is_on_event,
        user_name=user_name,
        user_email=user_email,
        stock_date_time=stock_date_time,
        number_of_bookings=len(ongoing_stock_bookings),
        stock_bookings=ongoing_stock_bookings,
        stock_name=stock_name,
        venue=venue,
    )

    return models.SendinblueTransactionalWithoutTemplateEmailData(
        subject=email_subject,
        html_content=email_html,
    )
