from models import Booking

def filter_booking_by_offer_id(bookings, offers):
    selected = None
    for offer in offers:
        for booking in bookings:
            if booking.stockId == offer.id:
                selected = offer.Offer
                break
    return selected

def get_cancellable_bookings_for_user(user):
    query = Booking.query.filter_by(
        userId=user.id
    )
    bookings = [b for b in query.all() if b.isUserCancellable]
    return bookings

def get_not_cancellable_bookings_for_user(user):
    query = Booking.query.filter_by(
        userId=user.id
    )
    bookings = [b for b in query.all() if not b.isUserCancellable]
    return bookings
