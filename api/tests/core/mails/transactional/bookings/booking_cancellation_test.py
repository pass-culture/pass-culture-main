import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.bookings.booking_cancellation import (
    send_booking_cancellation_confirmation_by_pro_to_pro_email,
)


pytestmark = pytest.mark.usefixtures("db_session")


class SendOffererDrivenCancellationEmailToOffererTest:
    def test_should_send_cancellation_by_offerer_email_to_offerer(self):
        # Given
        booking = bookings_factories.IndividualBookingFactory(
            stock__offer__bookingEmail="offer@example.com",
        )

        # When
        send_booking_cancellation_confirmation_by_pro_to_pro_email(booking)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["To"] == "offer@example.com"
