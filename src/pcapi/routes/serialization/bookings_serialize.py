from typing import Dict
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import Field

from pcapi.models import Booking
from pcapi.models import EventType
from pcapi.models import ThingType
from pcapi.routes.serialization import serialize
from pcapi.serialization.utils import to_camel
from pcapi.utils.human_ids import humanize


def serialize_booking(booking: Booking) -> Dict:
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
        'publicOfferId': humanize(offer_id),
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


def serialize_booking_minimal(booking: Booking) -> Dict:
    return {
        'amount': float(booking.amount),
        'completedUrl': booking.completedUrl,
        'id': humanize(booking.id),
        'isCancelled': booking.isCancelled,
        'quantity': booking.quantity,
        'stockId': humanize(booking.stockId),
        'stock': {
            'price': booking.stock.price
        },
        'token': booking.token,
        'user': {
            'id': humanize(booking.userId),
            "wallet_balance": float(booking.user.wallet_balance),
        },
    }


class PostBookingStockModel(BaseModel):
    price: float


class PostBookingUserModel(BaseModel):
    id: str
    wallet_balance: float


class PostBookingBodyModel(BaseModel):
    stock_id: str
    recommendation_id: Optional[str]
    quantity: int

    class Config:
        alias_generator = to_camel


class PostBookingResponseModel(BaseModel):
    amount: float
    completedUrl: Optional[str]
    id: str
    isCancelled: bool
    quantity: int
    stock: PostBookingStockModel
    stockId: str
    token: str
    user: PostBookingUserModel

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
