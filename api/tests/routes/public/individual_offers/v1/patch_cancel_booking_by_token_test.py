import datetime

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories

from .endpoints_test import create_offerer_provider_linked_to_venue


pytestmark = pytest.mark.usefixtures("db_session")


class CancelBookingByTokenReturns200Test:
    def test_key_has_rights_and_regular_product_offer(self, client):
        venue, _ = create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            extraData={"ean": "1234567890123"},
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        product_stock = offers_factories.StockFactory(offer=product_offer, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(
            venue=venue,
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2),
            stock=product_stock,
        )
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/cancel/token/{booking.token.lower()}",
        )
        assert response.status_code == 204
        assert booking.status is BookingStatus.CANCELLED

    def test_key_has_rights_and_regular_event_offer(self, client):
        venue, _ = create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        in_3_days = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        event_stock = offers_factories.EventStockFactory(offer=event_offer, beginningDatetime=in_3_days)
        booking = bookings_factories.BookingFactory(
            venue=venue,
            dateCreated=yesterday,
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2),
            stock=event_stock,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/cancel/token/{booking.token.lower()}",
        )

        assert response.status_code == 204
        assert booking.status == BookingStatus.CANCELLED


class PatchBookingByTokenReturns401Test:
    def test_when_user_no_api_key(self, client):
        response = client.patch("/public/bookings/v1/cancel/token/TOKEN")
        assert response.status_code == 401

    def test_when_user_wrong_api_key(self, client):
        response = client.patch(
            "/public/bookings/v1/cancel/token/TOKEN", headers={"Authorization": "Bearer WrongApiKey1234567"}
        )
        assert response.status_code == 401


class PatchBookingByTokenReturns403Test:
    def test_when_booking_event_in_less_than_48_hours(self, client):
        venue, _ = create_offerer_provider_linked_to_venue()
        tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)

        offer = offers_factories.EventOfferFactory(
            venue=venue,
        )
        stock = offers_factories.EventStockFactory(offer=offer, beginningDatetime=tomorrow)
        booking = bookings_factories.BookingFactory(stock=stock)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/cancel/token/{booking.token}",
        )

        assert response.json == {"booking": "This booking cannot be canceled anymore"}
        assert response.status_code == 403

    def test_when_cancelling_after_48_hours_following_booking_date(self, client):
        venue, _ = create_offerer_provider_linked_to_venue()
        in_2_weeks = datetime.datetime.utcnow() + datetime.timedelta(weeks=1)
        two_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=2)

        offer = offers_factories.EventOfferFactory(
            venue=venue,
        )
        stock = offers_factories.EventStockFactory(offer=offer, beginningDatetime=in_2_weeks)
        booking = bookings_factories.BookingFactory(stock=stock, dateCreated=two_days_ago)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/cancel/token/{booking.token}",
        )

        assert response.json == {"booking": "This booking cannot be canceled anymore"}
        assert response.status_code == 403

    def test_when_cancelling_less_than_48_hours_before_beginning_date(self, client):
        venue, _ = create_offerer_provider_linked_to_venue()
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        in_36_hours = datetime.datetime.utcnow() + datetime.timedelta(hours=36)

        offer = offers_factories.EventOfferFactory(
            venue=venue,
        )
        stock = offers_factories.EventStockFactory(offer=offer, beginningDatetime=in_36_hours)
        booking = bookings_factories.BookingFactory(stock=stock, dateCreated=yesterday)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/cancel/token/{booking.token}",
        )

        assert response.json == {"booking": "This booking cannot be canceled anymore"}
        assert response.status_code == 403

    def test_when_booking_is_refunded(self, client):
        # Given
        venue, _ = create_offerer_provider_linked_to_venue()

        offer = offers_factories.ThingOfferFactory(
            venue=venue,
        )
        stock = offers_factories.StockFactory(offer=offer)
        payment = finance_factories.PaymentFactory(booking__stock=stock)

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/cancel/token/{payment.booking.token}",
        )

        # Then
        assert response.status_code == 403
        assert response.json == {"payment": "This booking has been reimbursed"}


class PatchBookingByTokenReturns404Test:
    def test_missing_token(self, client):
        response = client.patch("/public/bookings/v1/cancel/token/")
        assert response.status_code == 404

    def test_key_has_no_rights_and_regular_offer(self, client):
        create_offerer_provider_linked_to_venue()
        venue = offerers_factories.VenueFactory()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        product_stock = offers_factories.StockFactory(offer=product_offer, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(
            venue=venue,
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2),
            stock=product_stock,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/cancel/token/{booking.token.lower()}",
        )
        assert response.status_code == 404
        assert response.json == {"global": "This countermark cannot be found"}


class PatchBookingByTokenReturns410Test:
    def test_when_booking_is_already_canceled(self, client):
        venue, _ = create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
        )
        product_stock = offers_factories.StockFactory(offer=product_offer)
        booking = bookings_factories.CancelledBookingFactory(stock=product_stock)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/cancel/token/{booking.token.lower()}",
        )

        assert response.status_code == 410
        assert response.json == {"booking": "This booking has already been canceled"}
