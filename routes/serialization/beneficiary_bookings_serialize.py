from datetime import datetime
from typing import List

from domain.beneficiary_bookings.beneficiary_bookings import BeneficiaryBookings
from models.offer_type import ProductType
from routes.serialization import as_dict, serialize
from utils.human_ids import humanize


def serialize_beneficiary_bookings(beneficiary_bookings: BeneficiaryBookings) -> List:
    results = []
    for booking_view in beneficiary_bookings.bookings:
        serialized_stocks = [as_dict(stock) for stock in beneficiary_bookings.stocks if
                             stock.offerId == booking_view.offerId]
        dictified_booking = {
            "completedUrl": _serialize_completed_url(booking_view),
            "isEventExpired": _serialize_stock_is_event_expired(booking_view),
            "amount": booking_view.amount,
            "cancellationDate": serialize(booking_view.cancellationDate),
            "dateCreated": serialize(booking_view.dateCreated),
            "dateUsed": serialize(booking_view.dateUsed),
            "id": humanize(booking_view.id),
            "isCancelled": booking_view.isCancelled,
            "isUsed": booking_view.isUsed,
            "quantity": booking_view.quantity,
            "qrCode": 'FAKE_QR_CODE',
            "recommendationId": humanize(booking_view.recommendationId),
            "stock": {
                "id": humanize(booking_view.stockId),
                "beginningDatetime": serialize(booking_view.beginningDatetime),
                "offerId": humanize(booking_view.offerId),
                "offer": {
                    "id": humanize(booking_view.offerId),
                    "isDigital": booking_view.url is not None and booking_view.url != '',
                    "isEvent": ProductType.is_event(booking_view.type),
                    "name": booking_view.name,
                    "thumb_url": '',
                    "stocks": serialized_stocks,
                    "venue": {
                        "id": humanize(booking_view.venueId),
                        "departementCode": booking_view.departementCode,
                    },
                }
            },
            "stockId": humanize(booking_view.stockId),
            "token": booking_view.token,
            "userId": humanize(booking_view.userId),
        }
        results.append(dictified_booking)

    return results


def _serialize_completed_url(booking_view: object) -> str:
    url = booking_view.url
    if url is None:
        return None
    if not url.startswith('http'):
        url = "http://" + url
    return url.replace('{token}', booking_view.token) \
        .replace('{offerId}', humanize(booking_view.id)) \
        .replace('{email}', booking_view.email)


def _serialize_stock_is_event_expired(bookings_view):
    return False if bookings_view.beginningDatetime is None else bookings_view.beginningDatetime <= datetime.utcnow()
