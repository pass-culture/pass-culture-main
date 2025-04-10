import logging

from pcapi.core import mails
from pcapi.core.bookings.models import Booking
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.utils import format_price
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.mailing import get_event_datetime


logger = logging.getLogger(__name__)


def get_booking_cancellation_by_beneficiary_to_pro_email_data(
    booking: Booking, one_side_cancellation: bool = False
) -> models.TransactionalEmailData:
    external_booking_information = None
    provider_name = None  # need to be filled only in case of one side cancellation
    if one_side_cancellation:
        external_booking = booking.externalBookings[0]
        assert booking.stock.offer.lastProvider  # helps mypy, should be the case with one_side_cancellation set to True
        provider_name = booking.stock.offer.lastProvider.name
        match booking.stock.offer.lastProvider.localClass:
            case "CDSStocks" | "CGRStocks":
                external_booking_information = f"barcode: {external_booking.barcode}"
            case "EMSStocks":
                external_booking_information = f"barcode: {external_booking.barcode}, additional_information: {external_booking.additional_information}"
            case _:
                logger.error(
                    "Unexpected case in send_booking_cancelled_unilaterally_provider_support_email",
                    extra={"booking_id": booking.id},
                )

    return models.TransactionalEmailData(
        template=TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO.value,
        params={
            "EVENT_DATE": (
                get_date_formatted_for_email(get_event_datetime(booking.stock))
                if booking.stock.beginningDatetime
                else ""
            ),
            "EVENT_HOUR": (
                get_time_formatted_for_email(get_event_datetime(booking.stock))
                if booking.stock.beginningDatetime
                else ""
            ),
            "EXTERNAL_BOOKING_INFORMATION": external_booking_information,
            "IS_EVENT": booking.stock.offer.isEvent,
            "IS_EXTERNAL": booking.isExternal,
            "OFFER_NAME": booking.stock.offer.name,
            "PRICE": booking.stock.price if booking.stock.price > 0 else "Gratuit",
            "FORMATTED_PRICE": format_price(booking.stock.price, booking.stock.offer.venue),
            "PROVIDER_NAME": provider_name,
            "QUANTITY": booking.quantity,
            "USER_EMAIL": booking.email,
            "USER_NAME": f"{booking.firstName} {booking.lastName}",
            "VENUE_NAME": booking.stock.offer.venue.common_name,
            "OFFER_ADDRESS": booking.stock.offer.fullAddress,
        },
        reply_to=models.EmailInfo(
            email=booking.email,
            name=f"{booking.firstName} {booking.lastName}",
        ),
    )


def send_booking_cancellation_by_beneficiary_to_pro_email(
    booking: Booking, one_side_cancellation: bool = False
) -> None:
    offer_booking_email = booking.stock.offer.bookingEmail
    if not offer_booking_email:
        return
    data = get_booking_cancellation_by_beneficiary_to_pro_email_data(booking, one_side_cancellation)
    mails.send(recipients=[offer_booking_email], data=data)
