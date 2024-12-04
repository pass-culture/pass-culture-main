from datetime import datetime

from pcapi.core.educational import utils


class ComputeEducationalBookingCancellationLimitDateTest:
    def test_should_be_30_days_before_event_when_booking_occured_more_than_15_days_before_event(
        self,
    ) -> None:
        # Given
        booking_datetime = datetime.fromisoformat("2021-11-04T15:00:00")
        event_beginning_datetime = datetime.fromisoformat("2021-12-15T20:00:00")
        fifteen_days_before_event = datetime.fromisoformat("2021-11-15T20:00:00")

        # When
        cancellation_limit_date = utils.compute_educational_booking_cancellation_limit_date(
            event_beginning_datetime, booking_datetime
        )

        # Then
        assert cancellation_limit_date == fifteen_days_before_event

    def test_should_be_30_days_before_event_when_booking_occured_more_than_30_days_before_event(
        self,
    ) -> None:
        # Given
        booking_datetime = datetime.fromisoformat("2021-11-04T15:00:00")
        event_beginning_datetime = datetime.fromisoformat("2021-12-15T20:00:00")
        thirty_days_before_event = datetime.fromisoformat("2021-11-15T20:00:00")

        # When
        cancellation_limit_date = utils.compute_educational_booking_cancellation_limit_date(
            event_beginning_datetime, booking_datetime
        )

        # Then
        assert cancellation_limit_date == thirty_days_before_event

    def test_should_be_booking_date_when_booking_occured_less_than_15_days_before_event(
        self,
    ) -> None:
        # Given
        booking_datetime = datetime.fromisoformat("2021-12-04T15:00:00")
        event_beginning_datetime = datetime.fromisoformat("2021-12-15T20:00:00")

        # When
        cancellation_limit_date = utils.compute_educational_booking_cancellation_limit_date(
            event_beginning_datetime, booking_datetime
        )

        # Then
        assert cancellation_limit_date == booking_datetime


class HashUserEmailTest:
    def test_should_hash_user_email(self) -> None:
        # Given
        email = "test@mail.com"

        # When
        result = utils.get_hashed_user_id(email)

        # Then
        assert result == "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816"


class GetNonEmptyDateTimeRangeTest:
    def test_get_non_empty_datetime_range(self) -> None:
        start = datetime(2024, 12, 24, 23, 59, 59)
        end = datetime(2024, 12, 25, 23, 59, 59)

        result = utils.get_non_empty_date_time_range(start, end)

        assert result.lower == start
        assert result.upper == end

    def test_get_non_empty_datetime_range_ends_when_starts(self) -> None:
        start = datetime(2024, 12, 24, 23, 59, 59)

        result = utils.get_non_empty_date_time_range(start, start)

        assert result.lower == start
        assert result.upper == datetime(2024, 12, 25, 0, 0, 0)
