from unittest.mock import patch

import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.mails.transactional.bookings.booking_cancellation_by_institution import (
    send_education_booking_cancellation_by_institution_email,
)


@pytest.mark.usefixtures("db_session")
class SendEducationeBookingCancellationByInstitutionEmailTest:
    @patch("pcapi.core.mails.transactional.bookings.booking_cancellation_by_institution.mails")
    def test_with_collective_booking(self, mails):
        # given
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__bookingEmail="pouet@example.com",
        )

        # when
        send_education_booking_cancellation_by_institution_email(booking)

        # then
        mails.send.assert_called_once()
        assert mails.send.call_args.kwargs["data"].params == {
            "OFFER_NAME": booking.collectiveStock.collectiveOffer.name,
            "EDUCATIONAL_INSTITUTION_NAME": booking.educationalInstitution.name,
            "VENUE_NAME": booking.collectiveStock.collectiveOffer.venue.name,
            "EVENT_DATE": booking.collectiveStock.beginningDatetime.strftime("%d/%m/%Y"),
            "EVENT_HOUR": booking.collectiveStock.beginningDatetime.strftime("%H:%M"),
            "REDACTOR_FIRSTNAME": booking.educationalRedactor.firstName,
            "REDACTOR_LASTNAME": booking.educationalRedactor.lastName,
            "REDACTOR_EMAIL": booking.educationalRedactor.email,
            "EDUCATIONAL_INSTITUTION_CITY": booking.educationalInstitution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": booking.educationalInstitution.postalCode,
        }
