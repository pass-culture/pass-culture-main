from typing import Any
from unittest.mock import patch

import pytest
import time_machine

from pcapi.core.educational import factories as educational_factories
from pcapi.core.mails.transactional.educational.eac_new_booking_to_pro import send_eac_new_booking_email_to_pro


pytestmark = pytest.mark.usefixtures("db_session")


class SendEacNewBookingEmailToProTest:
    @time_machine.travel("2019-11-26 18:29:20")
    @patch("pcapi.core.mails.transactional.educational.eac_new_booking_to_pro.mails")
    def test_with_collective_booking(self, mails: Any) -> None:
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__bookingEmails=["pouet@example.com", "plouf@example.com"],
        )

        send_eac_new_booking_email_to_pro(booking)

        mails.send.assert_called_once()
        assert mails.send.call_args.kwargs["data"].params == {
            "OFFER_NAME": booking.collectiveStock.collectiveOffer.name,
            "VENUE_NAME": booking.collectiveStock.collectiveOffer.venue.name,
            "EVENT_DATE": "mercredi 27 novembre 2019",
            "EVENT_HOUR": "19h29",
            "QUANTITY": 1,
            "PRICE": "100.00 €",
            "FORMATTED_PRICE": "100 €",
            "REDACTOR_FIRSTNAME": booking.educationalRedactor.firstName,
            "REDACTOR_LASTNAME": booking.educationalRedactor.lastName,
            "REDACTOR_EMAIL": booking.educationalRedactor.email,
            "EDUCATIONAL_INSTITUTION_NAME": booking.educationalInstitution.name,
            "EDUCATIONAL_INSTITUTION_CITY": booking.educationalInstitution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": booking.educationalInstitution.postalCode,
            "IS_EVENT": True,
            "BOOKING_ID": booking.id,
            "COLLECTIVE_OFFER_ADDRESS": "À déterminer avec l'enseignant",
        }
