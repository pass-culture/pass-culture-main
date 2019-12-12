from typing import Dict

from models import Booking
from models.offer_type import ProductType
from repository.feature_queries import feature_send_mail_to_users_enabled
from utils.date import utc_datetime_to_dept_timezone, get_date_formatted_for_email, get_time_formatted_for_email
from utils.human_ids import humanize
from utils.mailing import SUPPORT_EMAIL_ADDRESS, format_environment_for_email, \
    DEV_EMAIL_ADDRESS


def retrieve_data_for_beneficiary_booking_confirmation_email(booking: Booking) -> Dict:
    stock = booking.stock
    offer = stock.offer
    venue = offer.venue
    beneficiary = booking.user

    is_digital_offer = offer.isDigital
    is_physical_offer = ProductType.is_thing(name=offer.type) and not is_digital_offer
    is_event = ProductType.is_event(name=offer.type)

    department_code = venue.departementCode if not is_digital_offer else beneficiary.departementCode
    booking_date_in_tz = utc_datetime_to_dept_timezone(booking.dateCreated, department_code)

    beneficiary_email = beneficiary.email if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS
    beneficiary_first_name = beneficiary.firstName
    formatted_booking_date = get_date_formatted_for_email(booking_date_in_tz)
    formatted_booking_time = get_time_formatted_for_email(booking_date_in_tz)

    offer_name = offer.name
    offerer_name = venue.managingOfferer.name
    formatted_event_beginning_time = ''
    formatted_event_beginning_date = ''
    stock_price = str(stock.price * booking.quantity) if stock.price > 0 else 'Gratuit'
    booking_token = booking.token
    venue_name = venue.name
    venue_address = venue.address
    is_event_or_physical_offer_stringified_boolean = '1' if is_event or is_physical_offer else '0'
    is_physical_offer_stringified_boolean = '1' if is_physical_offer else '0'
    is_event_stringified_boolean = '1' if is_event else '0'
    is_single_event_stringified_boolean = '1' if is_event and booking.quantity == 1 else '0'
    is_duo_event_stringified_boolean = '1' if is_event and booking.quantity == 2 else '0'
    offer_id = humanize(offer.id)
    mediation_id = humanize(offer.activeMediation.id) if offer.activeMediation else 'vide'
    environment = format_environment_for_email()
    if is_event:
        event_beginning_date_in_tz = utc_datetime_to_dept_timezone(stock.beginningDatetime,
                                                                   department_code)
        formatted_event_beginning_time = get_time_formatted_for_email(event_beginning_date_in_tz)
        formatted_event_beginning_date = get_date_formatted_for_email(event_beginning_date_in_tz)

    return {
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'MJ-TemplateID': 1089755,
        'MJ-TemplateLanguage': True,
        'To': beneficiary_email,
        'Vars':
            {
                'user_first_name': beneficiary_first_name,
                'booking_date': formatted_booking_date,
                'booking_hour': formatted_booking_time,
                'offer_name': offer_name,
                'offerer_name': offerer_name,
                'event_date': formatted_event_beginning_date,
                'event_hour': formatted_event_beginning_time,
                'offer_price': stock_price,
                'offer_token': booking_token,
                'venue_name': venue_name,
                'venue_address': venue_address,
                'all_but_not_virtual_thing': is_event_or_physical_offer_stringified_boolean,
                'all_things_not_virtual_thing': is_physical_offer_stringified_boolean,
                'is_event': is_event_stringified_boolean,
                'is_single_event': is_single_event_stringified_boolean,
                'is_duo_event': is_duo_event_stringified_boolean,
                'offer_id': offer_id,
                'mediation_id': mediation_id,
                'env': environment
            }
    }
