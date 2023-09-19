from datetime import datetime

import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models
from pcapi.core.educational import testing as educational_testing
from pcapi.core.mails import testing as mails_testing
from pcapi.models import db
from pcapi.routes.public.united.endpoints.collective_bookings import cancel_collective_booking

from tests.routes.public.united import helpers


pytestmark = pytest.mark.usefixtures("db_session")


class CancelCollectiveBookingTest(helpers.PublicApiBaseTest):
    controller = cancel_collective_booking

    def test_cancel_booking(self, api_client, collective_booking):
        path = self.build_path(booking_id=collective_booking.id)
        with self.assert_valid_response(api_client, path=path):
            db.session.refresh(collective_booking)

            assert collective_booking.status == models.CollectiveBookingStatus.CANCELLED
            assert collective_booking.cancellationReason == models.CollectiveBookingCancellationReasons.PUBLIC_API
            assert (datetime.utcnow() - collective_booking.cancellationDate).total_seconds() < 15
            assert not collective_booking.dateUsed

            assert len(educational_testing.adage_requests) == 1
            assert len(mails_testing.outbox) == 1

    class UnauthorizedTest(helpers.UnauthorizedBaseTest):
        controller = cancel_collective_booking

        @pytest.mark.parametrize(
            "status", [models.CollectiveBookingStatus.REIMBURSED, models.CollectiveBookingStatus.CANCELLED]
        )
        def test_cannot_cancel_booking(self, api_client, collective_stock, status):
            booking = educational_factories.CollectiveBookingFactory(
                collectiveStock=collective_stock,
                status=status,
            )

            path = self.build_path(booking_id=booking.id)
            with self.assert_valid_response(api_client, path=path):
                db.session.refresh(booking)

                assert booking.status == status

                assert not educational_testing.adage_requests
                assert not mails_testing.outbox

    class ErrorTest(helpers.PublicApiBaseTest, helpers.UnauthenticatedMixin, helpers.UnknownResourceMixin):
        controller = cancel_collective_booking
        path_kwargs = {"booking_id": 1}
