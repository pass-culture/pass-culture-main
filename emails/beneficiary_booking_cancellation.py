import os
from typing import Dict

from babel.dates import format_date

from models import Booking
from utils.mailing import format_environment_for_email

SUPPORT_EMAIL_ADDRESS = os.environ.get('SUPPORT_EMAIL_ADDRESS')


def make_beneficiary_booking_cancellation_email_data(booking: Booking) -> Dict:
    stock = booking.stock
    beneficiary = booking.user
    offer = stock.resolvedOffer
    beneficiary_email = beneficiary.email
    environment = format_environment_for_email()
    event_date = ''
    event_hour = ''
    first_name = beneficiary.firstName
    is_event = int(offer.isEvent)
    offer_id = offer.id
    offer_name = offer.name
    price = str(stock.price)
    is_free_offer = '1' if price == '0' else '0'
    mediation_id = booking.mediationId if booking.mediationId is not None else ''

    if is_event:
        beginning_date_time = stock.beginningDatetime
        event_date = format_date(beginning_date_time, format='dd MMMM', locale='fr')
        event_hour = beginning_date_time.strftime('%Hh%M')

    return {
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'Mj-TemplateID': 1091464,
        'Mj-TemplateLanguage': True,
        'To': beneficiary_email,
        'Vars': {
            'env': environment,
            'event_date': event_date,
            'event_hour': event_hour,
            'is_free_offer': is_free_offer,
            'is_event': is_event,
            'mediation_id': mediation_id,
            'offer_id': offer_id,
            'offer_name': offer_name,
            'offer_price': price,
            'user_first_name': first_name,
        },
    }
