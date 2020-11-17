from datetime import datetime

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200:
    def when_current_user_has_rights_on_offer(self, app, db_session):
        # given
        offer = offers_factories.OfferFactory()
        offers_factories.UserOffererFactory(
            user__email="pro@example.com",
            offerer=offer.venue.managingOfferer,
        )
        stock = offers_factories.StockFactory(offer=offer)

        # when
        client = TestClient(app.test_client()).with_auth("pro@example.com")
        response = client.delete(f"/stocks/{humanize(stock.id)}")

        # then
        assert response.status_code == 200
        assert response.json == {"id": humanize(stock.id)}
        assert stock.isSoftDeleted


class Returns400:
    def when_stock_is_on_an_offer_from_titelive_provider(self, app, db_session):
        # given
        provider = offerers_factories.ProviderFactory(localClass="TiteLiveThings")
        offer = offers_factories.OfferFactory(lastProvider=provider, idAtProviders="1")
        stock = offers_factories.StockFactory(offer=offer)

        user = users_factories.UserFactory(isAdmin=True, canBookFreeOffers=False)

        # when
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.delete(f"/stocks/{humanize(stock.id)}")

        # then
        assert response.status_code == 400
        assert response.json["global"] == ["Les offres importées ne sont pas modifiables"]


class Returns403:
    def when_current_user_has_no_rights_on_offer(self, app, db_session):
        # given
        user = users_factories.UserFactory(email="notadmin@example.com")
        stock = offers_factories.StockFactory()

        # when
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.delete(f"/stocks/{humanize(stock.id)}")

        # then
        assert response.status_code == 403
