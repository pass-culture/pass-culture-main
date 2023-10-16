import pytest

import pcapi.core.educational.api.booking as educational_booking_api
import pcapi.core.educational.exceptions as educational_exceptions
import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models


pytestmark = pytest.mark.usefixtures("db_session")


class CancelCollectiveBookingTest:
    def test_can_cancel_before_it_is_used(self):
        booking = educational_factories.CollectiveBookingFactory()

        educational_booking_api.cancel_collective_booking(
            booking,
            educational_models.CollectiveBookingCancellationReasons.OFFERER,
        )
        assert booking.status == educational_models.CollectiveBookingStatus.CANCELLED

    def test_can_cancel_already_used(self):
        finance_event = finance_factories.UsedCollectiveBookingFinanceEventFactory()
        booking = finance_event.collectiveBooking

        educational_booking_api.cancel_collective_booking(
            booking,
            educational_models.CollectiveBookingCancellationReasons.OFFERER,
        )
        assert booking.status == educational_models.CollectiveBookingStatus.CANCELLED
        assert finance_event.status == finance_models.FinanceEventStatus.CANCELLED

    def test_cannot_cancel_already_reimbursed(self):
        finance_event = finance_factories.UsedCollectiveBookingFinanceEventFactory(
            status=finance_models.FinanceEventStatus.PRICED,
            collectiveBooking__status=educational_models.CollectiveBookingStatus.REIMBURSED,
            collectiveBooking__collectiveStock__collectiveOffer__venue__pricing_point="self",
        )
        booking = finance_event.collectiveBooking

        with pytest.raises(educational_exceptions.BookingIsAlreadyRefunded):
            educational_booking_api.cancel_collective_booking(
                booking,
                educational_models.CollectiveBookingCancellationReasons.OFFERER,
            )
        assert booking.status == educational_models.CollectiveBookingStatus.REIMBURSED
        assert finance_event.status == finance_models.FinanceEventStatus.PRICED
