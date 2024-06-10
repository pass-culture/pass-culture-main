import datetime

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core import testing
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.utils import date as date_utils

from . import utils


pytestmark = pytest.mark.usefixtures("db_session")


class GetBookingByTokenReturns200Test:
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
            user__postalCode="75001",
            stock=product_stock,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(9):
            response = client.get(
                f"/public/bookings/v1/token/{booking.token.lower()}",
            )
            assert response.status_code == 200
            assert response.json == {
                "confirmationDate": date_utils.format_into_utc_date(booking.cancellationLimitDate),
                "creationDate": date_utils.format_into_utc_date(booking.dateCreated),
                "id": booking.id,
                "offerEan": "1234567890123",
                "offerId": product_offer.id,
                "offerName": product_offer.name,
                "price": finance_utils.to_eurocents(booking.amount),
                "status": "CONFIRMED",
                "priceCategoryId": None,
                "priceCategoryLabel": None,
                "quantity": booking.quantity,
                "stockId": product_stock.id,
                "userBirthDate": date_utils.isoformat(booking.user.birth_date),
                "userEmail": booking.user.email,
                "venueAddress": venue.street,
                "venueDepartementCode": venue.departementCode,
                "venueId": venue.id,
                "venueName": venue.name,
                "userFirstName": "Jeanne",
                "userLastName": "Doux",
                "userPhoneNumber": "+33101010101",
                "userPostalCode": "75001",
            }

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
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2),
            user__postalCode="69100",
            stock=event_stock,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(11):
            response = client.get(
                f"/public/bookings/v1/token/{booking.token.lower()}",
            )

            assert response.status_code == 200
            assert response.json == {
                "confirmationDate": date_utils.format_into_utc_date(booking.cancellationLimitDate),
                "creationDate": date_utils.format_into_utc_date(booking.dateCreated),
                "id": booking.id,
                "offerEan": None,
                "offerId": event_offer.id,
                "offerName": event_offer.name,
                "price": finance_utils.to_eurocents(booking.amount),
                "status": "CONFIRMED",
                "priceCategoryId": booking.stock.priceCategory.id,
                "priceCategoryLabel": booking.stock.priceCategory.label,
                "quantity": booking.quantity,
                "stockId": event_stock.id,
                "userBirthDate": date_utils.isoformat(booking.user.birth_date),
                "userEmail": booking.user.email,
                "venueAddress": venue.street,
                "venueDepartementCode": venue.departementCode,
                "venueId": venue.id,
                "venueName": venue.name,
                "userFirstName": "Jeanne",
                "userLastName": "Doux",
                "userPhoneNumber": "+33101010101",
                "userPostalCode": "69100",
            }


class GetBookingByTokenReturns401Test:
    def test_when_user_no_api_key(self, client):
        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(1):
            response = client.get("/public/bookings/v1/token/TOKEN")

            assert response.status_code == 401

    def test_when_user_wrong_api_key(self, client):
        with testing.assert_num_queries(1):
            response = client.get(
                "/public/bookings/v1/token/TOKEN", headers={"Authorization": "Bearer WrongApiKey1234567"}
            )
            assert response.status_code == 401


class GetBookingByTokenReturns403Test:
    def test_when_booking_not_confirmed(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        next_week = datetime.datetime.utcnow() + datetime.timedelta(weeks=1)

        offer = offers_factories.ThingOfferFactory(venue=venue)
        stock = offers_factories.StockFactory(offer=offer, beginningDatetime=next_week)
        booking = bookings_factories.BookingFactory(stock=stock)

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(7):
            response = client.get(
                f"/public/bookings/v1/token/{booking.token}",
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

        offer = offers_factories.ThingOfferFactory(venue=venue)
        stock = offers_factories.StockFactory(offer=offer)
        booking = bookings_factories.ReimbursedBookingFactory(stock=stock)

        # When
        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(4):
            response = client.get(f"/public/bookings/v1/token/{booking.token}")

            # Then
            assert response.status_code == 403
            assert response.json == {"payment": "This booking has already been reimbursed"}


class GetBookingByTokenReturns404Test:
    def test_missing_token(self, client):
        with testing.assert_num_queries(0):
            response = client.get("/public/bookings/v1/token/")
            assert response.status_code == 404

    def test_inactive_venue_provider(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue(is_venue_provider_active=False)
        product_offer = offers_factories.ThingOfferFactory(venue=venue)
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        product_stock = offers_factories.StockFactory(offer=product_offer, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(stock=product_stock)

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(4):
            response = client.get(
                f"/public/bookings/v1/token/{booking.token.lower()}",
            )

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

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(4):
            response = client.get(
                f"/public/bookings/v1/token/{booking.token.lower()}",
            )
            assert response.status_code == 404
            assert response.json == {"global": "This countermark cannot be found"}


class GetBookingByTokenReturns410Test:
    def test_when_booking_is_already_validated(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(venue=venue)
        product_stock = offers_factories.StockFactory(offer=product_offer)
        booking = bookings_factories.UsedBookingFactory(stock=product_stock)

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(5):
            response = client.get(
                f"/public/bookings/v1/token/{booking.token.lower()}",
            )

            assert response.status_code == 410
            assert response.json == {"booking": "This booking has already been validated"}

    def test_when_booking_is_cancelled(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(venue=venue)
        product_stock = offers_factories.StockFactory(offer=product_offer)
        booking = bookings_factories.CancelledBookingFactory(stock=product_stock)

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(5):
            response = client.get(
                f"/public/bookings/v1/token/{booking.token.lower()}",
            )

            assert response.status_code == 410
            assert response.json == {"booking": "This booking has been cancelled"}
