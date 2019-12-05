from typing import Dict, List

from models import Booking
from models.offer_type import ProductType
from utils.config import ENV, IS_PROD
from utils.date import utc_datetime_to_dept_timezone, get_date_formatted_for_email, get_time_formatted_for_email
from utils.mailing import SUPPORT_EMAIL_ADDRESS, _create_email_recipients


def retrieve_data_for_user_booking_confirmation_email(booking: Booking, recipients: List[str]) -> Dict:
    stock = booking.stock
    offer = stock.offer
    venue = offer.venue
    user = booking.user

    is_digital_offer = offer.isDigital
    is_physical_offer = ProductType.is_thing(name=offer.type) and not is_digital_offer
    is_event = ProductType.is_event(name=offer.type)

    booking_date_in_tz = utc_datetime_to_dept_timezone(booking.dateCreated, venue.departementCode)

    if is_event:
        event_beginning_date_in_tz = utc_datetime_to_dept_timezone(stock.beginningDatetime,
                                                                   venue.departementCode)
        formatted_event_beginning_time = get_time_formatted_for_email(event_beginning_date_in_tz)
        formatted_event_beginning_date = get_date_formatted_for_email(event_beginning_date_in_tz)
    else:
        formatted_event_beginning_time = ''
        formatted_event_beginning_date = ''

    return {
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'MJ-TemplateID': 1089755,
        'MJ-TemplateLanguage': True,
        'To': _create_email_recipients(recipients),
        'Vars':
            {
                'user_first_name': user.firstName,
                'booking_date': (get_date_formatted_for_email(booking_date_in_tz)),
                'booking_hour': (get_time_formatted_for_email(booking_date_in_tz)),
                'offer_name': offer.name,
                'offerer_name': venue.managingOfferer.name,
                'event_date': formatted_event_beginning_date,
                'event_hour': formatted_event_beginning_time,
                'offer_price': stock.price,
                'offer_token': booking.token,
                'venue_name': venue.name,
                'venue_address': venue.address,
                'all_but_not_virtual_thing': 1 if is_event or is_physical_offer else 0,
                'all_things_not_virtual_thing': 1 if is_physical_offer else 0,
                'is_event': 1 if is_event else 0,
                'offer_id': offer.id,
                'mediation_id': offer.activeMediation.id,
                'env': (f'-{ENV}' if not IS_PROD else '')
            }
    }
