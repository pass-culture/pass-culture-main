from datetime import datetime

from models import PcObject, Booking
from scripts.fill_date_used_for_bookings import fill_date_used_for_bookings
from tests.conftest import clean_database
from tests.test_utils import create_booking, create_user, create_deposit, create_booking_activity, save_all_activities


class FillDateUsedForBookingsTest:
    @clean_database
    def test_fill_date_used_for_bookings(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user)
        booking = create_booking(user)
        booking.isUsed = True
        PcObject.save(user, deposit, booking)

        activity_update = create_booking_activity(
            booking, 'booking', 'update', issued_at=datetime(2018, 2, 12),
            data={'isUsed': True}
        )
        save_all_activities(activity_update)

        # When
        fill_date_used_for_bookings()

        # Then
        updated_booking = Booking.query.first()
        assert updated_booking.dateUsed == datetime(2018, 2, 12)

    @clean_database
    def test_does_not_fill_date_used_for_bookings_with_date_used(self, app):
        # Given
        user = create_user()
        deposit = create_deposit(user)
        booking = create_booking(user)
        booking.isUsed = True
        booking.dateUsed = datetime(2019, 2, 12)
        PcObject.save(user, deposit, booking)

        activity_update = create_booking_activity(
            booking, 'booking', 'update', issued_at=datetime(2018, 2, 12),
            data={'isUsed': True}
        )
        save_all_activities(activity_update)

        # When
        fill_date_used_for_bookings()

        # Then
        updated_booking = Booking.query.first()
        assert updated_booking.dateUsed == datetime(2019, 2, 12)
