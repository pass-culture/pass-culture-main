from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.bookings import factories as booking_factories
from pcapi.core.offers import factories as offer_factories
from pcapi.core.offers.models import Stock
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    def test_edit_educational_stock(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
        )
        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 204
        edited_stock = Stock.query.get(stock.id)
        assert edited_stock.beginningDatetime == datetime(2022, 1, 17, 22)
        assert edited_stock.bookingLimitDatetime == datetime(2021, 12, 31, 20)
        assert edited_stock.price == 1500
        assert edited_stock.numberOfTickets == 38

    def test_edit_educational_stock_partially(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
        )
        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "totalPrice": 1500,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 204
        edited_stock = Stock.query.get(stock.id)
        assert edited_stock.beginningDatetime == datetime(2022, 1, 17, 22)
        assert edited_stock.bookingLimitDatetime == stock.bookingLimitDatetime
        assert edited_stock.price == 1500
        assert edited_stock.numberOfTickets == 32


class Return403Test:
    def test_edit_educational_stocks_should_not_be_possible_when_user_not_linked_to_offerer(self, app, client):
        stock = offer_factories.EducationalEventStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
            price=1200,
        )
        offer_factories.UserOffererFactory(
            user__email="user@example.com",
        )

        # When
        stock_edition_payload = {
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "totalPrice": 1500,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
        }


class Return400Test:
    def should_not_allow_number_of_tickets_to_be_negative_on_edition(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
        )
        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "numberOfTickets": -10,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        edited_stock = Stock.query.get(stock.id)
        assert edited_stock.numberOfTickets == 32

    def should_not_allow_price_to_be_negative_on_creation(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
        )
        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "totalPrice": -10,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        edited_stock = Stock.query.get(stock.id)
        assert edited_stock.price == 1200

    def should_not_accept_payload_with_bookingLimitDatetime_after_beginningDatetime(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
        )
        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "beginningDatetime": "2021-12-20T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T22:00:00Z",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        edited_stock = Stock.query.get(stock.id)
        assert edited_stock.bookingLimitDatetime == stock.bookingLimitDatetime

    def should_not_edit_stock_when_event_expired(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(beginningDatetime=datetime.utcnow() - timedelta(minutes=1))
        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "totalPrice": 1500,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400

    def should_not_allow_stock_edition_when_numberOfTickets_has_been_set_to_none(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory()
        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "numberOfTickets": None,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"numberOfTickets": ["Le nombre de places ne peut être nul"]}

    def should_not_allow_stock_edition_when_totalPrice_has_been_set_to_none(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory()
        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "totalPrice": None,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"totalPrice": ["Le prix ne peut être nul"]}

    def should_not_allow_stock_edition_when_beginnningDatetime_has_been_set_to_none(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory()
        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "beginningDatetime": None,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"beginningDatetime": ["La date d’évènement ne peut être nulle"]}

    def should_raise_error_when_more_than_one_non_cancelled_bookings_associated_with_stock(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(price=1200, quantity=2, dnBookedQuantity=2)
        booking_factories.EducationalBookingFactory(stock=stock)
        booking_factories.EducationalBookingFactory(stock=stock)

        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "totalPrice": 1500,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {
            "educationalStockEdition": [
                "Plusieurs réservations non annulées portent sur ce stock d'une offre éducationnelle"
            ]
        }
