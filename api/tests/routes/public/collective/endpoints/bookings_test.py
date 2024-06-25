from datetime import datetime

from flask import url_for
import pytest

from pcapi.core.educational import testing as educational_testing
import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
from pcapi.core.mails import testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="venue")
def venue_fixture():
    vp = providers_factories.VenueProviderFactory(isActive=True)
    offerers_factories.ApiKeyFactory(provider=vp.provider, offerer=vp.venue.managingOfferer)
    return vp.venue


class CancelCollectiveBookingTest:
    def test_cancel_collective_booking(self, client, venue):
        booking = educational_factories.CollectiveBookingFactory(collectiveStock__collectiveOffer__venue=venue)

        response = self._send_request(client, booking.id)
        assert response.status_code == 204

        db.session.refresh(booking)

        assert booking.cancellationReason == educational_models.CollectiveBookingCancellationReasons.PUBLIC_API
        assert booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp(), rel=1)
        assert booking.status == educational_models.CollectiveBookingStatus.CANCELLED

        assert len(educational_testing.adage_requests) == 1
        assert len(mails_testing.outbox) == 1

    def test_cannot_cancel_reimbursed_booking(self, client, venue):
        booking = educational_factories.ReimbursedCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue=venue
        )

        response = self._send_request(client, booking.id)
        assert response.status_code == 403

        db.session.refresh(booking)
        assert booking.status == educational_models.CollectiveBookingStatus.REIMBURSED

    def test_cannot_cancel_already_cancelled_booking(self, client, venue):
        booking = educational_factories.CancelledCollectiveBookingFactory(collectiveStock__collectiveOffer__venue=venue)

        response = self._send_request(client, booking.id)
        assert response.status_code == 403

        db.session.refresh(booking)
        assert booking.status == educational_models.CollectiveBookingStatus.CANCELLED

    def _send_request(self, client, booking_id: int):
        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        return client.patch(
            url_for("public_api.v2_prefixed_public_api.cancel_collective_booking", booking_id=booking_id)
        )
