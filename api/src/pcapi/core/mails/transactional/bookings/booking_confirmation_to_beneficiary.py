from pcapi.core import mails
from pcapi.core.bookings.constants import BOOKINGS_AUTO_EXPIRY_DELAY
from pcapi.core.bookings.constants import BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY
from pcapi.core.bookings.models import Booking
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.mails import models
from pcapi.core.mails.transactional.bookings import common as bookings_common
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.date import utc_datetime_to_department_timezone
from pcapi.utils.urls import booking_app_link


def send_individual_booking_confirmation_email_to_beneficiary(booking: Booking) -> None:
    data = get_booking_confirmation_to_beneficiary_email_data(booking)
    mails.send(recipients=[booking.user.email], data=data)


def get_booking_confirmation_to_beneficiary_email_data(
    booking: Booking,
) -> models.TransactionalEmailData:
    stock = booking.stock
    offer = stock.offer
    venue = offer.venue
    beneficiary = booking.user

    if offer.isDigital and booking.activationCode:
        can_expire = False
    else:
        can_expire = offer.subcategory.can_expire

    if can_expire:
        if offer.subcategoryId == subcategories.LIVRE_PAPIER.id:
            expiration_delay = BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY.days
        else:
            expiration_delay = BOOKINGS_AUTO_EXPIRY_DELAY.days
    else:
        expiration_delay = None

    department_code = offer.departementCode if not offer.isDigital else beneficiary.departementCode
    booking_date_in_tz = utc_datetime_to_department_timezone(booking.dateCreated, department_code)
    formatted_booking_date = get_date_formatted_for_email(booking_date_in_tz)
    formatted_booking_time = get_time_formatted_for_email(booking_date_in_tz)

    stock_price = f"{booking.total_amount} €" if stock.price > 0 else "Gratuit"

    if offer.isEvent:
        if stock.beginningDatetime is None:
            raise ValueError("Can't convert None to local timezone")
        event_beginning_date_in_tz = utc_datetime_to_department_timezone(stock.beginningDatetime, department_code)
        formatted_event_beginning_time = get_time_formatted_for_email(event_beginning_date_in_tz)
        formatted_event_beginning_date = get_date_formatted_for_email(event_beginning_date_in_tz)
    else:
        formatted_event_beginning_time = None
        formatted_event_beginning_date = None

    is_digital_booking_with_activation_code_and_no_expiration_date = int(
        bool(offer.isDigital and booking.activationCode and not booking.activationCode.expirationDate)
    )

    code_expiration_date = (
        get_date_formatted_for_email(booking.activationCode.expirationDate)
        if offer.isDigital and booking.activationCode and booking.activationCode.expirationDate
        else None
    )

    return models.TransactionalEmailData(
        template=TransactionalEmail.BOOKING_CONFIRMATION_BY_BENEFICIARY.value,
        params={
            "USER_FIRST_NAME": beneficiary.firstName,
            "BOOKING_DATE": formatted_booking_date,
            "BOOKING_HOUR": formatted_booking_time,
            "OFFER_NAME": offer.name,
            "OFFERER_NAME": bookings_common.get_offerer_name(booking),
            "EVENT_DATE": formatted_event_beginning_date,
            "EVENT_HOUR": formatted_event_beginning_time,
            "OFFER_PRICE": stock_price,
            "OFFER_PRICE_CATEGORY": booking.priceCategoryLabel,
            "OFFER_TAGS": ",".join([criterion.name for criterion in offer.criteria]),
            "OFFER_TOKEN": bookings_common.get_booking_token(booking),
            "OFFER_CATEGORY": offer.category.id,
            "OFFER_SUBCATEGORY": offer.subcategoryId,
            "IS_DIGITAL_BOOKING_WITH_ACTIVATION_CODE_AND_NO_EXPIRATION_DATE": bool(
                is_digital_booking_with_activation_code_and_no_expiration_date
            ),
            "CODE_EXPIRATION_DATE": code_expiration_date,
            "VENUE_NAME": venue.publicName if venue.publicName else venue.name,
            "VENUE_ADDRESS": bookings_common.get_venue_street(booking),
            "VENUE_POSTAL_CODE": offer.postalCode,
            "VENUE_CITY": offer.city,
            "ALL_BUT_NOT_VIRTUAL_THING": offer.isEvent or (not offer.isEvent and not offer.isDigital),
            "ALL_THINGS_NOT_VIRTUAL_THING": not offer.isEvent and not offer.isDigital,
            "IS_EVENT": offer.isEvent,
            "IS_EXTERNAL": booking.isExternal,
            "IS_SINGLE_EVENT": offer.isEvent and booking.quantity == 1,
            "IS_DUO_EVENT": booking.quantity == 2,
            "CAN_EXPIRE": can_expire,
            "EXPIRATION_DELAY": expiration_delay,
            "HAS_OFFER_URL": offer.isDigital,
            "DIGITAL_OFFER_URL": booking.completedUrl or None,
            "OFFER_WITHDRAWAL_DETAILS": offer.withdrawalDetails or None,
            "BOOKING_LINK": booking_app_link(booking),
            "OFFER_WITHDRAWAL_DELAY": bookings_common.get_offer_withdrawal_delay(booking),
            "OFFER_WITHDRAWAL_TYPE": bookings_common.get_offer_withdrawal_type(booking),
            "FEATURES": ", ".join(stock.features),
        },
    )
