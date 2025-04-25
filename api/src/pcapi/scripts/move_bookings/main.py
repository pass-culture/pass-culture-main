from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import models as bookings_models
from pcapi.models import db


NEW_STOCK_ID = 334037110
OLD_STOCK_ID = 328050857


if __name__ == "__main__":
    from pcapi.flask_app import app

    with app.app_context():
        print("Starting update")

        bookings = bookings_models.Booking.query.filter(
            bookings_models.Booking.stockId == OLD_STOCK_ID,
            bookings_models.Booking.status == bookings_models.BookingStatus.CONFIRMED,
        ).all()
        print(f"{len(bookings)} bookings to update")

        for booking in bookings:
            booking.stockId = NEW_STOCK_ID
            db.session.add(booking)
        db.session.commit()

        bookings_api.recompute_dnBookedQuantity([OLD_STOCK_ID, NEW_STOCK_ID])
        db.session.commit()
        print("Update complete")
