from typing import List, Dict

from models import Booking
from models.offer_type import ProductType
from repository import booking_queries
from utils.mailing import build_pc_pro_offer_link, format_environment_for_email, SUPPORT_EMAIL_ADDRESS, \
    _create_email_recipients, extract_users_information_from_bookings, format_booking_date_for_email, \
    format_booking_hours_for_email


def get_offerer_booking_recap_email_data(booking: Booking, recipients: List[str]) -> Dict:
    offer = booking.stock.resolvedOffer
    venue_name = offer.venue.name
    offer_name = offer.product.name
    price = 'Gratuit' if booking.stock.price == 0 else str(booking.stock.price)
    quantity = booking.quantity
    user_email = booking.user.email
    user_firstname = booking.user.firstName
    user_lastname = booking.user.lastName
    departement_code = offer.venue.departementCode or 'numérique'
    offer_type = offer.type
    is_event = int(offer.isEvent)
    bookings = booking_queries.find_ongoing_bookings_by_stock(
        booking.stock)

    offer_link = build_pc_pro_offer_link(offer)
    environment = format_environment_for_email()

    mailjet_json = {
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'MJ-TemplateID': 1095029,
        'MJ-TemplateLanguage': True,
        'To': _create_email_recipients(recipients),
        'Vars': {
            'nom_offre': offer_name,
            'nom_lieu': venue_name,
            'is_event': is_event,
            'nombre_resa': len(bookings),
            'ISBN': '',
            'offer_type': 'book',
            'date': '',
            'heure': '',
            'quantity': quantity,
            'contremarque': booking.token,
            'prix': price,
            'users': extract_users_information_from_bookings(bookings),
            'user_firstName': user_firstname,
            'user_lastName': user_lastname,
            'user_email': user_email,
            'lien_offre_pcpro': offer_link,
            'departement': departement_code,
            'env': environment
        },
    }

    offer_is_a_book = ProductType.is_book(offer_type)

    if offer_is_a_book:
        mailjet_json['Vars']['ISBN'] = offer.extraData['isbn'] if offer.extraData is not None \
                                                                  and 'isbn' in offer.extraData else ''
    else:
        mailjet_json['Vars']['offer_type'] = offer_type

    offer_is_an_event = is_event == 1
    if offer_is_an_event:
        mailjet_json['Vars']['date'] = format_booking_date_for_email(booking)
        mailjet_json['Vars']['heure'] = format_booking_hours_for_email(booking)

    return mailjet_json