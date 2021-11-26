from datetime import datetime

from pcapi.core.educational.utils import compute_educational_booking_cancellation_limit_date


class ComputeEducationalBookingCancellationLimitDate:
    def test_should_be_15_days_before_event_when_booking_occured_more_than_15_days_before_event(
        self,
    ):
        # Given
        booking_datetime = datetime.fromisoformat("2021-11-04T15:00:00")
        event_beginning_datetime = datetime.fromisoformat("2021-12-15T20:00:00")
        fifteen_days_before_event = datetime.fromisoformat("2021-11-30T20:00:00")

        # When
        cancellation_limit_date = compute_educational_booking_cancellation_limit_date(
            event_beginning_datetime, booking_datetime
        )

        # Then
        assert cancellation_limit_date == fifteen_days_before_event

    def test_should_be_booking_date_when_booking_occured_less_than_15_days_before_event(
        self,
    ):
        # Given
        booking_datetime = datetime.fromisoformat("2021-12-04T15:00:00")
        event_beginning_datetime = datetime.fromisoformat("2021-12-15T20:00:00")

        # When
        cancellation_limit_date = compute_educational_booking_cancellation_limit_date(
            event_beginning_datetime, booking_datetime
        )

        # Then
        assert cancellation_limit_date == booking_datetime
