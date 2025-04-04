from datetime import datetime

import pytest

from pcapi.core.educational import testing as educational_testing
import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
from pcapi.core.mails import testing as mails_testing
import pcapi.core.offerers.models as offerers_models
from pcapi.models import db

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper
from tests.routes.public.helpers import assert_attribute_does_not_change


pytestmark = pytest.mark.usefixtures("db_session")


class CancelCollectiveBookingTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/v2/collective/bookings/{booking_id}"
    endpoint_method = "patch"
    default_path_params = {"booking_id": 1}

    def setup_base_resource(self, venue: offerers_models.Venue | None = None) -> educational_models.CollectiveBooking:
        venue = venue or self.setup_venue()
        return educational_factories.CollectiveBookingFactory(collectiveStock__collectiveOffer__venue=venue)

    def test_should_raise_404_because_has_no_access_to_venue(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        booking = self.setup_base_resource()
        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(booking_id=booking.id))
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        booking = self.setup_base_resource(venue=venue_provider.venue)
        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(booking_id=booking.id))
        assert response.status_code == 404

    def test_should_raise_401_because_api_key_not_linked_to_provider(self, client):
        num_queries = 2  # Select API key + rollback
        super().test_should_raise_401_because_api_key_not_linked_to_provider(client, num_queries=num_queries)

    def test_cancel_collective_booking(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        booking = self.setup_base_resource(venue=venue_provider.venue)

        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(booking_id=booking.id))
        assert response.status_code == 204

        db.session.refresh(booking)

        assert booking.cancellationReason == educational_models.CollectiveBookingCancellationReasons.PUBLIC_API
        assert booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp(), rel=1)
        assert booking.status == educational_models.CollectiveBookingStatus.CANCELLED

        assert len(educational_testing.adage_requests) == 1
        assert len(mails_testing.outbox) == 1

    @pytest.mark.parametrize(
        "booking_factory,expected_json",
        [
            (
                educational_factories.CancelledCollectiveBookingFactory,
                {"booking": "Impossible d'annuler une réservation déjà annulée"},
            ),
            (
                educational_factories.ReimbursedCollectiveBookingFactory,
                {"booking": "Cette réservation est en train d’être remboursée, il est impossible de l’invalider"},
            ),
            (
                educational_factories.UsedCollectiveBookingFactory,
                {"booking": "Cette réservation a déjà été utilisée et ne peut être annulée"},
            ),
        ],
    )
    def test_should_raise_403_when_status_is_not_confirmed(self, client: TestClient, booking_factory, expected_json):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        booking = booking_factory(collectiveStock__collectiveOffer__venue=venue_provider.venue)

        with assert_attribute_does_not_change(booking, "status"):
            response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(booking_id=booking.id))
            assert response.status_code == 403
            assert response.json == expected_json
