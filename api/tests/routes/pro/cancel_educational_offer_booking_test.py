import pytest

from pcapi.core.bookings import factories as booking_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.models import CollectiveBookingStatus
import pcapi.core.educational.testing as adage_api_testing
from pcapi.core.offerers import factories as offerer_factories
from pcapi.core.offers import factories as offer_factories
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as user_factories
from pcapi.routes.adage.v1.serialization.prebooking import serialize_educational_booking
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


@override_settings(ADAGE_API_URL="https://adage_base_url")
@override_settings(ADAGE_API_KEY="adage-api-key")
class Returns204Test:
    def test_cancel_pending_booking(self, client):
        user = user_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offer_factories.UserOffererFactory(user=user, offerer=offerer)

        educational_booking = booking_factories.PendingEducationalBookingFactory(
            stock__offer__venue__managingOfferer=offerer
        )

        offer_id = humanize(educational_booking.stock.offer.id)
        client = client.with_session_auth(user.email)
        response = client.patch(f"/offers/{offer_id}/cancel_booking")

        assert response.status_code == 204
        assert educational_booking.status == BookingStatus.CANCELLED

        expected_payload = serialize_educational_booking(educational_booking.educationalBooking)
        assert len(adage_api_testing.adage_requests) == 1
        assert adage_api_testing.adage_requests[0]["sent_data"] == expected_payload
        assert adage_api_testing.adage_requests[0]["url"] == "https://adage_base_url/v1/prereservation-annule"

    def test_cancel_confirmed_booking(self, client):
        user = user_factories.AdminFactory()
        educational_booking = booking_factories.EducationalBookingFactory()
        offer_id = humanize(educational_booking.stock.offer.id)

        client = client.with_session_auth(user.email)
        response = client.patch(f"/offers/{offer_id}/cancel_booking")

        assert response.status_code == 204
        assert educational_booking.status == BookingStatus.CANCELLED

        expected_payload = serialize_educational_booking(educational_booking.educationalBooking)
        assert len(adage_api_testing.adage_requests) == 1
        assert adage_api_testing.adage_requests[0]["sent_data"] == expected_payload
        assert adage_api_testing.adage_requests[0]["url"] == "https://adage_base_url/v1/prereservation-annule"

    def test_cancel_collective_booking_if_pending(self, client):
        user = user_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offer_factories.UserOffererFactory(user=user, offerer=offerer)

        booking = booking_factories.PendingEducationalBookingFactory(stock__offer__venue__managingOfferer=offerer)
        collective_booking = CollectiveBookingFactory(
            status=CollectiveBookingStatus.PENDING,
            venue__managingOfferer=offerer,
            collectiveStock__collectiveOffer__offerId=booking.stock.offer.id,
        )

        offer_id = humanize(booking.stock.offer.id)
        client = client.with_session_auth(user.email)
        response = client.patch(f"/offers/{offer_id}/cancel_booking")

        assert response.status_code == 204
        assert booking.status == BookingStatus.CANCELLED
        assert collective_booking.status == CollectiveBookingStatus.CANCELLED

    def test_cancel_collective_booking_if_confirmed(self, client):
        user = user_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offer_factories.UserOffererFactory(user=user, offerer=offerer)

        booking = booking_factories.PendingEducationalBookingFactory(stock__offer__venue__managingOfferer=offerer)
        collective_booking = CollectiveBookingFactory(
            status=CollectiveBookingStatus.CONFIRMED,
            venue__managingOfferer=offerer,
            collectiveStock__collectiveOffer__offerId=booking.stock.offer.id,
        )

        offer_id = humanize(booking.stock.offer.id)
        client = client.with_session_auth(user.email)
        response = client.patch(f"/offers/{offer_id}/cancel_booking")

        assert response.status_code == 204
        assert booking.status == BookingStatus.CANCELLED
        assert collective_booking.status == CollectiveBookingStatus.CANCELLED


@override_settings(ADAGE_API_URL="https://adage_base_url")
@override_settings(ADAGE_API_KEY="adage-api-key")
class Returns404Test:
    @override_settings(ADAGE_API_URL="https://adage_base_url")
    @override_settings(ADAGE_API_KEY="adage-api-key")
    def test_no_educational_offer_found(self, client):
        user = user_factories.AdminFactory()
        offer = offer_factories.OfferFactory()
        offer_id = humanize(offer.id)

        client = client.with_session_auth(user.email)
        response = client.patch(f"/offers/{offer_id}/cancel_booking")

        assert response.status_code == 404
        assert response.json == {
            "code": "NO_EDUCATIONAL_OFFER_FOUND",
            "message": "No educational offer has been found with this id",
        }
        assert len(adage_api_testing.adage_requests) == 0

    @override_settings(ADAGE_API_URL="https://adage_base_url")
    @override_settings(ADAGE_API_KEY="adage-api-key")
    def test_no_active_stock_found(self, client):
        user = user_factories.AdminFactory()
        stock = offer_factories.EducationalEventStockFactory(isSoftDeleted=True)
        offer_id = humanize(stock.offer.id)

        client = client.with_session_auth(user.email)
        response = client.patch(f"/offers/{offer_id}/cancel_booking")

        assert response.status_code == 404
        assert response.json == {
            "code": "NO_ACTIVE_STOCK_FOUND",
            "message": "No active stock has been found with this id",
        }
        assert len(adage_api_testing.adage_requests) == 0


@override_settings(ADAGE_API_URL="https://adage_base_url")
@override_settings(ADAGE_API_KEY="adage-api-key")
class Returns403Test:
    def test_user_does_not_have_access_to_offerer(self, client):
        user = user_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offer_factories.UserOffererFactory(user=user, offerer=offerer, validationToken="validationToken")

        offer = offer_factories.EducationalEventOfferFactory(venue__managingOfferer=offerer)

        offer_id = humanize(offer.id)
        client = client.with_session_auth(user.email)
        response = client.patch(f"/offers/{offer_id}/cancel_booking")

        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
        }
        assert len(adage_api_testing.adage_requests) == 0


@override_settings(ADAGE_API_URL="https://adage_base_url")
@override_settings(ADAGE_API_KEY="adage-api-key")
class Returns400Test:
    def test_offer_has_multiple_active_stocks(self, client):
        user = user_factories.AdminFactory()
        offer = offer_factories.EducationalEventOfferFactory()
        stock1 = offer_factories.EducationalEventStockFactory(offer=offer)
        offer_factories.EducationalEventStockFactory(offer=offer)
        educational_booking = booking_factories.PendingEducationalBookingFactory(stock=stock1)

        offer_id = humanize(offer.id)
        client = client.with_session_auth(user.email)
        response = client.patch(f"/offers/{offer_id}/cancel_booking")

        assert response.status_code == 400
        assert educational_booking.status == BookingStatus.PENDING
        assert response.json == {
            "code": "MULTIPLE_STOCKS",
            "message": "This educational offer has multiple active stocks",
        }
        assert len(adage_api_testing.adage_requests) == 0

    def test_offer_has_no_booking_to_cancel(self, client):
        user = user_factories.AdminFactory()
        educational_booking = booking_factories.RefusedEducationalBookingFactory()
        offer_id = humanize(educational_booking.stock.offer.id)

        client = client.with_session_auth(user.email)
        response = client.patch(f"/offers/{offer_id}/cancel_booking")

        assert response.status_code == 400
        assert response.json == {"code": "NO_BOOKING", "message": "This educational offer has no booking to cancel"}
        assert len(adage_api_testing.adage_requests) == 0

    def test_offer_has_no_booking_to_cancel_because_used(self, client):
        user = user_factories.AdminFactory()
        stock = offer_factories.EducationalThingStockFactory()
        educational_booking = booking_factories.UsedEducationalBookingFactory(stock=stock)
        offer_id = humanize(educational_booking.stock.offer.id)

        client = client.with_session_auth(user.email)
        response = client.patch(f"/offers/{offer_id}/cancel_booking")

        assert response.status_code == 400
        assert response.json == {"code": "NO_BOOKING", "message": "This educational offer has no booking to cancel"}
        assert len(adage_api_testing.adage_requests) == 0
