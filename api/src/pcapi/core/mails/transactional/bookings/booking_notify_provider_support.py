import logging

from pcapi import settings
from pcapi.core import mails
from pcapi.core.bookings.models import Booking
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


logger = logging.getLogger(__name__)


def get_booking_cancelled_unilaterally_provider_support_email_data(
    external_booking_information: str,
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.EXTERNAL_BOOKING_SUPPORT_CANCELLATION.value,
        params={"EXTERNAL_BOOKING_INFORMATION": external_booking_information},
    )


def send_booking_cancelled_unilaterally_provider_support_email(booking: Booking) -> None:
    external_booking = booking.externalBookings[0]
    match booking.stock.offer.lastProvider.localClass:
        case "CDSStocks":
            recipient = settings.CDS_SUPPORT_EMAIL_ADDRESS
            external_booking_information = f"barcode: {external_booking.barcode}"
        case "CGRStocks":
            recipient = settings.CGR_SUPPORT_EMAIL_ADDRESS
            external_booking_information = f"barcode: {external_booking.barcode}"
        case "EMSStocks":
            recipient = settings.EMS_SUPPORT_EMAIL_ADDRESS
            external_booking_information = f"barcode: {external_booking.barcode}, additional_information: {external_booking.additional_information}"
        case _:
            logger.error(
                "Unexpected case in send_booking_cancelled_unilaterally_provider_support_email",
                extra={"booking_id": booking.id},
            )
            return
    data = get_booking_cancelled_unilaterally_provider_support_email_data(external_booking_information)
    mails.send(recipients=[recipient], data=data)
