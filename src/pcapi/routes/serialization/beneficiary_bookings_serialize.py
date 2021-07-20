from pcapi.domain.beneficiary_bookings.beneficiary_booking import BeneficiaryBooking
from pcapi.domain.beneficiary_bookings.beneficiary_bookings_with_stocks import BeneficiaryBookingsWithStocks
from pcapi.domain.beneficiary_bookings.stock import Stock
from pcapi.routes.serialization import serialize
from pcapi.utils.human_ids import humanize


def serialize_beneficiary_bookings(
    beneficiary_bookings: BeneficiaryBookingsWithStocks, with_qr_code: bool = False
) -> list:
    results = []
    for beneficiary_booking in beneficiary_bookings.bookings:
        serialized_stocks = _serialize_stocks_for_beneficiary_bookings(
            beneficiary_booking.offerId, beneficiary_bookings.stocks
        )
        serialized_booking = _serialize_beneficiary_booking(
            beneficiary_booking, serialized_stocks, with_qr_code=with_qr_code
        )
        results.append(serialized_booking)
    return results


def _serialize_stock_for_beneficiary_booking(stock: Stock) -> dict:
    return {
        "dateCreated": serialize(stock.date_created),
        "beginningDatetime": serialize(stock.beginning_datetime),
        "bookingLimitDatetime": serialize(stock.booking_limit_datetime),
        "dateModified": serialize(stock.date_modified),
        "offerId": humanize(stock.offer_id),
        "quantity": stock.quantity,
        "price": stock.price,
        "id": humanize(stock.id),
        "isBookable": stock.is_available_for_booking,
        "remainingQuantity": "unlimited",
    }


def _serialize_stocks_for_beneficiary_bookings(matched_offer_id: int, stocks: list[Stock]) -> list[dict]:
    return [_serialize_stock_for_beneficiary_booking(stock) for stock in stocks if stock.offer_id == matched_offer_id]


def _serialize_offer_is_bookable(serialized_stocks: list[dict]) -> bool:
    are_stocks_bookable = [stock["isBookable"] for stock in serialized_stocks]
    return True in are_stocks_bookable


def _serialize_beneficiary_booking(
    beneficiary_booking: BeneficiaryBooking, serialized_stocks: list[dict], with_qr_code: bool = False
) -> dict:
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
        "status": beneficiary_booking.status,
        "displayAsEnded": beneficiary_booking.displayAsEnded,
        "activationCode": beneficiary_booking.activationCode,
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
                "thumbUrl": beneficiary_booking.thumb_url,
                "stocks": serialized_stocks,
                "isBookable": _serialize_offer_is_bookable(serialized_stocks),
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
