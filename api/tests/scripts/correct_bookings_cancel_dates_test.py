from datetime import datetime
from unittest.mock import patch

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.models import Booking
from pcapi.repository import repository
from pcapi.scripts.booking import correct_bookings_cancel_dates


class CorrectBookingCancelDatesFromFileTest:
    @pytest.mark.usefixtures("db_session")
    @patch.object(correct_bookings_cancel_dates, "open")
    @patch.object(correct_bookings_cancel_dates.csv, "reader")
    def test_should_correct_booking_cancel_dates_in_csv(self, mock_reader, mock_open):
        # Given
        booking = BookingFactory()
        repository.save(booking)
        new_cancellation_date = datetime.strptime("2018-04-01 03:00:00.00000", "%Y-%m-%d %H:%M:%S.%f")

        csv_rows = [
            [
                "id",
                "cancellationDate",
            ],
            [booking.id, new_cancellation_date],
        ]

        mock_reader.return_value = csv_rows

        # When
        correct_bookings_cancel_dates.run("path/to/my_csv")
        bookings = Booking.query.all()

        # Then
        assert len(bookings) == 1
        assert bookings[0].cancellationDate == new_cancellation_date
