from sqlalchemy.orm import joinedload

from pcapi.core import mails
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.models import Stock
from pcapi.utils.mailing import build_pc_pro_offer_link
from pcapi.utils.mailing import extract_users_information_from_bookings
from pcapi.utils.mailing import format_booking_date_for_email
from pcapi.utils.mailing import format_booking_hours_for_email


def get_booking_cancellation_by_beneficiary_to_pro_email_data(booking: Booking) -> dict:
    bookings = (
        Booking.query.filter(Booking.status != BookingStatus.CANCELLED, Booking.stock == booking.stock)
        .options(joinedload(Booking.individualBooking).joinedload(IndividualBooking.user))
        .all()
    )

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO.value,
        params={
            "DEPARTEMENT": booking.stock.offer.venue.departementCode or "numérique",
            "NOM_OFFRE": booking.stock.offer.name,
            "LIEN_OFFRE_PCPRO": build_pc_pro_offer_link(booking.stock.offer),
            "NOM_LIEU": booking.stock.offer.venue.name,
            "PRIX": booking.stock.price if booking.stock.price > 0 else "Gratuit",
            "IS_EVENT": booking.stock.offer.isEvent,
            "DATE": format_booking_date_for_email(booking),
            "HEURE": format_booking_hours_for_email(booking),
            "QUANTITE": booking.quantity,
            "USER_NAME": f"{booking.firstName} {booking.lastName}",
            "USER_EMAIL": booking.email,
            "IS_ACTIVE": _is_offer_active_for_recap(booking.stock),
            "NOMBRE_RESA": len(bookings),
            "USERS": extract_users_information_from_bookings(bookings),
        },
    )


def _is_offer_active_for_recap(stock: Stock) -> bool:
    return stock.isBookable and (stock.quantity is None or stock.remainingQuantity > 0)


def send_booking_cancellation_by_beneficiary_to_pro_email(booking: Booking) -> bool:
    offerer_booking_email = booking.stock.offer.bookingEmail
    if not offerer_booking_email:
        return True
    data = get_booking_cancellation_by_beneficiary_to_pro_email_data(booking)
    return mails.send(recipients=[offerer_booking_email], data=data)
