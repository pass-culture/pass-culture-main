import pytest

from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_deposit
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user
from pcapi.models import Booking
from pcapi.models.db import db
from pcapi.repository import repository
from pcapi.scripts.update_booking_cancellation_date_from_activity import update_booking_cancellation_date_from_activity


class UpdateBookingCancellationDateFromActivityTest:

    @staticmethod
    def setup_method():
        db.engine.execute("ALTER TABLE booking DISABLE TRIGGER stock_update_cancellation_date;")

    @staticmethod
    def teardown_method():
        db.engine.execute("ALTER TABLE booking ENABLE TRIGGER stock_update_cancellation_date;")

    @pytest.mark.usefixtures("db_session")
    def test_should_fill_cancellation_date_using_activity(self, app):
        # Given
        user = create_user()
        create_deposit(user, amount=500)
        booking = create_booking(user=user, quantity=1, is_cancelled=False)
        repository.save(booking)

        booking.isCancelled = True
        repository.save(booking)

        # When
        update_booking_cancellation_date_from_activity()

        # Then
        count_of_cancelled_booking_without_cancellation_date = Booking.query.filter(
            (Booking.cancellationDate == None),
            (Booking.isCancelled == True)
        ).count()

        assert count_of_cancelled_booking_without_cancellation_date == 0
