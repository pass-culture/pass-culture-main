from pcapi.core import mails
from pcapi.core.bookings import utils as bookings_utils
from pcapi.core.bookings.models import Booking
from pcapi.core.mails import models
from pcapi.core.mails.transactional.bookings import common as bookings_common
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.models.feature import FeatureToggle
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.date import utc_datetime_to_department_timezone
from pcapi.utils.urls import booking_app_link


def send_individual_booking_event_reminder_email_to_beneficiary(booking: Booking) -> None:
    data = get_booking_event_reminder_to_beneficiary_email_data(booking)

    if data is None:
        return

    mails.send(recipients=[booking.user.email], data=data)


def get_booking_event_reminder_to_beneficiary_email_data(
    booking: Booking,
) -> models.TransactionalEmailData | None:
    if booking.stock.beginningDatetime is None:
        return None

    department_code = (
        booking.stock.offer.venue.departementCode if not booking.stock.offer.isDigital else booking.user.departementCode
    )

    event_beginning_date_in_tz = utc_datetime_to_department_timezone(booking.stock.beginningDatetime, department_code)
    formatted_event_beginning_date = get_date_formatted_for_email(event_beginning_date_in_tz)
    formatted_event_beginning_time = get_time_formatted_for_email(event_beginning_date_in_tz)

    emailTemplate = (
        TransactionalEmail.BOOKING_EVENT_REMINDER_TO_BENEFICIARY_WITH_METADATA
        if FeatureToggle.WIP_ENABLE_REMINDER_MARKETING_MAIL_METADATA_DISPLAY.is_active()
        else TransactionalEmail.BOOKING_EVENT_REMINDER_TO_BENEFICIARY
    )

    return models.TransactionalEmailData(
        template=emailTemplate.value,
        params={
            "BOOKING_LINK": booking_app_link(booking),
            "EVENT_DATETIME_ISO": event_beginning_date_in_tz.isoformat(),
            "EVENT_DATE": formatted_event_beginning_date,
            "EVENT_HOUR": formatted_event_beginning_time,
            "IS_DUO_EVENT": booking.quantity == 2,
            "OFFER_NAME": booking.stock.offer.name,
            "OFFER_TAGS": ",".join([criterion.name for criterion in booking.stock.offer.criteria]),
            "OFFER_TOKEN": bookings_common.get_booking_token(booking),
            "OFFER_WITHDRAWAL_DELAY": bookings_common.get_offer_withdrawal_delay(booking),
            "OFFER_WITHDRAWAL_DETAILS": bookings_common.get_offer_withdrawal_details(booking),
            "OFFER_WITHDRAWAL_TYPE": bookings_common.get_offer_withdrawal_type(booking),
            "QR_CODE": bookings_utils.get_qr_code_data(booking.token),
            "SUBCATEGORY": booking.stock.offer.subcategoryId,
            "USER_FIRST_NAME": booking.user.firstName,
            "VENUE_ADDRESS": bookings_common.get_venue_street(booking),
            "VENUE_CITY": booking.stock.offer.venue.city,
            "VENUE_NAME": (
                booking.stock.offer.venue.publicName
                if booking.stock.offer.venue.publicName
                else booking.stock.offer.venue.name
            ),
            "VENUE_POSTAL_CODE": booking.stock.offer.venue.postalCode,
        },
    )
