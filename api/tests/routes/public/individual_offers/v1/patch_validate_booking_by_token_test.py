import datetime

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.utils import date as date_utils

from . import utils


class ValidateBookingByTokenReturns200Test:
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
            venue=venue,
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2),
            stock=product_stock,
        )
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/use/token/{booking.token.lower()}",
        )
        assert response.status_code == 204
        assert booking.is_used_or_reimbursed is True

    def test_key_has_rights_and_regular_event_offer(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        event_stock = offers_factories.EventStockFactory(offer=event_offer, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(
            venue=venue,
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2),
            stock=event_stock,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/use/token/{booking.token.lower()}",
        )

        assert response.status_code == 204
        assert booking.is_used_or_reimbursed is True


class PatchBookingByTokenReturns401Test:
    def test_when_user_no_api_key(self, client):
        response = client.patch("/public/bookings/v1/use/token/TOKEN")
        assert response.status_code == 401

    def test_when_user_wrong_api_key(self, client):
        response = client.patch(
            "/public/bookings/v1/use/token/TOKEN", headers={"Authorization": "Bearer WrongApiKey1234567"}
        )
        assert response.status_code == 401


class PatchBookingByTokenReturns403Test:
    def test_when_booking_not_confirmed(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        next_week = datetime.datetime.utcnow() + datetime.timedelta(weeks=1)

        offer = offers_factories.ThingOfferFactory(
            venue=venue,
        )
        stock = offers_factories.StockFactory(offer=offer, beginningDatetime=next_week)
        booking = bookings_factories.BookingFactory(stock=stock)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/use/token/{booking.token}",
        )

        cancellation_limit_date = datetime.datetime.strftime(
            date_utils.utc_datetime_to_department_timezone(
                booking.cancellationLimitDate, booking.venue.departementCode
            ),
            "%d/%m/%Y à %H:%M",
        )

        assert response.json == {
            "booking": f"Vous pourrez valider cette contremarque à partir du {cancellation_limit_date}, une fois le délai d’annulation passé."
        }
        assert response.status_code == 403

    def test_when_booking_is_refunded(self, client):
        # Given
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        offer = offers_factories.ThingOfferFactory(
            venue=venue,
        )
        stock = offers_factories.StockFactory(offer=offer)
        payment = finance_factories.PaymentFactory(booking__stock=stock)

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/use/token/{payment.booking.token}",
        )

        # Then
        assert response.status_code == 403
        assert response.json == {"payment": "This booking has already been reimbursed"}


class PatchBookingByTokenReturns404Test:
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
            venue=venue,
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2),
            stock=product_stock,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/use/token/{booking.token.lower()}",
        )
        assert response.status_code == 404
        assert response.json == {"global": "This countermark cannot be found"}


class PatchBookingByTokenReturns410Test:
    def test_when_booking_is_already_validated(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
        )
        product_stock = offers_factories.StockFactory(offer=product_offer)
        booking = bookings_factories.UsedBookingFactory(stock=product_stock)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/use/token/{booking.token.lower()}",
        )

        assert response.status_code == 410
        assert response.json == {"booking": "This booking has already been validated"}

    def test_when_booking_is_cancelled(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
        )
        product_stock = offers_factories.StockFactory(offer=product_offer)
        booking = bookings_factories.CancelledBookingFactory(stock=product_stock)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/bookings/v1/use/token/{booking.token.lower()}",
        )

        assert response.status_code == 410
        assert response.json == {"booking": "This booking has been canceled"}
