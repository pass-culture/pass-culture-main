from datetime import timedelta
import pytest
import time_machine

from pcapi.core.bookings.api import auto_mark_as_used_after_event
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.testing import override_features


@pytest.mark.usefixtures("db_session")
class EducationalApiIntegrationTest:
    @override_features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    def test_integration(self, db_session):
        with time_machine.travel("2024-12-06") as traveller:
            collective_offer = educational_factories.BookedCollectiveOfferFactory()
            collective_stock = collective_offer.collectiveStock
            collective_booking = collective_stock.collectiveBookings[0]

            beginning_datetime = collective_stock.beginningDatetime

            assert collective_offer.displayedStatus == educational_models.CollectiveOfferDisplayedStatus.BOOKED

            traveller.move_to(beginning_datetime + timedelta(days=4))

            # The offer displayed status is updated to ENDED
            assert collective_offer.displayedStatus == educational_models.CollectiveOfferDisplayedStatus.ENDED
            # but the booking status is still CONFIRMED
            assert collective_booking.status == educational_models.CollectiveBookingStatus.CONFIRMED

            # Mark the booking as used
            auto_mark_as_used_after_event()

            assert collective_booking.status == educational_models.CollectiveBookingStatus.USED
            assert collective_offer.displayedStatus == educational_models.CollectiveOfferDisplayedStatus.ENDED

            # Generate the Reimbursement
            # launch _generate_invoice_legacy after creating a batch of cashflows

            # assert collective_offer.displayedStatus == educational_models.CollectiveOfferDisplayedStatus.REIMBURSED
