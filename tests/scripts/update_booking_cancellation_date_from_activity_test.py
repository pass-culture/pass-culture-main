from models import BookingSQLEntity
from models.db import db
from repository import repository
from scripts.update_booking_cancellation_date_from_activity import update_booking_cancellation_date_from_activity
from tests.conftest import clean_database
from model_creators.generic_creators import create_user, create_stock, create_booking, create_deposit


class UpdateBookingCancellationDateFromActivityTest:

    @staticmethod
    def setup_method():
        db.engine.execute("ALTER TABLE booking DISABLE TRIGGER stock_update_cancellation_date;")

    @staticmethod
    def teardown_method():
        db.engine.execute("ALTER TABLE booking ENABLE TRIGGER stock_update_cancellation_date;")

    @clean_database
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
        count_of_cancelled_booking_without_cancellation_date = BookingSQLEntity.query.filter(
            (BookingSQLEntity.cancellationDate == None),
            (BookingSQLEntity.isCancelled == True)
        ).count()

        assert count_of_cancelled_booking_without_cancellation_date == 0
