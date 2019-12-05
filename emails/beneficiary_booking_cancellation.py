import os
from typing import Dict

from flask import render_template

from models import Booking, Stock, User
from repository.feature_queries import feature_send_mail_to_users_enabled
from utils.date import format_datetime
from utils.mailing import _get_event_datetime

DEV_EMAIL_ADDRESS = os.environ.get('DEV_EMAIL_ADDRESS')
SUPPORT_EMAIL_ADDRESS = os.environ.get('SUPPORT_EMAIL_ADDRESS')

def make_user_booking_cancellation_recap_email(booking: Booking) -> Dict:
    stock = booking.stock
    user = booking.user
    email_html, email_subject = _generate_user_driven_cancellation_email_for_user(user, stock)

    return {
        'FromName': 'pass Culture',
        'FromEmail': SUPPORT_EMAIL_ADDRESS if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS,
        'Subject': email_subject,
        'Html-part': email_html,
    }

def _generate_user_driven_cancellation_email_for_user(user: User, stock: Stock) -> (str, str):
    venue = stock.resolvedOffer.venue
    if stock.beginningDatetime is None:
        email_subject = 'Annulation de votre commande pour {}'.format(
            stock.resolvedOffer.product.name)
        email_html = render_template('mails/user_cancellation_email_thing.html',
                                     user=user,
                                     thing_name=stock.resolvedOffer.product.name,
                                     thing_reference=stock.resolvedOffer.product.idAtProviders,
                                     venue=venue)
    else:
        date_in_tz = _get_event_datetime(stock)
        formatted_date_time = format_datetime(date_in_tz)
        email_html = render_template('mails/user_cancellation_email_event.html',
                                     user=user,
                                     event_occurrence_name=stock.offer.product.name,
                                     venue=venue,
                                     formatted_date_time=formatted_date_time)
        email_subject = 'Annulation de votre réservation pour {} le {}'.format(
            stock.offer.product.name,
            formatted_date_time
        )

    return email_html, email_subject
