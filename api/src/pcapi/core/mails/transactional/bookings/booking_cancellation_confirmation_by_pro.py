from pcapi.core import mails
from pcapi.core.bookings.models import Booking
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.utils.mailing import format_booking_date_for_email
from pcapi.utils.mailing import format_booking_hours_for_email


def get_booking_cancellation_confirmation_by_pro_email_data(
    bookings: list[Booking],
) -> SendinblueTransactionalEmailData:
    booking = bookings[0]
    stock = booking.stock
    offer = stock.offer
    event_date = format_booking_date_for_email(booking)
    event_hour = format_booking_hours_for_email(booking)
    offer_price = str(stock.price) if stock.price > 0 else "Gratuit"
    quantity = sum([booking.quantity for booking in bookings])
    venue_name = offer.venue.publicName if offer.venue.publicName else offer.venue.name

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.BOOKING_CANCELLATION_CONFIRMATION_BY_PRO.value,
        params={
            "OFFER_NAME": offer.name,
            "VENUE_NAME": venue_name,
            "PRICE": offer_price,
            "IS_EVENT": offer.isEvent,
            "EVENT_DATE": event_date,
            "EVENT_HOUR": event_hour,
            "QUANTITY": quantity,
            "RESERVATIONS_NUMBER": len(bookings),
        },
    )


def send_booking_cancellation_confirmation_by_pro_email(bookings: list[Booking]) -> bool:
    offerer_booking_email = bookings[0].stock.offer.bookingEmail
    if not offerer_booking_email:
        return True
    data = get_booking_cancellation_confirmation_by_pro_email_data(bookings)
    return mails.send(recipients=[offerer_booking_email], data=data)
