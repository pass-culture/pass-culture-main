from typing import List, Dict

from domain.beneficiary_bookings.beneficiary_bookings import BeneficiaryBookings, BeneficiaryBooking
from domain.beneficiary_bookings.stock import Stock
from routes.serialization import serialize
from utils.human_ids import humanize


def serialize_beneficiary_bookings(beneficiary_bookings: BeneficiaryBookings, with_qr_code: bool = False) -> List:
    results = []
    for beneficiary_booking in beneficiary_bookings.bookings:
        serialized_stocks = _serialize_stocks_for_beneficiary_bookings(beneficiary_booking.offerId,
                                                                       beneficiary_bookings.stocks)
        serialized_booking = _serialize_beneficiary_booking(beneficiary_booking,
                                                            serialized_stocks,
                                                            with_qr_code=with_qr_code)
        results.append(serialized_booking)
    return results


def _serialize_stock_for_beneficiary_booking(stock: Stock) -> Dict:
    return {
        "dateCreated": serialize(stock.dateCreated),
        "beginningDatetime": serialize(stock.beginningDatetime),
        "bookingLimitDatetime": serialize(stock.bookingLimitDatetime),
        "dateModified": serialize(stock.dateModified),
        "offerId": humanize(stock.offerId),
        "quantity": stock.quantity,
        "price": stock.price,
        "id": humanize(stock.id),
    }


def _serialize_stocks_for_beneficiary_bookings(matched_offer_id: int, stocks: List[Stock]) -> List[Dict]:
    return [_serialize_stock_for_beneficiary_booking(stock) for stock in stocks if stock.offerId == matched_offer_id]


def _serialize_beneficiary_booking(beneficiary_booking: BeneficiaryBooking, serialized_stocks: List[Dict],
                                   with_qr_code: bool = False) -> Dict:
    dictified_booking = {
        "completedUrl": beneficiary_booking.booking_access_url,
        "isEventExpired": beneficiary_booking.is_event_expired,
        "amount": beneficiary_booking.amount,
        "cancellationDate": serialize(beneficiary_booking.cancellationDate),
        "dateCreated": serialize(beneficiary_booking.dateCreated),
        "dateUsed": serialize(beneficiary_booking.dateUsed),
        "id": humanize(beneficiary_booking.id),
        "isCancelled": beneficiary_booking.isCancelled,
        "isUsed": beneficiary_booking.isUsed,
        "quantity": beneficiary_booking.quantity,
        "recommendationId": humanize(beneficiary_booking.recommendationId),
        "stock": {
            "id": humanize(beneficiary_booking.stockId),
            "beginningDatetime": serialize(beneficiary_booking.beginningDatetime),
            "offerId": humanize(beneficiary_booking.offerId),
            "price": beneficiary_booking.price,
            "isEventExpired": beneficiary_booking.is_event_expired,
            "offer": {
                "description": beneficiary_booking.description,
                "durationMinutes": beneficiary_booking.durationMinutes,
                "extraData": beneficiary_booking.extraData,
                "isDuo": beneficiary_booking.isDuo,
                "withdrawalDetails": beneficiary_booking.withdrawalDetails,
                "id": humanize(beneficiary_booking.offerId),
                "isDigital": beneficiary_booking.is_booked_offer_digital,
                "isEvent": beneficiary_booking.is_booked_offer_event,
                "isNational": beneficiary_booking.isNational,
                "name": beneficiary_booking.name,
                "offerType": beneficiary_booking.humanized_offer_type,
                "thumb_url": '',
                "stocks": serialized_stocks,
                "venue": {
                    "id": humanize(beneficiary_booking.venueId),
                    "departementCode": beneficiary_booking.departementCode,
                    "name": beneficiary_booking.venueName,
                    "address": beneficiary_booking.address,
                    "postalCode": beneficiary_booking.postalCode,
                    "city": beneficiary_booking.city,
                    "latitude": beneficiary_booking.latitude,
                    "longitude": beneficiary_booking.longitude,
                },
                "venueId": humanize(beneficiary_booking.venueId),
            },
        },
        "stockId": humanize(beneficiary_booking.stockId),
        "token": beneficiary_booking.token,
        "userId": humanize(beneficiary_booking.userId),
    }
    if with_qr_code:
        dictified_booking["qrCode"] = beneficiary_booking.qr_code
    return dictified_booking
