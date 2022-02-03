from typing import Union

from pcapi.core import mails
from pcapi.core.bookings.constants import BOOKINGS_AUTO_EXPIRY_DELAY
from pcapi.core.bookings.constants import BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.categories import subcategories
from pcapi.core.mails.transactional.sendinblue_template_ids import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.models.feature import FeatureToggle
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.date import utc_datetime_to_department_timezone
from pcapi.utils.human_ids import humanize
from pcapi.utils.urls import booking_app_link


def send_individual_booking_confirmation_email_to_beneficiary(individual_booking: IndividualBooking) -> bool:
    data = get_booking_confirmation_to_beneficiary_email_data(individual_booking)
    return mails.send(recipients=[individual_booking.user.email], data=data)


def get_booking_confirmation_to_beneficiary_email_data(
    individual_booking: IndividualBooking,
) -> Union[dict, SendinblueTransactionalEmailData]:
    stock = individual_booking.booking.stock
    offer = stock.offer
    venue = offer.venue
    beneficiary = individual_booking.user

    if offer.isDigital and individual_booking.booking.activationCode:
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

    department_code = venue.departementCode if not offer.isDigital else beneficiary.departementCode
    booking_date_in_tz = utc_datetime_to_department_timezone(individual_booking.booking.dateCreated, department_code)
    formatted_booking_date = get_date_formatted_for_email(booking_date_in_tz)
    formatted_booking_time = get_time_formatted_for_email(booking_date_in_tz)

    stock_price = f"{individual_booking.booking.total_amount} €" if stock.price > 0 else "Gratuit"

    mediation_id = humanize(offer.activeMediation.id) if offer.activeMediation else "vide"
    if offer.isEvent:
        event_beginning_date_in_tz = utc_datetime_to_department_timezone(stock.beginningDatetime, department_code)
        formatted_event_beginning_time = get_time_formatted_for_email(event_beginning_date_in_tz)
        formatted_event_beginning_date = get_date_formatted_for_email(event_beginning_date_in_tz)
    else:
        formatted_event_beginning_time = None
        formatted_event_beginning_date = None

    is_digital_booking_with_activation_code_and_no_expiration_date = int(
        bool(
            offer.isDigital
            and individual_booking.booking.activationCode
            and not individual_booking.booking.activationCode.expirationDate
        )
    )

    code_expiration_date = (
        get_date_formatted_for_email(individual_booking.booking.activationCode.expirationDate)
        if offer.isDigital
        and individual_booking.booking.activationCode
        and individual_booking.booking.activationCode.expirationDate
        else None
    )

    booking_token = (
        individual_booking.booking.activationCode.code
        if individual_booking.booking.activationCode
        else individual_booking.booking.token
    )

    if not FeatureToggle.ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS.is_active():
        return {
            "MJ-TemplateID": 3094927,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "user_first_name": beneficiary.firstName,
                "booking_date": formatted_booking_date,
                "booking_hour": formatted_booking_time,
                "offer_name": offer.name,
                "offerer_name": venue.managingOfferer.name,
                "event_date": formatted_event_beginning_date if formatted_event_beginning_date else "",
                "event_hour": formatted_event_beginning_time if formatted_event_beginning_time else "",
                "offer_price": stock_price,
                "offer_token": booking_token,
                "is_digital_booking_with_activation_code_and_no_expiration_date": is_digital_booking_with_activation_code_and_no_expiration_date,
                "code_expiration_date": code_expiration_date if code_expiration_date else "",
                "venue_name": venue.publicName if venue.publicName else venue.name,
                "venue_address": venue.address,
                "venue_postal_code": venue.postalCode,
                "venue_city": venue.city,
                "all_but_not_virtual_thing": int(offer.isEvent or (not offer.isEvent and not offer.isDigital)),
                "all_things_not_virtual_thing": int(not offer.isEvent and not offer.isDigital),
                "is_event": int(offer.isEvent),
                "is_single_event": int(offer.isEvent and individual_booking.booking.quantity == 1),
                "is_duo_event": int(individual_booking.booking.quantity == 2),
                "offer_id": humanize(offer.id),
                "mediation_id": mediation_id,
                "can_expire": int(can_expire),
                "expiration_delay": expiration_delay or "",
                "has_offer_url": int(offer.isDigital),
                "digital_offer_url": individual_booking.booking.completedUrl or "",
                "offer_withdrawal_details": offer.withdrawalDetails or "",
                "booking_link": booking_app_link(individual_booking.booking),
            },
        }

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.BOOKING_CONFIRMATION_BY_BENEFICIARY.value,
        params={
            "USER_FIRST_NAME": beneficiary.firstName,
            "BOOKING_DATE": formatted_booking_date,
            "BOOKING_HOUR": formatted_booking_time,
            "OFFER_NAME": offer.name,
            "OFFERER_NAME": venue.managingOfferer.name,
            "EVENT_DATE": formatted_event_beginning_date,
            "EVENT_HOUR": formatted_event_beginning_time,
            "OFFER_PRICE": stock_price,
            "OFFER_TOKEN": booking_token,
            "IS_DIGITAL_BOOKING_WITH_ACTIVATION_CODE_AND_NO_EXPIRATION_DATE": bool(
                is_digital_booking_with_activation_code_and_no_expiration_date
            ),
            "CODE_EXPIRATION_DATE": code_expiration_date,
            "VENUE_NAME": venue.publicName if venue.publicName else venue.name,
            "VENUE_ADDRESS": venue.address,
            "VENUE_POSTAL_CODE": venue.postalCode,
            "VENUE_CITY": venue.city,
            "ALL_BUT_NOT_VIRTUAL_THING": offer.isEvent or (not offer.isEvent and not offer.isDigital),
            "ALL_THINGS_NOT_VIRTUAL_THING": not offer.isEvent and not offer.isDigital,
            "IS_EVENT": offer.isEvent,
            "IS_SINGLE_EVENT": offer.isEvent and individual_booking.booking.quantity == 1,
            "IS_DUO_EVENT": individual_booking.booking.quantity == 2,
            "OFFER_ID": humanize(offer.id),
            "MEDIATION_ID": mediation_id,
            "CAN_EXPIRE": can_expire,
            "EXPIRATION_DELAY": expiration_delay,
            "HAS_OFFER_URL": offer.isDigital,
            "DIGITAL_OFFER_URL": individual_booking.booking.completedUrl or None,
            "OFFER_WITHDRAWAL_DETAILS": offer.withdrawalDetails or None,
            "BOOKING_LINK": booking_app_link(individual_booking.booking),
        },
    )
