from typing import Dict

from models import Booking, Stock, Offer
from repository.feature_queries import feature_send_mail_to_users_enabled
from utils.mailing import build_pc_pro_offer_link, SUPPORT_EMAIL_ADDRESS, extract_users_information_from_bookings, \
    DEV_EMAIL_ADDRESS, format_booking_date_for_email, format_booking_hours_for_email, format_environment_for_email


def make_offerer_booking_recap_email_after_user_cancellation_data(booking: Booking, recipients: str) -> Dict:
    user = booking.user
    stock = booking.stock
    bookings = list(filter(lambda ongoing_booking: not ongoing_booking.isCancelled, stock.bookings))
    offer = stock.resolvedOffer
    venue = offer.venue
    offerer = venue.managingOfferer
    departement_code = offerer.postalCode
    offer_pc_pro_link = build_pc_pro_offer_link(offer)
    environment = format_environment_for_email()
    booked_date = format_booking_date_for_email(booking)
    booked_hour = format_booking_hours_for_email(booking)
    is_active = _is_offer_active_for_recap(stock)

    return {
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'MJ-TemplateID': 780015,
        'MJ-TemplateLanguage': True,
        'To': recipients if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS,
        'Vars': {
            'departement': departement_code,
            'nom_offre': offer.name,
            'lien_offre_pcpro': offer_pc_pro_link,
            'nom_lieu': venue.name,
            'prix': float(stock.price),
            'is_event': int(offer.isEvent),
            'date': booked_date,
            'heure': booked_hour,
            'quantite': booking.quantity,
            'user_name': user.publicName,
            'user_email': user.email,
            'is_active': int(is_active),
            'nombre_resa': len(bookings),
            'env': environment,
            'users': extract_users_information_from_bookings(bookings),
        },
    }


def _is_offer_active_for_recap(stock: Stock) -> bool:
    return stock.resolvedOffer.isActive and stock.remainingQuantity > 0 and stock.isBookable
