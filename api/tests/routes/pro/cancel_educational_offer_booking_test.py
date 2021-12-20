import pytest

from pcapi.core.bookings import factories as booking_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offerers import factories as offerer_factories
from pcapi.core.offers import factories as offer_factories
from pcapi.core.users import factories as user_factories


pytestmark = pytest.mark.usefixtures("db_session")


class Returns204Test:
    def test_cancel_pending_booking(self, client):
        user = user_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offer_factories.UserOffererFactory(user=user, offerer=offerer)

        educational_booking = booking_factories.PendingEducationalBookingFactory(
            stock__offer__venue__managingOfferer=offerer
        )

        offer_id = educational_booking.stock.offer.id
        client = client.with_session_auth(user.email)
        response = client.patch(f"/offers/{offer_id}/cancel_booking")

        assert response.status_code == 204
        assert educational_booking.status == BookingStatus.CANCELLED

    def test_cancel_confirmed_booking(self, client):
        user = user_factories.AdminFactory()
        educational_booking = booking_factories.EducationalBookingFactory()
        offer_id = educational_booking.stock.offer.id

        client = client.with_session_auth(user.email)
        response = client.patch(f"/offers/{offer_id}/cancel_booking")

        assert response.status_code == 204
        assert educational_booking.status == BookingStatus.CANCELLED


class Returns404Test:
    def test_no_educational_offer_found(self, client):
        user = user_factories.AdminFactory()
        offer = offer_factories.OfferFactory()
        offer_id = offer.id

        client = client.with_session_auth(user.email)
        response = client.patch(f"/offers/{offer_id}/cancel_booking")

        assert response.status_code == 404
        assert response.json == {"offerId": "No educational offer has been found with this id"}

    def test_no_active_stock_found(self, client):
        user = user_factories.AdminFactory()
        stock = offer_factories.EducationalEventStockFactory(isSoftDeleted=True)
        offer_id = stock.offer.id

        client = client.with_session_auth(user.email)
        response = client.patch(f"/offers/{offer_id}/cancel_booking")

        assert response.status_code == 404
        assert response.json == {"offerId": "No active stock has been found with this id"}


class Returns403Test:
    def test_user_does_not_have_access_to_offerer(self, client):
        user = user_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offer_factories.UserOffererFactory(user=user, offerer=offerer, validationToken="validationToken")

        offer = offer_factories.EducationalEventOfferFactory(venue__managingOfferer=offerer)

        offer_id = offer.id
        client = client.with_session_auth(user.email)
        response = client.patch(f"/offers/{offer_id}/cancel_booking")

        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
        }


class Returns400Test:
    def test_offer_has_multiple_active_stocks(self, client):
        user = user_factories.AdminFactory()
        offer = offer_factories.EducationalEventOfferFactory()
        stock1 = offer_factories.EducationalEventStockFactory(offer=offer)
        offer_factories.EducationalEventStockFactory(offer=offer)
        educational_booking = booking_factories.PendingEducationalBookingFactory(stock=stock1)

        offer_id = offer.id
        client = client.with_session_auth(user.email)
        response = client.patch(f"/offers/{offer_id}/cancel_booking")

        assert response.status_code == 400
        assert educational_booking.status == BookingStatus.PENDING
        assert response.json == {"offerId": "This educational offer has multiple active stocks"}

    def test_offer_has_no_booking_to_cancel(self, client):
        user = user_factories.AdminFactory()
        educational_booking = booking_factories.RefusedEducationalBookingFactory()
        offer_id = educational_booking.stock.offer.id

        client = client.with_session_auth(user.email)
        response = client.patch(f"/offers/{offer_id}/cancel_booking")

        assert response.status_code == 400
        assert response.json == {"offerId": "This educational offer has no booking to cancel"}
