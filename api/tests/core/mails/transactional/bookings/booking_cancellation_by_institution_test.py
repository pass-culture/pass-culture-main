import pytest
import time_machine

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models
from pcapi.core.geography import factories as geography_factories
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.educational.eac_booking_cancellation import send_eac_booking_cancellation_email
from pcapi.core.offerers import factories as offerers_factories
from pcapi.utils.date import get_naive_utc_now


@pytest.mark.usefixtures("db_session")
class SendEducationeBookingCancellationByInstitutionEmailTest:
    @time_machine.travel("2024-11-26 18:29:20")
    def test_with_collective_booking(self):
        venue = offerers_factories.VenueFactory()
        offer = educational_factories.CollectiveOfferOnAddressVenueLocationFactory(
            venue=venue, bookingEmails=["pouet@example.com", "plouf@example.com"]
        )
        booking = educational_factories.CollectiveBookingFactory(
            cancellationReason=models.CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE,
            collectiveStock=offer.collectiveStock,
        )

        send_eac_booking_cancellation_email(booking)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["params"] == {
            "OFFER_NAME": booking.collectiveStock.collectiveOffer.name,
            "EDUCATIONAL_INSTITUTION_NAME": booking.educationalInstitution.name,
            "VENUE_NAME": booking.collectiveStock.collectiveOffer.venue.name,
            # datetime is J+10, 18h29 UTC is displayed as Paris time
            "EVENT_DATE": "vendredi 6 décembre 2024",
            "EVENT_HOUR": "19h29",
            "START_DATE": "vendredi 6 décembre 2024",
            "START_HOUR": "19h29",
            "END_DATE": "vendredi 6 décembre 2024",
            "END_HOUR": "19h29",
            "REDACTOR_FIRSTNAME": booking.educationalRedactor.firstName,
            "REDACTOR_LASTNAME": booking.educationalRedactor.lastName,
            "REDACTOR_EMAIL": booking.educationalRedactor.email,
            "EDUCATIONAL_INSTITUTION_CITY": booking.educationalInstitution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": booking.educationalInstitution.postalCode,
            "COLLECTIVE_CANCELLATION_REASON": booking.cancellationReason.value,
            "BOOKING_ID": booking.id,
            "COLLECTIVE_OFFER_ID": booking.collectiveStock.collectiveOfferId,
            "COLLECTIVE_OFFER_ADDRESS": f"{venue.publicName} - {booking.collectiveStock.collectiveOffer.offererAddress.address.fullAddress}",
        }

    @time_machine.travel("2024-11-26 18:29:20")
    def test_with_offer_address(self):
        venue = offerers_factories.VenueFactory(offererAddress__address__departmentCode="33")
        assert venue.offererAddress.address.departmentCode == "33"

        offer = educational_factories.CollectiveOfferOnOtherAddressLocationFactory(
            offererAddress__address=geography_factories.OverseasAddressFactory(), venue=venue
        )
        assert offer.offererAddress.address.departmentCode == "972"
        booking = educational_factories.CancelledCollectiveBookingFactory(collectiveStock=offer.collectiveStock)
        offer.collectiveStock.startDatetime = get_naive_utc_now()
        offer.collectiveStock.endDatetime = get_naive_utc_now()

        send_eac_booking_cancellation_email(booking)

        # check that the hour is located with the offer address (UTC-4)
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["params"]["START_DATE"] == "mardi 26 novembre 2024"
        assert mails_testing.outbox[0]["params"]["START_HOUR"] == "14h29"
        assert mails_testing.outbox[0]["params"]["END_DATE"] == "mardi 26 novembre 2024"
        assert mails_testing.outbox[0]["params"]["END_HOUR"] == "14h29"
