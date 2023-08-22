from datetime import datetime

from flask import url_for
from freezegun import freeze_time
import pytest

import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class GetCollectiveBookingTest:
    def test_get_collective_booking(self, client):
        vp = providers_factories.VenueProviderFactory(isActive=True)
        offerers_factories.ApiKeyFactory(provider=vp.provider, offerer=vp.venue.managingOfferer)

        booking = educational_factories.UsedCollectiveBookingFactory(collectiveStock__collectiveOffer__venue=vp.venue)

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        response = client.get(url_for("pro_public_api_v2.get_collective_booking", booking_id=booking.id))

        assert response.status_code == 200
        assert response.json == {
            "id": booking.id,
            "status": booking.status.value,
            "dateUsed": booking.dateUsed.isoformat(),
            "cancellationLimitDate": booking.cancellationLimitDate.isoformat(),
            "dateCreated": booking.dateCreated.isoformat(),
            "confirmationDate": booking.confirmationDate.isoformat(),
            "educationalYear": {
                "adageId": booking.educationalYear.adageId,
                "beginningDate": booking.educationalYear.beginningDate.isoformat(),
                "expirationDate": booking.educationalYear.expirationDate.isoformat(),
            },
            "venueId": booking.venueId,
        }

    def test_not_found_if_booking_does_not_exist(self, client):
        vp = providers_factories.VenueProviderFactory(isActive=True)
        offerers_factories.ApiKeyFactory(provider=vp.provider, offerer=vp.venue.managingOfferer)

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        response = client.get(url_for("pro_public_api_v2.get_collective_booking", booking_id=-1))

        assert response.status_code == 404

    def test_not_found_if_missing_access_rights(self, client):
        offerers_factories.ApiKeyFactory()
        booking = educational_factories.CollectiveBookingFactory()

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        response = client.get(url_for("pro_public_api_v2.get_collective_booking", booking_id=booking.id))

        assert response.status_code == 404


@pytest.fixture(name="venue")
def venue_fixture():
    vp = providers_factories.VenueProviderFactory(isActive=True)
    offerers_factories.ApiKeyFactory(provider=vp.provider, offerer=vp.venue.managingOfferer)
    return vp.venue


class CancelCollectiveBookingTest:
    @freeze_time("2023-01-01 10:00:00")
    def test_cancel_collective_booking(self, client, venue):
        booking = educational_factories.CollectiveBookingFactory(collectiveStock__collectiveOffer__venue=venue)

        response = self._send_request(client, booking.id)
        assert response.status_code == 204

        db.session.refresh(booking)

        assert booking.cancellationReason == educational_models.CollectiveBookingCancellationReasons.PUBLIC_API
        assert booking.cancellationDate == datetime(2023, 1, 1, 10)
        assert booking.status == educational_models.CollectiveBookingStatus.CANCELLED

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
        return client.patch(url_for("pro_public_api_v2.cancel_collective_booking", booking_id=booking_id))
