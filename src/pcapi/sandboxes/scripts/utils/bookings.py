from pcapi.models import Booking


def find_offer_compatible_with_bookings(offer_with_stock_id_tuples, bookings):
    compatible_offer = None
    for offer_with_stock_id_tuple in offer_with_stock_id_tuples:
        for booking in bookings:
            if booking.stockId == offer_with_stock_id_tuple[1]:
                compatible_offer = offer_with_stock_id_tuple[0]
                break
    return compatible_offer

def get_cancellable_bookings_for_user(user):
    query = Booking.query.filter_by(
        userId=user.id
    )
    bookings = [b for b in query.all() if b.isUserCancellable]
    return bookings
