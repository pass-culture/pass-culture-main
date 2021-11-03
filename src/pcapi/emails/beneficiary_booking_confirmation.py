from pcapi.core.bookings.constants import BOOKINGS_AUTO_EXPIRY_DELAY
from pcapi.core.bookings.constants import BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY
from pcapi.core.bookings.models import Booking
from pcapi.core.categories import subcategories
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.date import utc_datetime_to_department_timezone
from pcapi.utils.human_ids import humanize


def retrieve_data_for_beneficiary_booking_confirmation_email(booking: Booking) -> dict:
    stock = booking.stock
    offer = stock.offer
    venue = offer.venue
    beneficiary = booking.user

    is_digital_offer = offer.isDigital
    is_physical_offer = not offer.isEvent and not is_digital_offer
    is_event = offer.isEvent

    if is_digital_offer and booking.activationCode:
        can_expire = 0
    else:
        can_expire = int(offer.subcategory.can_expire)

    expiration_delay: str = ""
    if can_expire:
        if offer.subcategoryId == subcategories.LIVRE_PAPIER.id:
            expiration_delay = BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY.days
        else:
            expiration_delay = BOOKINGS_AUTO_EXPIRY_DELAY.days

    department_code = venue.departementCode if not is_digital_offer else beneficiary.departementCode
    booking_date_in_tz = utc_datetime_to_department_timezone(booking.dateCreated, department_code)

    beneficiary_first_name = beneficiary.firstName
    formatted_booking_date = get_date_formatted_for_email(booking_date_in_tz)
    formatted_booking_time = get_time_formatted_for_email(booking_date_in_tz)

    offer_name = offer.name
    offerer_name = venue.managingOfferer.name
    formatted_event_beginning_time = ""
    formatted_event_beginning_date = ""
    stock_price = f"{booking.total_amount} €" if stock.price > 0 else "Gratuit"
    venue_name = venue.publicName if venue.publicName else venue.name
    venue_address = venue.address or ""
    venue_postal_code = venue.postalCode or ""
    venue_city = venue.city or ""
    is_event_or_physical_offer_stringified_boolean = 1 if is_event or is_physical_offer else 0
    is_physical_offer_stringified_boolean = 1 if is_physical_offer else 0
    is_event_stringified_boolean = 1 if is_event else 0
    is_single_event_stringified_boolean = 1 if is_event and booking.quantity == 1 else 0
    is_duo_event_stringified_boolean = 1 if is_event and booking.quantity == 2 else 0
    offer_id = humanize(offer.id)
    mediation_id = humanize(offer.activeMediation.id) if offer.activeMediation else "vide"
    if is_event:
        event_beginning_date_in_tz = utc_datetime_to_department_timezone(stock.beginningDatetime, department_code)
        formatted_event_beginning_time = get_time_formatted_for_email(event_beginning_date_in_tz)
        formatted_event_beginning_date = get_date_formatted_for_email(event_beginning_date_in_tz)

    is_digital_booking_with_activation_code_and_no_expiration_date = (
        1 if is_digital_offer and booking.activationCode and not booking.activationCode.expirationDate else 0
    )

    code_expiration_date = (
        get_date_formatted_for_email(booking.activationCode.expirationDate)
        if is_digital_offer and booking.activationCode and booking.activationCode.expirationDate
        else ""
    )

    booking_token = booking.activationCode.code if booking.activationCode else booking.token
    has_offer_url = 1 if is_digital_offer else 0
    return {
        "MJ-TemplateID": 3094927,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "user_first_name": beneficiary_first_name,
            "booking_date": formatted_booking_date,
            "booking_hour": formatted_booking_time,
            "offer_name": offer_name,
            "offerer_name": offerer_name,
            "event_date": formatted_event_beginning_date,
            "event_hour": formatted_event_beginning_time,
            "offer_price": stock_price,
            "offer_token": booking_token,
            "is_digital_booking_with_activation_code_and_no_expiration_date": is_digital_booking_with_activation_code_and_no_expiration_date,
            "code_expiration_date": code_expiration_date,
            "venue_name": venue_name,
            "venue_address": venue_address,
            "venue_postal_code": venue_postal_code,
            "venue_city": venue_city,
            "all_but_not_virtual_thing": is_event_or_physical_offer_stringified_boolean,
            "all_things_not_virtual_thing": is_physical_offer_stringified_boolean,
            "is_event": is_event_stringified_boolean,
            "is_single_event": is_single_event_stringified_boolean,
            "is_duo_event": is_duo_event_stringified_boolean,
            "offer_id": offer_id,
            "mediation_id": mediation_id,
            "can_expire": can_expire,
            "expiration_delay": expiration_delay,
            "has_offer_url": has_offer_url,
            "digital_offer_url": booking.completedUrl or "",
            "offer_withdrawal_details": offer.withdrawalDetails or "",
        },
    }
