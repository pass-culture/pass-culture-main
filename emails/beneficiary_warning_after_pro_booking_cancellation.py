from typing import Dict

from models import Booking
from repository.feature_queries import feature_send_mail_to_users_enabled
from utils.date import ENGLISH_TO_FRENCH_MONTH
from utils.mailing import SUPPORT_EMAIL_ADDRESS, DEV_EMAIL_ADDRESS, format_booking_hours_for_email, get_event_datetime


def retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation(booking: Booking) -> Dict:
    is_event = booking.stock.beginningDatetime is not None
    if is_event:
        date_event = _format_booking_date(booking)
        heure_event = format_booking_hours_for_email(booking)
        event = '1'
    else:
        date_event = ''
        heure_event = ''
        event = '0'

    return {
        'FromEmail': SUPPORT_EMAIL_ADDRESS if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS,
        'FromName': 'pass Culture',
        'MJ-TemplateID': 1116690,
        'MJ-TemplateLanguage': True,
        'To': booking.user.email if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS,
        'Vars': {
            'prix_offre': str(booking.stock.price),
            'offer_price': '1' if booking.stock.price > 0 else '0',
            'heure_event': heure_event,
            'date_event': date_event,
            'nom_lieu': booking.stock.offer.venue.publicName if booking.stock.offer.venue.publicName else booking.stock.offer.venue.name,
            'event': event,
            'prenom_user': booking.user.firstName,
            'nom_offre': booking.stock.offer.name
        }
    }


def _format_booking_date(booking: Booking) -> str:
    if booking.stock.resolvedOffer.isEvent:

        date_in_tz = get_event_datetime(booking.stock)
        english_month = date_in_tz.strftime('%B')
        offer_date = date_in_tz.strftime('%d %B %Y').replace(english_month, ENGLISH_TO_FRENCH_MONTH[english_month])
        return offer_date
    return ''