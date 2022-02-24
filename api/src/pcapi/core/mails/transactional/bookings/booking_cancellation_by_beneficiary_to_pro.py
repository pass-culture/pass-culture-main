from pcapi.core import mails
from pcapi.core.bookings.models import Booking
from pcapi.core.mails.models.sendinblue_models import EmailInfo
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.utils.mailing import format_booking_date_for_email
from pcapi.utils.mailing import format_booking_hours_for_email


def get_booking_cancellation_by_beneficiary_to_pro_email_data(booking: Booking) -> dict:

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO.value,
        params={
            "DEPARTEMENT": booking.stock.offer.venue.departementCode or "numérique",
            "NOM_OFFRE": booking.stock.offer.name,
            "NOM_LIEU": booking.stock.offer.venue.name,
            "PRIX": booking.stock.price if booking.stock.price > 0 else "Gratuit",
            "IS_EVENT": booking.stock.offer.isEvent,
            "DATE": format_booking_date_for_email(booking),
            "HEURE": format_booking_hours_for_email(booking),
            "QUANTITE": booking.quantity,
            "USER_NAME": f"{booking.firstName} {booking.lastName}",
            "USER_EMAIL": booking.email,
        },
        reply_to=EmailInfo(email=booking.email, name=f"{booking.firstName} {booking.lastName}"),
    )


def send_booking_cancellation_by_beneficiary_to_pro_email(booking: Booking) -> bool:
    offerer_booking_email = booking.stock.offer.bookingEmail
    if not offerer_booking_email:
        return True
    data = get_booking_cancellation_by_beneficiary_to_pro_email_data(booking)
    return mails.send(recipients=[offerer_booking_email], data=data)
