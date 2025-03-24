from pcapi.core import mails
from pcapi.core.bookings.models import Booking
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.utils import format_price
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.mailing import get_event_datetime


def get_booking_cancellation_confirmation_by_pro_email_data(
    bookings: list[Booking],
) -> models.TransactionalEmailData:
    booking = bookings[0]
    stock = booking.stock
    offer = stock.offer
    event_date = get_date_formatted_for_email(get_event_datetime(stock)) if stock.beginningDatetime else ""
    event_hour = get_time_formatted_for_email(get_event_datetime(stock)) if stock.beginningDatetime else ""
    offer_price = str(stock.price) if stock.price > 0 else "Gratuit"
    quantity = sum(booking.quantity for booking in bookings)

    return models.TransactionalEmailData(
        template=TransactionalEmail.BOOKING_CANCELLATION_CONFIRMATION_BY_PRO.value,
        params={
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.common_name,
            "PRICE": offer_price,
            "FORMATTED_PRICE": format_price(stock.price, offer.venue),
            "IS_EVENT": offer.isEvent,
            "IS_EXTERNAL": booking.isExternal,
            "EVENT_DATE": event_date,
            "EVENT_HOUR": event_hour,
            "QUANTITY": quantity,
            "RESERVATIONS_NUMBER": len(bookings),
            "OFFER_ADDRESS": offer.fullAddress,
        },
    )


def get_collective_booking_cancellation_confirmation_by_pro_email_data(
    booking: CollectiveBooking,
) -> models.TransactionalEmailData:
    stock = booking.collectiveStock
    offer = stock.collectiveOffer
    event_date = get_date_formatted_for_email(get_event_datetime(stock)) if stock.startDatetime else ""
    event_hour = get_time_formatted_for_email(get_event_datetime(stock)) if stock.startDatetime else ""
    offer_price = str(stock.price) if stock.price > 0 else "Gratuit"

    return models.TransactionalEmailData(
        template=TransactionalEmail.BOOKING_CANCELLATION_CONFIRMATION_BY_PRO.value,
        params={
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.common_name,
            "PRICE": offer_price,
            "FORMATTED_PRICE": format_price(stock.price, offer.venue),
            "IS_EVENT": True,
            "EVENT_DATE": event_date,
            "EVENT_HOUR": event_hour,
            "QUANTITY": 1,
            "RESERVATIONS_NUMBER": 1,
        },
    )


def send_booking_cancellation_confirmation_by_pro_email(bookings: list[Booking]) -> None:
    offerer_booking_email = bookings[0].stock.offer.bookingEmail
    if not offerer_booking_email:
        return
    data = get_booking_cancellation_confirmation_by_pro_email_data(bookings)
    mails.send(recipients=[offerer_booking_email], data=data)


def send_collective_booking_cancellation_confirmation_by_pro_email(booking: CollectiveBooking) -> None:
    offerer_booking_emails = booking.collectiveStock.collectiveOffer.bookingEmails
    if not offerer_booking_emails:
        return
    data = get_collective_booking_cancellation_confirmation_by_pro_email_data(booking)
    main_recipient, bcc_recipients = [offerer_booking_emails[0]], offerer_booking_emails[1:]
    mails.send(recipients=main_recipient, bcc_recipients=bcc_recipients, data=data)
