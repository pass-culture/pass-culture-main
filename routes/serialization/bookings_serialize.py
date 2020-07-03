from typing import Dict

from domain.booking.booking import Booking
from models import BookingSQLEntity, EventType, ThingType
from routes.serialization import serialize
from utils.human_ids import humanize


def serialize_booking(booking: BookingSQLEntity) -> Dict:
    booking_id = humanize(booking.id)
    user_email = booking.user.email
    is_used = booking.isUsed
    offer_name = booking.stock.offer.product.name
    user_name = booking.user.publicName
    venue_departement_code = booking.stock.offer.venue.departementCode
    offer_id = booking.stock.offer.id
    venue_name = booking.stock.offer.venue.name
    venue_address = booking.stock.offer.venue.address
    offer_type = 'EVENEMENT' if booking.stock.offer.isEvent else 'BIEN'
    offer_formula = ''
    if booking.stock.offer.type == str(EventType.CINEMA):
        offer_formula = 'PLACE'
    elif booking.stock.offer.type == str(ThingType.CINEMA_ABO):
        offer_formula = 'ABO'
    offer_date_time = serialize(booking.stock.beginningDatetime) if booking.stock.beginningDatetime else ''
    price = booking.stock.price
    quantity = booking.quantity
    offer_extra_data = booking.stock.offer.extraData
    product_isbn = ''
    if offer_extra_data and 'isbn' in offer_extra_data:
        product_isbn = offer_extra_data['isbn']
    date_of_birth = ''
    phone_number = ''
    if booking.stock.offer.product.type == str(EventType.ACTIVATION):
        date_of_birth = serialize(booking.user.dateOfBirth)
        phone_number = booking.user.phoneNumber

    return {
        'bookingId': booking_id,
        'dateOfBirth': date_of_birth,
        'datetime': offer_date_time,
        'ean13': product_isbn,
        'email': user_email,
        'formula': offer_formula,
        'isUsed': is_used,
        'offerId': offer_id,
        'offerName': offer_name,
        'offerType': offer_type,
        'phoneNumber': phone_number,
        'price': price,
        'quantity': quantity,
        'userName': user_name,
        'venueAddress': venue_address,
        'venueDepartementCode': venue_departement_code,
        'venueName': venue_name
    }


def serialize_domain_booking(booking: Booking) -> Dict:
    return {
        'amount': booking.amount,
        'completedUrl': booking.completed_url,
        'id': humanize(booking.identifier),
        'isCancelled': booking.isCancelled,
        'quantity': booking.quantity,
        'stockId': humanize(booking.stock.identifier),
        'stock': {
            'price': booking.stock.price
        },
        'token': booking.token,
        'user': {
            'id': humanize(booking.beneficiary.identifier),
            "wallet_balance": booking.beneficiary.wallet_balance,
        },
    }
