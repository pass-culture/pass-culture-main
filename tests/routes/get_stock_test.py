import json

import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.repository import repository
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200:
    def when_user_is_logged_in(self, app, db_session):
        # given
        user = users_factories.UserFactory()
        stock = offers_factories.StockFactory(price=10, quantity=10)
        humanized_stock_id = humanize(stock.id)

        # when
        request = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .get("/stocks/" + humanized_stock_id)
        )
        # then
        assert request.json == {
            "beginningDatetime": None,
            "bookingLimitDatetime": None,
            "dateCreated": format_into_utc_date(stock.dateCreated),
            "dateModified": format_into_utc_date(stock.dateModified),
            "dateModifiedAtLastProvider": format_into_utc_date(
                stock.dateModifiedAtLastProvider
            ),
            "fieldsUpdated": [],
            "hasBeenMigrated": None,
            "id": humanized_stock_id,
            "idAtProviders": None,
            "isSoftDeleted": False,
            "lastProviderId": None,
            "offerId": humanize(stock.offer.id),
            "price": 10.0,
            "quantity": 10,
        }
        assert request.status_code == 200


class Returns404:
    def when_stock_is_soft_deleted(self, app, db_session):
        # given
        user = users_factories.UserFactory()
        stock = offers_factories.StockFactory(price=10, quantity=10, isSoftDeleted=True)
        humanized_stock_id = humanize(stock.id)

        # when
        request = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .get("/stocks/" + humanized_stock_id)
        )

        # then
        assert request.json == {}
        assert request.status_code == 404


class Returns401:
    def when_user_is_not_logged_in(self, app, db_session):
        # given
        user = users_factories.UserFactory(email="right@email.fr")
        stock = offers_factories.StockFactory()
        humanized_stock_id = humanize(stock.id)

        # when
        request = (
            TestClient(app.test_client())
            .with_auth("wrong@email.fr")
            .get("/stocks/" + humanized_stock_id)
        )

        # then
        assert request.json == {"identifier": ["Identifiant incorrect"]}
        assert request.status_code == 401
