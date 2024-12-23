import pytest

from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.educational import testing as adage_api_testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.core.token import SecureToken
from pcapi.core.token.serialization import ConnectAsInternalModel
from pcapi.core.users import factories as user_factories
from pcapi.routes.adage.v1.serialization.prebooking import serialize_collective_booking

from tests.conftest import TestClient


STATUSES_ALLOWING_CANCEL = (
    models.CollectiveOfferDisplayedStatus.PREBOOKED,
    models.CollectiveOfferDisplayedStatus.BOOKED,
)

STATUSES_NOT_ALLOWING_CANCEL = tuple(
    set(models.CollectiveOfferDisplayedStatus)
    - {*STATUSES_ALLOWING_CANCEL, models.CollectiveOfferDisplayedStatus.INACTIVE}
)

pytestmark = pytest.mark.usefixtures("db_session")


@override_settings(ADAGE_API_URL="https://adage_base_url")
@override_settings(ADAGE_API_KEY="adage-api-key")
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
        response = client.patch(f"/pro/collective/offers/{offer_id}/cancel_booking")

        assert response.status_code == 204
        assert collective_booking.status == models.CollectiveBookingStatus.CANCELLED

        expected_payload = serialize_collective_booking(collective_booking)
        assert len(adage_api_testing.adage_requests) == 1
        assert adage_api_testing.adage_requests[0]["sent_data"] == expected_payload
        assert adage_api_testing.adage_requests[0]["url"] == "https://adage_base_url/v1/prereservation-annule"

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
        response = client.patch(f"/pro/collective/offers/{offer_id}/cancel_booking")

        assert response.status_code == 204
        assert collective_booking.status == models.CollectiveBookingStatus.CANCELLED
        assert collective_booking.cancellationUser == user

        expected_payload = serialize_collective_booking(collective_booking)
        assert len(adage_api_testing.adage_requests) == 1
        assert adage_api_testing.adage_requests[0]["sent_data"] == expected_payload
        assert adage_api_testing.adage_requests[0]["url"] == "https://adage_base_url/v1/prereservation-annule"

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

        response_token = client.get(f"/pro/users/connect-as/{secure_token.token}")
        assert response_token.status_code == 302

        offer_id = collective_booking.collectiveStock.collectiveOffer.id
        response = client.patch(f"/pro/collective/offers/{offer_id}/cancel_booking")

        assert response.status_code == 204
        assert collective_booking.status == models.CollectiveBookingStatus.CANCELLED
        assert collective_booking.cancellationUser == admin

    @override_features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    @pytest.mark.parametrize("status", STATUSES_ALLOWING_CANCEL)
    def test_cancel_allowed_action(self, client, status):
        offer = factories.create_collective_offer_by_status(status)
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth("pro@example.com")
        response = client.patch(f"/pro/collective/offers/{offer.id}/cancel_booking")

        assert response.status_code == 204
        assert offer.collectiveStock.collectiveBookings[0].status == models.CollectiveBookingStatus.CANCELLED

    @override_features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    def test_cancel_ended(self, client):
        offer = factories.EndedCollectiveOfferFactory(booking_is_confirmed=True)
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth("pro@example.com")
        response = client.patch(f"/pro/collective/offers/{offer.id}/cancel_booking")

        assert response.status_code == 204
        assert offer.collectiveStock.collectiveBookings[0].status == models.CollectiveBookingStatus.CANCELLED


class Returns404Test:
    def test_no_collective_offer_found(self, client):
        user = user_factories.UserFactory()
        offer_id = 123789654

        client = client.with_session_auth(user.email)
        response = client.patch(f"/pro/collective/offers/{offer_id}/cancel_booking")

        assert response.status_code == 404
        assert response.json == {
            "code": "NO_COLLECTIVE_OFFER_FOUND",
            "message": "No collective offer has been found with this id",
        }
        assert len(adage_api_testing.adage_requests) == 0


class Returns403Test:
    def test_user_does_not_have_access_to_offerer(self, client):
        user = user_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.NotValidatedUserOffererFactory(user=user, offerer=offerer)

        offer = factories.CollectiveOfferFactory(venue__managingOfferer=offerer)

        offer_id = offer.id
        client = client.with_session_auth(user.email)
        response = client.patch(f"/pro/collective/offers/{offer_id}/cancel_booking")

        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."]
        }
        assert len(adage_api_testing.adage_requests) == 0

    @override_features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    @pytest.mark.parametrize("status", STATUSES_NOT_ALLOWING_CANCEL)
    def test_cancel_unallowed_action(self, client, status):
        offer = factories.create_collective_offer_by_status(status)
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth("pro@example.com")
        response = client.patch(f"/pro/collective/offers/{offer.id}/cancel_booking")

        assert response.status_code == 403
        assert response.json == {
            "code": "CANCEL_NOT_ALLOWED",
            "message": "This collective offer status does not allow cancellation",
        }


class Returns400Test:

    @pytest.mark.parametrize(
        "status",
        [
            models.CollectiveBookingStatus.CANCELLED,
            models.CollectiveBookingStatus.USED,
            models.CollectiveBookingStatus.REIMBURSED,
        ],
    )
    def test_offer_that_cannot_be_cancelled_because_of_status(self, client: TestClient, status):
        user = user_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        educational_booking = factories.CollectiveBookingFactory(
            status=status, collectiveStock__collectiveOffer__venue__managingOfferer=offerer
        )
        offer_id = educational_booking.collectiveStock.collectiveOffer.id

        client = client.with_session_auth(user.email)
        response = client.patch(f"/pro/collective/offers/{offer_id}/cancel_booking")

        assert response.status_code == 400
        assert response.json == {"code": "NO_BOOKING", "message": "This collective offer has no booking to cancel"}
        assert len(adage_api_testing.adage_requests) == 0
