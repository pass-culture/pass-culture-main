from datetime import datetime
from datetime import timedelta

from pcapi.core.educational.utils import compute_cancellation_limit_date_for_educational_booking


class ComputeCancellationLimitDateForEducationalBookingTest:
    def test_cancellation_limit_date_is_15_days_before_event_when_booking_occured_more_than_15_days_before_event_and_event_utc(
        self,
    ):
        # Given
        booking_datetime = datetime(2021, 11, 5, 15, 30)
        event_beginning_datetime = booking_datetime + timedelta(days=30, hours=4)

        # When
        cancellation_limit_date = compute_cancellation_limit_date_for_educational_booking(
            event_beginning_datetime, booking_datetime
        )

        # Then
        assert cancellation_limit_date == event_beginning_datetime - timedelta(days=15)

    def test_cancellation_limit_date_is_booking_date_when_booking_occured_less_than_15_days_before_event_and_event_utc(
        self,
    ):
        pass
