import pytest

from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.educational import testing
from pcapi.core.educational.serialization.collective_booking import serialize_collective_booking
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.token import SecureToken
from pcapi.core.token.serialization import ConnectAsInternalModel
from pcapi.core.users import factories as user_factories


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.settings(ADAGE_API_URL="https://adage_base_url", ADAGE_API_KEY="adage-api-key")
class Returns204Test:
    def test_cancel_pending_booking(self, client):
        user = user_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        collective_booking = factories.CollectiveBookingFactory(
            status=models.CollectiveBookingStatus.PENDING,
            collectiveStock__collectiveOffer__venue__managingOfferer=offerer,
        )

        offer_id = collective_booking.collectiveStock.collectiveOffer.id
        client = client.with_session_auth(user.email)
        response = client.patch(f"/collective/offers/{offer_id}/cancel_booking")

        assert response.status_code == 204
        assert collective_booking.status == models.CollectiveBookingStatus.CANCELLED

        expected_payload = serialize_collective_booking(collective_booking)
        assert len(testing.adage_requests) == 1
        assert testing.adage_requests[0]["sent_data"] == expected_payload
        assert testing.adage_requests[0]["url"] == "https://adage_base_url/v1/prereservation-annule"

    def test_cancel_confirmed_booking(self, client):
        user = user_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        collective_booking = factories.CollectiveBookingFactory(
            status=models.CollectiveBookingStatus.CONFIRMED,
            collectiveStock__collectiveOffer__venue__managingOfferer=offerer,
        )

        offer_id = collective_booking.collectiveStock.collectiveOffer.id
        client = client.with_session_auth(user.email)
        response = client.patch(f"/collective/offers/{offer_id}/cancel_booking")

        assert response.status_code == 204
        assert collective_booking.status == models.CollectiveBookingStatus.CANCELLED
        assert collective_booking.cancellationUser == user

        expected_payload = serialize_collective_booking(collective_booking)
        assert len(testing.adage_requests) == 1
        assert testing.adage_requests[0]["sent_data"] == expected_payload
        assert testing.adage_requests[0]["url"] == "https://adage_base_url/v1/prereservation-annule"

    def test_cancel_confirmed_booking_user_connect_as(self, client):
        user = user_factories.ProFactory()
        admin = user_factories.AdminFactory(email="admin@example.com")
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        collective_booking = factories.CollectiveBookingFactory(
            status=models.CollectiveBookingStatus.CONFIRMED,
            collectiveStock__collectiveOffer__venue__managingOfferer=offerer,
        )
        expected_redirect_link = "https://example.com"
        secure_token = SecureToken(
            data=ConnectAsInternalModel(
                redirect_link=expected_redirect_link,
                user_id=user.id,
                internal_admin_email=admin.email,
                internal_admin_id=admin.id,
            ).dict(),
        )

        response_token = client.get(f"/users/connect-as/{secure_token.token}")
        assert response_token.status_code == 302

        offer_id = collective_booking.collectiveStock.collectiveOffer.id
        response = client.patch(f"/collective/offers/{offer_id}/cancel_booking")

        assert response.status_code == 204
        assert collective_booking.status == models.CollectiveBookingStatus.CANCELLED
        assert collective_booking.cancellationUser == admin

    @pytest.mark.parametrize("status", testing.STATUSES_ALLOWING_CANCEL)
    def test_cancel_allowed_action(self, client, status):
        offer = factories.create_collective_offer_by_status(status)
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth("pro@example.com")
        response = client.patch(f"/collective/offers/{offer.id}/cancel_booking")

        assert response.status_code == 204
        assert offer.collectiveStock.collectiveBookings[0].status == models.CollectiveBookingStatus.CANCELLED

    def test_cancel_ended(self, client):
        offer = factories.EndedCollectiveOfferConfirmedBookingFactory()
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth("pro@example.com")
        response = client.patch(f"/collective/offers/{offer.id}/cancel_booking")

        assert response.status_code == 204
        assert offer.collectiveStock.collectiveBookings[0].status == models.CollectiveBookingStatus.CANCELLED


class Returns404Test:
    def test_no_collective_offer_found(self, client):
        user = user_factories.UserFactory()
        offer_id = 123789654

        client = client.with_session_auth(user.email)
        response = client.patch(f"/collective/offers/{offer_id}/cancel_booking")

        assert response.status_code == 404
        assert response.json == {
            "code": "NO_COLLECTIVE_OFFER_FOUND",
            "message": "No collective offer has been found with this id",
        }
        assert len(testing.adage_requests) == 0


class Returns403Test:
    def test_user_does_not_have_access_to_offerer(self, client):
        user = user_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.NewUserOffererFactory(user=user, offerer=offerer)

        offer = factories.CollectiveOfferFactory(venue__managingOfferer=offerer)

        offer_id = offer.id
        client = client.with_session_auth(user.email)
        response = client.patch(f"/collective/offers/{offer_id}/cancel_booking")

        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."]
        }
        assert len(testing.adage_requests) == 0

    @pytest.mark.parametrize("status", testing.STATUSES_NOT_ALLOWING_CANCEL)
    def test_cancel_unallowed_action(self, client, status):
        offer = factories.create_collective_offer_by_status(status)
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth("pro@example.com")
        response = client.patch(f"/collective/offers/{offer.id}/cancel_booking")

        assert response.status_code == 403
        assert response.json == {
            "code": "CANCEL_NOT_ALLOWED",
            "message": "This collective offer status does not allow cancellation",
        }
