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

    @pytest.mark.parametrize("status", educational_testing.STATUSES_ALLOWING_CANCEL)
    def test_allowed_action(self, client, status):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.create_collective_offer_by_status(status, venue=venue_provider.venue)
        [booking] = offer.collectiveStock.collectiveBookings

        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(booking_id=booking.id))
        assert response.status_code == 204

        db.session.refresh(booking)
        assert booking.cancellationReason == educational_models.CollectiveBookingCancellationReasons.PUBLIC_API
        assert booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp(), rel=1)
        assert booking.status == educational_models.CollectiveBookingStatus.CANCELLED

    def test_cancel_offer_ended(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.EndedCollectiveOfferFactory(venue=venue_provider.venue, booking_is_confirmed=True)
        [booking] = offer.collectiveStock.collectiveBookings

        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(booking_id=booking.id))
        assert response.status_code == 204

        db.session.refresh(booking)
        assert booking.cancellationReason == educational_models.CollectiveBookingCancellationReasons.PUBLIC_API
        assert booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp(), rel=1)
        assert booking.status == educational_models.CollectiveBookingStatus.CANCELLED

    @pytest.mark.parametrize(
        "status",
        (
            educational_models.CollectiveOfferDisplayedStatus.ENDED,
            educational_models.CollectiveOfferDisplayedStatus.EXPIRED,
            educational_models.CollectiveOfferDisplayedStatus.REIMBURSED,
        ),
    )
    def test_cancel_unallowed_action(self, client, status):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.create_collective_offer_by_status(status, venue=venue_provider.venue)
        [booking] = offer.collectiveStock.collectiveBookings

        with assert_attribute_does_not_change(booking, "status"):
            response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(booking_id=booking.id))

        assert response.status_code == 403
        assert response.json == {
            "booking": f"Impossible d'annuler cette réservation car le statut de l'offre est {status.value}"
        }

    def test_cancel_offer_cancelled(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.CancelledWithBookingCollectiveOfferFactory(venue=venue_provider.venue)
        [booking] = offer.collectiveStock.collectiveBookings

        with assert_attribute_does_not_change(booking, "status"):
            response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(booking_id=booking.id))

        assert response.status_code == 403
        assert response.json == {
            "booking": "Impossible d'annuler cette réservation car le statut de l'offre est CANCELLED"
        }

    def test_cancel_offer_ended_booking_used(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.EndedCollectiveOfferFactory(venue=venue_provider.venue)
        [booking] = offer.collectiveStock.collectiveBookings

        with assert_attribute_does_not_change(booking, "status"):
            response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(booking_id=booking.id))

        assert response.status_code == 403
        assert response.json == {"booking": "Impossible d'annuler cette réservation car le statut de l'offre est ENDED"}

    def test_cancel_offer_archived(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.ArchivedReimbursedCollectiveOfferFactory(venue=venue_provider.venue)
        [booking] = offer.collectiveStock.collectiveBookings

        with assert_attribute_does_not_change(booking, "status"):
            response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(booking_id=booking.id))

        assert response.status_code == 403
        assert response.json == {
            "booking": "Impossible d'annuler cette réservation car le statut de l'offre est ARCHIVED"
        }
