from typing import Dict
from babel.dates import format_date

from models import Booking
from repository.feature_queries import feature_send_mail_to_users_enabled
from utils.mailing import SUPPORT_EMAIL_ADDRESS, DEV_EMAIL_ADDRESS, format_booking_hours_for_email, get_event_datetime


def retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation(booking: Booking) -> Dict:
    stock = booking.stock
    offer = stock.offer
    event_date = ''
    event_hour = ''
    email_to = booking.user.email if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS
    is_event = int(offer.isEvent)
    if is_event:
        event_date = format_date(get_event_datetime(stock), format='full', locale='fr')
        event_hour = format_booking_hours_for_email(booking)
    is_free_offer = 1 if stock.price == 0 else 0
    is_thing = int(offer.isThing)
    is_online = int(offer.isDigital)
    if is_online:
        is_event = 0
        is_thing = 0
    offerer_name = offer.venue.managingOfferer.name
    offer_name = offer.name
    offer_price = str(stock.price * booking.quantity)
    user_first_name = booking.user.firstName
    venue_name = offer.venue.publicName if offer.venue.publicName else offer.venue.name

    return {
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'MJ-TemplateID': 1116690,
        'MJ-TemplateLanguage': True,
        'To': email_to,
        'Vars': {
            'event_date': event_date,
            'event_hour': event_hour,
            'is_event': is_event,
            'is_free_offer': is_free_offer,
            'is_online': is_online,
            'is_thing': is_thing,
            'offer_name': offer_name,
            'offer_price': offer_price,
            'offerer_name': offerer_name,
            'user_first_name': user_first_name,
            'venue_name': venue_name
        }
    }
