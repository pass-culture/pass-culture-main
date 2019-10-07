from models import Booking, PcObject
from repository import booking_queries

CHUNK_SIZE = 500


def fill_date_used_for_bookings():
    bookings = Booking.query \
        .filter_by(isUsed=True) \
        .filter(Booking.dateUsed == None) \
        .all()
    print("Number of bookings found: %s" % len(bookings))
    bookings_id_errors = []
    counter = 0

    for booking in bookings:
        booking.dateUsed = booking_queries.find_date_used(booking)
        try:
            PcObject.save(booking)
        except Exception:
            print("Error saving booking %s" % booking.id)
            bookings_id_errors.append(booking.id)

        counter += 1
        if counter % CHUNK_SIZE == 0:
            print("Processed %s bookings" % counter)

    print("Booking ids in errors :")
    print(bookings_id_errors)
