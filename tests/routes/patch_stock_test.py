from datetime import datetime

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import StockSQLEntity
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns200:
    def when_user_has_editor_rights_on_offerer(self, app):
        # given
        offer = offers_factories.ThingOfferFactory()
        offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        stock = offers_factories.StockFactory(
            offer=offer,
            price=100,
            quantity=10,
        )

        # when
        client = TestClient(app.test_client()).with_auth("user@example.com")
        data = {"price": 20, "quantity": 5}
        response = client.patch(f"/stocks/{humanize(stock.id)}", json=data)

        # then
        assert response.status_code == 200
        stock = StockSQLEntity.query.one()
        assert stock.price == 20
        assert stock.quantity == 5

    def when_beginning_and_booking_limit_datetime_are_updated_for_event(self, app):
        # given
        offer = offers_factories.EventOfferFactory()
        offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        stock = offers_factories.StockFactory(
            offer=offer,
            price=100,
            quantity=10,
        )

        # when
        client = TestClient(app.test_client()).with_auth("user@example.com")
        beginning = datetime(2020, 1, 1, 12, 0, 0)
        booking_limit = datetime(2020, 1, 1, 10, 0, 0)
        data = {
            "price": 20,
            "quantity": 5,
            "beginningDatetime": beginning.isoformat(),
            "bookingLimitDatetime": booking_limit.isoformat(),
        }
        response = client.patch(f"/stocks/{humanize(stock.id)}", json=data)

        # then
        assert response.status_code == 200
        stock = StockSQLEntity.query.one()
        assert stock.price == 20
        assert stock.quantity == 5
        assert stock.beginningDatetime == beginning
        assert stock.bookingLimitDatetime == booking_limit

    def when_user_is_admin(self, app):
        # given
        user = users_factories.UserFactory(canBookFreeOffers=False, isAdmin=True)
        offer = offers_factories.ThingOfferFactory()
        stock = offers_factories.StockFactory(offer=offer, price=100, quantity=10)

        # when
        client = TestClient(app.test_client()).with_auth(user.email)
        data = {"price": 20, "quantity": 5}
        response = client.patch(f"/stocks/{humanize(stock.id)}", json=data)

        # then
        assert response.status_code == 200
        assert stock.price == 20
        assert stock.quantity == 5

    def when_offer_come_from_allocine_provider_and_fields_updated_in_stock_are_editable(self, app):
        # given
        provider = offerers_factories.ProviderFactory(
            localClass="AllocineStocks",
            apiKey=None,
        )
        offer = offers_factories.ThingOfferFactory(
            lastProvider=provider,
            idAtProviders="1",
        )
        offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        stock = offers_factories.StockFactory(
            offer=offer,
            price=100,
            quantity=10,
        )
        initial_beginning = stock.beginningDatetime

        # when
        client = TestClient(app.test_client()).with_auth("user@example.com")
        booking_limit = datetime(2020, 1, 1, 10, 0, 0)
        data = {
            "price": 20,
            "quantity": 5,
            "bookingLimitDatetime": booking_limit.isoformat(),
            # updating beginningDatetime is not allowed
        }
        response = client.patch(f"/stocks/{humanize(stock.id)}", json=data)

        # then
        assert response.status_code == 200
        stock = StockSQLEntity.query.one()
        assert stock.price == 20
        assert stock.quantity == 5
        assert stock.beginningDatetime == initial_beginning
        assert stock.bookingLimitDatetime == booking_limit


@pytest.mark.usefixtures("db_session")
class Returns400:
    def when_wrong_type_for_quantity(self, app):
        # given
        user = users_factories.UserFactory(canBookFreeOffers=False, isAdmin=True)
        stock = offers_factories.StockFactory()

        # when
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.patch(f"/stocks/{humanize(stock.id)}", json={"quantity": " "})

        # then
        assert response.status_code == 400
        assert response.json == {"quantity": ["Saisissez un nombre valide"]}

    def when_booking_limit_datetime_is_none_for_event(self, app, db_session):
        # Given
        user = users_factories.UserFactory(canBookFreeOffers=False, isAdmin=True)
        stock = offers_factories.EventStockFactory()

        # When
        data = {
            "price": 0,
            "offerId": humanize(stock.offer.id),
            "beginningDatetime": stock.beginningDatetime.isoformat(),
            "bookingLimitDatetime": None,
        }
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.patch(f"/stocks/{humanize(stock.id)}", json=data)

        # Then
        assert response.status_code == 400
        assert response.json == {"bookingLimitDatetime": ["Ce paramètre est obligatoire"]}


class Returns403:
    def when_user_has_no_rights(self, app, db_session):
        # given
        user = users_factories.UserFactory(email="wrong@example.com")
        stock = offers_factories.StockFactory()

        # when
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.patch(f"/stocks/{humanize(stock.id)}", json={"quantity": 5})

        # then
        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
        }
