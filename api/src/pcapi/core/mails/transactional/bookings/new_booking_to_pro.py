from pcapi.core import mails
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.mails.models.sendinblue_models import EmailInfo
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.utils.mailing import format_booking_date_for_email
from pcapi.utils.mailing import format_booking_hours_for_email


def get_new_booking_to_pro_email_data(
    individual_booking: IndividualBooking,
) -> SendinblueTransactionalEmailData:
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

    data = SendinblueTransactionalEmailData(
        reply_to=EmailInfo(
            email=individual_booking.user.email,
            name=f"{individual_booking.user.firstName} {individual_booking.user.lastName}",
        ),
        template=TransactionalEmail.NEW_BOOKING_TO_PRO.value,
        params={
            "OFFER_NAME": offer.name,
            "VENUE_NAME": venue.publicName if venue.publicName else venue.name,
            "IS_EVENT": offer.isEvent,
            "ISBN": isbn,
            "OFFER_SUBCATEGORY": offer_subcategory,
            "EVENT_DATE": event_date,
            "EVENT_HOUR": event_hour,
            "QUANTITY": booking.quantity,
            "COUNTERMARK": booking.token,
            "PRICE": "Gratuit" if booking.stock.price == 0 else f"{booking.stock.price} €",
            "USER_FIRSTNAME": individual_booking.user.firstName,
            "USER_LASTNAME": individual_booking.user.lastName,
            "USER_PHONENUMBER": individual_booking.user.phoneNumber or "",
            "USER_EMAIL": individual_booking.user.email,
            "CAN_EXPIRE": can_expire,
            "IS_BOOKING_AUTOVALIDATED": is_booking_autovalidated,
            "MUST_USE_TOKEN_FOR_PAYMENT": not (
                individual_booking.booking.stock.price == 0
                or individual_booking.booking.activationCode
                or is_booking_autovalidated
            ),
        },
    )

    return data


def send_user_new_booking_to_pro_email(individual_booking: IndividualBooking) -> bool:
    offerer_booking_email = individual_booking.booking.stock.offer.bookingEmail
    if not offerer_booking_email:
        return True
    data = get_new_booking_to_pro_email_data(individual_booking)
    return mails.send(recipients=[offerer_booking_email], data=data)
