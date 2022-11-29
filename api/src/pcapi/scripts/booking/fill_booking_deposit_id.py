from pcapi.core.bookings import models as bookings_models
from pcapi.models import db


def fill_booking_deposit_id(batch_size: int = 1000, start_id: int = 0) -> None:
    max_individual_booking_id = (
        bookings_models.IndividualBooking.query.with_entities(bookings_models.IndividualBooking.id)
        .order_by(bookings_models.IndividualBooking.id.desc())
        .limit(1)
        .one()[0]
    )

    start_index = start_id

    while start_index < max_individual_booking_id:
        end_index = min(start_index + batch_size, max_individual_booking_id)
        print(f"updating booking between {start_index} and {end_index}")
        db.session.execute(
            f"""
            UPDATE booking
            SET "depositId" = individual_booking."depositId"
            FROM individual_booking
            WHERE individual_booking.id = booking."individualBookingId"
            AND booking.id BETWEEN {start_index} AND {end_index};
            """
        )
        db.session.commit()
        start_index = end_index + 1
    print("DONE")
