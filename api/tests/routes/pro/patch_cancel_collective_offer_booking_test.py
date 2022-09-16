import pytest

from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.models import CollectiveBookingStatus
import pcapi.core.educational.testing as adage_api_testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as user_factories
from pcapi.routes.adage.v1.serialization.prebooking import serialize_collective_booking
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


@override_settings(ADAGE_API_URL="https://adage_base_url")
@override_settings(ADAGE_API_KEY="adage-api-key")
class Returns204Test:
    def test_cancel_pending_booking(self, client):
        user = user_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        collective_booking = CollectiveBookingFactory(
            status=CollectiveBookingStatus.PENDING, collectiveStock__collectiveOffer__venue__managingOfferer=offerer
        )

        offer_id = humanize(collective_booking.collectiveStock.collectiveOffer.id)
        client = client.with_session_auth(user.email)
        response = client.patch(f"/collective/offers/{offer_id}/cancel_booking")

        assert response.status_code == 204
        assert collective_booking.status == CollectiveBookingStatus.CANCELLED

        expected_payload = serialize_collective_booking(collective_booking)
        assert len(adage_api_testing.adage_requests) == 1
        assert adage_api_testing.adage_requests[0]["sent_data"] == expected_payload
        assert adage_api_testing.adage_requests[0]["url"] == "https://adage_base_url/v1/prereservation-annule"

    def test_cancel_confirmed_booking(self, client):
        user = user_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        collective_booking = CollectiveBookingFactory(
            status=CollectiveBookingStatus.CONFIRMED, collectiveStock__collectiveOffer__venue__managingOfferer=offerer
        )

        offer_id = humanize(collective_booking.collectiveStock.collectiveOffer.id)
        client = client.with_session_auth(user.email)
        response = client.patch(f"/collective/offers/{offer_id}/cancel_booking")

        assert response.status_code == 204
        assert collective_booking.status == CollectiveBookingStatus.CANCELLED

        expected_payload = serialize_collective_booking(collective_booking)
        assert len(adage_api_testing.adage_requests) == 1
        assert adage_api_testing.adage_requests[0]["sent_data"] == expected_payload
        assert adage_api_testing.adage_requests[0]["url"] == "https://adage_base_url/v1/prereservation-annule"


class Returns404Test:
    def test_no_collective_offer_found(self, client):
        user = user_factories.AdminFactory()
        offer_id = humanize(123789654)

        client = client.with_session_auth(user.email)
        response = client.patch(f"/collective/offers/{offer_id}/cancel_booking")

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
        offerers_factories.UserOffererFactory(user=user, offerer=offerer, validationToken="validationToken")

        offer = CollectiveOfferFactory(venue__managingOfferer=offerer)

        offer_id = humanize(offer.id)
        client = client.with_session_auth(user.email)
        response = client.patch(f"/collective/offers/{offer_id}/cancel_booking")

        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
        }
        assert len(adage_api_testing.adage_requests) == 0


class Returns400Test:
    def test_offer_has_no_booking_to_cancel(self, client):
        user = user_factories.AdminFactory()
        educational_booking = CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED)
        offer_id = humanize(educational_booking.collectiveStock.collectiveOffer.id)

        client = client.with_session_auth(user.email)
        response = client.patch(f"/collective/offers/{offer_id}/cancel_booking")

        assert response.status_code == 400
        assert response.json == {"code": "NO_BOOKING", "message": "This collective offer has no booking to cancel"}
        assert len(adage_api_testing.adage_requests) == 0

    def test_booking_is_already_used(self, client):
        user = user_factories.AdminFactory()
        collective_booking = CollectiveBookingFactory(status=CollectiveBookingStatus.USED)
        offer_id = humanize(collective_booking.collectiveStock.collectiveOffer.id)

        client = client.with_session_auth(user.email)
        response = client.patch(f"/collective/offers/{offer_id}/cancel_booking")

        assert response.status_code == 400
        assert response.json == {"code": "NO_BOOKING", "message": "This collective offer has no booking to cancel"}
        assert len(adage_api_testing.adage_requests) == 0

    def test_booking_is_already_reimbursed(self, client):
        user = user_factories.AdminFactory()
        collective_booking = CollectiveBookingFactory(status=CollectiveBookingStatus.REIMBURSED)
        offer_id = humanize(collective_booking.collectiveStock.collectiveOffer.id)

        client = client.with_session_auth(user.email)
        response = client.patch(f"/collective/offers/{offer_id}/cancel_booking")

        assert response.status_code == 400
        assert response.json == {"code": "NO_BOOKING", "message": "This collective offer has no booking to cancel"}
        assert len(adage_api_testing.adage_requests) == 0
