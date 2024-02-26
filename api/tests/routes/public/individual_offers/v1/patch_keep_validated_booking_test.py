import datetime

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories

from . import utils


pytestmark = pytest.mark.usefixtures("db_session")


class PatchKeepBookingByTokenReturns204Test:
    def test_key_has_rights_and_regular_product_offer(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            extraData={"ean": "1234567890123"},
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        product_stock = offers_factories.StockFactory(offer=product_offer, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2),
            stock=product_stock,
            dateUsed=datetime.datetime.utcnow() - datetime.timedelta(days=1),
            status=BookingStatus.USED,
        )
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/keep/token/{booking.token.lower()}",
        )
        assert response.status_code == 204
        assert booking.status is BookingStatus.CONFIRMED


class PatchKeepBookingByTokenReturns401Test:
    def test_when_user_no_api_key(self, client):
        response = client.patch("/public/bookings/v1/use/token/TOKEN")
        assert response.status_code == 401

    def test_when_user_wrong_api_key(self, client):
        response = client.patch(
            "/public/bookings/v1/keep/token/TOKEN", headers={"Authorization": "Bearer WrongApiKey1234567"}
        )
        assert response.status_code == 401


class PatchKeepBookingByTokenReturns403Test:
    def test_when_booking_is_refunded(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            extraData={"ean": "1234567890123"},
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        product_stock = offers_factories.StockFactory(offer=product_offer, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2),
            stock=product_stock,
            dateUsed=datetime.datetime.utcnow() - datetime.timedelta(days=1),
            status=BookingStatus.REIMBURSED,
        )
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/keep/token/{booking.token.lower()}",
        )
        assert response.status_code == 403
        assert response.json == {"payment": "This booking has been reimbursed"}
        assert booking.status is BookingStatus.REIMBURSED

    def test_when_booking_is_not_used(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            extraData={"ean": "1234567890123"},
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        product_stock = offers_factories.StockFactory(offer=product_offer, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2),
            stock=product_stock,
            dateUsed=datetime.datetime.utcnow() - datetime.timedelta(days=1),
            status=BookingStatus.CONFIRMED,
        )
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/keep/token/{booking.token.lower()}",
        )
        assert response.status_code == 403
        assert response.json == {"booking": "This booking has not been used"}
        assert booking.status is BookingStatus.CONFIRMED

    def test_when_stock_is_event_and_booking_is_not_confirmed_yet(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue)
        event_stock = offers_factories.StockFactory(
            offer=event_offer, bookingLimitDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=10)
        )
        booking = bookings_factories.BookingFactory(
            stock=event_stock,
            status=BookingStatus.CONFIRMED,
            dateCreated=datetime.datetime.utcnow() + datetime.timedelta(hours=10),
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/keep/token/{booking.token.lower()}",
        )

        assert response.status_code == 403
        assert response.json == {"booking": "This booking has not been used"}


class PatchKeepBookingByTokenReturns404Test:
    def test_missing_token(self, client):
        response = client.patch("/public/bookings/v1/use/token/")
        assert response.status_code == 404

    def test_key_has_no_rights_and_regular_offer(self, client):
        utils.create_offerer_provider_linked_to_venue()
        venue = offerers_factories.VenueFactory()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        product_stock = offers_factories.StockFactory(offer=product_offer, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2),
            stock=product_stock,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/keep/token/{booking.token.lower()}",
        )
        assert response.status_code == 404
        assert response.json == {"global": "This countermark cannot be found"}

    def test_venue_provider_inactive(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue(is_venue_provider_active=False)
        product_offer = offers_factories.ThingOfferFactory(venue=venue)
        product_stock = offers_factories.StockFactory(offer=product_offer)
        booking = bookings_factories.BookingFactory(stock=product_stock)
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/keep/token/{booking.token.lower()}",
        )
        assert response.status_code == 404


class PatchKeepBookingByTokenReturns410Test:
    def test_when_booking_has_activation_code(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.DigitalOfferFactory(venue=venue)

        product_stock = offers_factories.StockWithActivationCodesFactory(offer=product_offer)
        booking = bookings_factories.UsedBookingFactory(stock=product_stock)
        offers_factories.ActivationCodeFactory(stock=product_stock, booking=booking)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/keep/token/{booking.token.lower()}",
        )

        assert response.status_code == 403
        assert response.json == {"booking": "This booking has validation codes, and cannot be marked as unused"}

    def test_when_booking_is_cancelled(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(venue=venue)
        product_stock = offers_factories.StockFactory(offer=product_offer)
        booking = bookings_factories.CancelledBookingFactory(stock=product_stock)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/keep/token/{booking.token.lower()}",
        )

        assert response.status_code == 410
        assert response.json == {"booking": "This booking has been cancelled"}
