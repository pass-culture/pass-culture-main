from pcapi.core import mails
from pcapi.core.bookings import constants as booking_constants
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.categories import subcategories
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.utils.mailing import format_booking_date_for_email
from pcapi.utils.mailing import format_booking_hours_for_email


def get_new_booking_to_pro_email_data(
    individual_booking: IndividualBooking, first_venue_booking: bool = False
) -> models.TransactionalEmailData:
    booking = individual_booking.booking
    offer = booking.stock.offer
    venue = offer.venue

    if offer.isEvent:
        event_date = format_booking_date_for_email(booking)
        event_hour = format_booking_hours_for_email(booking)
    else:
        event_date = ""
        event_hour = ""

    if "isbn" in offer.subcategory.conditional_fields:
        isbn = offer.extraData.get("isbn", "") if offer.extraData is not None else ""
        offer_subcategory = "book"
    else:
        isbn = ""
        offer_subcategory = offer.subcategoryId

    if booking.stock.canHaveActivationCodes and booking.activationCode:
        can_expire = False
        is_booking_autovalidated = True
    else:
        can_expire = offer.subcategory.can_expire
        is_booking_autovalidated = False

    if first_venue_booking:
        template = TransactionalEmail.FIRST_VENUE_BOOKING_TO_PRO.value
    else:
        template = TransactionalEmail.NEW_BOOKING_TO_PRO.value

    data = models.TransactionalEmailData(
        reply_to=models.EmailInfo(
            email=individual_booking.user.email,
            name=f"{individual_booking.user.firstName} {individual_booking.user.lastName}",
        ),
        template=template,
        params={
            "CAN_EXPIRE": can_expire,
            "COUNTERMARK": booking.token,
            "DEPARTMENT_CODE": venue.departementCode if not offer.isDigital else "numérique",
            "EVENT_DATE": event_date,
            "EVENT_HOUR": event_hour,
            "IS_BOOKING_AUTOVALIDATED": is_booking_autovalidated,
            "IS_EVENT": offer.isEvent,
            "IS_THING": offer.isThing,
            "IS_DIGITAL": offer.isDigital,
            "IS_EXTERNAL": booking.isExternal,
            "ISBN": isbn,
            "OFFER_NAME": offer.name,
            "OFFER_SUBCATEGORY": offer_subcategory,
            "PRICE": "Gratuit" if booking.stock.price == 0 else f"{booking.stock.price} €",
            "QUANTITY": booking.quantity,
            "USER_EMAIL": individual_booking.user.email,
            "USER_FIRSTNAME": individual_booking.user.firstName,
            "USER_LASTNAME": individual_booking.user.lastName,
            "USER_PHONENUMBER": individual_booking.user.phoneNumber or "",
            "VENUE_NAME": venue.publicName if venue.publicName else venue.name,
            "MUST_USE_TOKEN_FOR_PAYMENT": not (
                individual_booking.booking.stock.price == 0
                or individual_booking.booking.activationCode
                or is_booking_autovalidated
            ),
            "WITHDRAWAL_PERIOD": booking_constants.BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY.days
            if offer.subcategoryId == subcategories.LIVRE_PAPIER.id
            else booking_constants.BOOKINGS_AUTO_EXPIRY_DELAY.days,
        },
    )

    return data


def send_user_new_booking_to_pro_email(individual_booking: IndividualBooking, first_venue_booking: bool) -> bool:
    if first_venue_booking:
        offerer_booking_email = individual_booking.booking.stock.offer.venue.bookingEmail
    else:
        offerer_booking_email = individual_booking.booking.stock.offer.bookingEmail

    if not offerer_booking_email:
        return True
    data = get_new_booking_to_pro_email_data(individual_booking, first_venue_booking)
    return mails.send(recipients=[offerer_booking_email], data=data)
