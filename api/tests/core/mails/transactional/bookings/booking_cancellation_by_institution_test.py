from unittest.mock import patch

import pytest
import time_machine

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models
from pcapi.core.mails.transactional.educational.eac_booking_cancellation import send_eac_booking_cancellation_email
from pcapi.core.offerers import factories as offerers_factories


@pytest.mark.usefixtures("db_session")
class SendEducationeBookingCancellationByInstitutionEmailTest:
    @time_machine.travel("2024-11-26 18:29:20")
    @patch("pcapi.core.mails.transactional.educational.eac_booking_cancellation.mails")
    def test_with_collective_booking(self, mails):
        venue = offerers_factories.VenueFactory()
        booking = educational_factories.CollectiveBookingFactory(
            cancellationReason=models.CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE,
            collectiveStock__collectiveOffer__bookingEmails=["pouet@example.com", "plouf@example.com"],
            collectiveStock__collectiveOffer__venue=venue,
            collectiveStock__collectiveOffer__locationType=models.CollectiveLocationType.ADDRESS,
            collectiveStock__collectiveOffer__offererAddress=venue.offererAddress,
        )

        send_eac_booking_cancellation_email(booking)

        mails.send.assert_called_once()
        assert mails.send.call_args.kwargs["data"].params == {
            "OFFER_NAME": booking.collectiveStock.collectiveOffer.name,
            "EDUCATIONAL_INSTITUTION_NAME": booking.educationalInstitution.name,
            "VENUE_NAME": booking.collectiveStock.collectiveOffer.venue.name,
            "EVENT_DATE": "mercredi 27 novembre 2024",
            "EVENT_HOUR": "19h29",
            "REDACTOR_FIRSTNAME": booking.educationalRedactor.firstName,
            "REDACTOR_LASTNAME": booking.educationalRedactor.lastName,
            "REDACTOR_EMAIL": booking.educationalRedactor.email,
            "EDUCATIONAL_INSTITUTION_CITY": booking.educationalInstitution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": booking.educationalInstitution.postalCode,
            "COLLECTIVE_CANCELLATION_REASON": booking.cancellationReason.value,
            "BOOKING_ID": booking.id,
            "COLLECTIVE_OFFER_ADDRESS": f"{venue.common_name} - {booking.collectiveStock.collectiveOffer.offererAddress.address.fullAddress}",
        }
