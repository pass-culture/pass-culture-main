from typing import Any
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.mails.transactional.educational.eac_new_booking_to_pro import send_eac_new_booking_email_to_pro


pytestmark = pytest.mark.usefixtures("db_session")


class SendEacNewBookingEmailToProTest:
    @freeze_time("2019-11-26 18:29:20.891028")
    @patch("pcapi.core.mails.transactional.educational.eac_new_booking_to_pro.mails")
    def test_with_collective_booking(self, mails: Any) -> None:
        # given
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__bookingEmail="pouet@example.com",
        )

        # when
        send_eac_new_booking_email_to_pro(booking)

        # then
        mails.send.assert_called_once()
        assert mails.send.call_args.kwargs["data"].params == {
            "OFFER_NAME": booking.collectiveStock.collectiveOffer.name,
            "VENUE_NAME": booking.collectiveStock.collectiveOffer.venue.name,
            "EVENT_DATE": "27-Nov-2019",
            "EVENT_HOUR": "19h29",
            "QUANTITY": 1,
            "PRICE": "100.00 €",
            "REDACTOR_FIRSTNAME": booking.educationalRedactor.firstName,
            "REDACTOR_LASTNAME": booking.educationalRedactor.lastName,
            "REDACTOR_EMAIL": booking.educationalRedactor.email,
            "EDUCATIONAL_INSTITUTION_NAME": booking.educationalInstitution.name,
            "EDUCATIONAL_INSTITUTION_CITY": booking.educationalInstitution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": booking.educationalInstitution.postalCode,
            "IS_EVENT": True,
        }
