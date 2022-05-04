from pcapi.core import mails
import pcapi.core.bookings.api as bookings_api
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.date import utc_datetime_to_department_timezone
from pcapi.utils.urls import booking_app_link


def send_individual_booking_event_reminder_email_to_beneficiary(individual_booking: IndividualBooking) -> bool:
    data = get_booking_event_reminder_to_beneficiary_email_data(individual_booking)
    return mails.send(recipients=[individual_booking.user.email], data=data)


def get_booking_event_reminder_to_beneficiary_email_data(
    individual_booking: IndividualBooking,
) -> SendinblueTransactionalEmailData:

    department_code = (
        individual_booking.booking.stock.offer.venue.departementCode
        if not individual_booking.booking.stock.offer.isDigital
        else individual_booking.user.departementCode
    )

    event_beginning_date_in_tz = utc_datetime_to_department_timezone(
        individual_booking.booking.stock.beginningDatetime, department_code
    )
    formatted_event_beginning_date = get_date_formatted_for_email(event_beginning_date_in_tz)
    formatted_event_beginning_time = get_time_formatted_for_email(event_beginning_date_in_tz)

    booking_token = (
        individual_booking.booking.activationCode.code
        if individual_booking.booking.activationCode
        else individual_booking.booking.token
    )

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.BOOKING_EVENT_REMINDER_TO_BENEFICIARY.value,  # id_prod à zero -> à changer avec l'id du template sur le compte sib de prod
        params={
            "BOOKING_LINK": booking_app_link(individual_booking.booking),
            "EVENT_DATE": formatted_event_beginning_date,
            "EVENT_HOUR": formatted_event_beginning_time,
            "IS_DUO_EVENT": individual_booking.booking.quantity == 2,
            "OFFER_NAME": individual_booking.booking.stock.offer.name,
            "OFFER_TOKEN": booking_token,
            "OFFER_WITHDRAWAL_DELAY": individual_booking.booking.stock.offer.withdrawalDelay,  # --> changer les secondes en jours
            "OFFER_WITHDRAWAL_DETAILS": individual_booking.booking.stock.offer.withdrawalDetails or None,
            "OFFER_WITHDRAWAL_TYPE": individual_booking.booking.stock.offer.withdrawalType,
            "QR_CODE": bookings_api.get_qr_code_data(individual_booking.booking.token),
            "SUBCATEGORY": individual_booking.booking.stock.offer.subcategoryId,  # subcategoryId utilisé pour filtrer dans sib, n'est pas affiché à l'utiliser
            "USER_FIRST_NAME": individual_booking.user.firstName,
            "VENUE_ADDRESS": individual_booking.booking.stock.offer.venue.address,
            "VENUE_CITY": individual_booking.booking.stock.offer.venue.city,
            "VENUE_NAME": individual_booking.booking.stock.offer.venue.publicName
            if individual_booking.booking.stock.offer.venue.publicName
            else individual_booking.booking.stock.offer.venue.name,
            "VENUE_POSTAL_CODE": individual_booking.booking.stock.offer.venue.postalCode,
        },
    )
