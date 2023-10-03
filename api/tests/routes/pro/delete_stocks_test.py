import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offer_models
import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def test_delete_multiple_stocks_by_offer_id(self, client):
        # Given
        offer = offers_factories.OfferFactory()
        user = users_factories.UserFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offer.venue.managingOfferer)

        batch_stocks = offers_factories.StockFactory.create_batch(3, offer=offer)
        data = {"ids_to_delete": [stock.id for stock in batch_stocks]}

        # When
        response = client.with_session_auth(user.email).post(f"/offers/{offer.id}/stocks/delete", json=data)

        # Then
        assert response.status_code == 204

        assert all(stock.isSoftDeleted for stock in offer_models.Stock.query.all())

    def test_delete_unaccessible_stocks(self, client):
        # Given
        offer = offers_factories.OfferFactory()
        another_offer = offers_factories.OfferFactory()
        user = users_factories.UserFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offer.venue.managingOfferer)

        another_offer_stocks = offers_factories.StockFactory.create_batch(3, offer=another_offer)

        # When
        response = client.with_session_auth(user.email).post(
            f"/offers/{offer.id}/stocks/delete", json={"ids_to_delete": [stock.id for stock in another_offer_stocks]}
        )

        # Then
        assert response.status_code == 204

        assert all(not stock.isSoftDeleted for stock in offer_models.Stock.query.all())


@pytest.mark.usefixtures("db_session")
class Returns401Test:
    def test_delete_stocks_not_connected(self, client):
        # Given
        offer = offers_factories.OfferFactory()
        user = users_factories.UserFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offer.venue.managingOfferer)
        stock = offers_factories.StockFactory(offer=offer)
        data = {"ids_to_delete": [stock.id]}

        # When
        response = client.post(f"/offers/{offer.id}/stocks/delete", json=data)

        # Then
        assert response.status_code == 401


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_delete_stocks_when_current_user_has_no_rights_on_offer(self, client):
        # given
        offer = offers_factories.OfferFactory()
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        stock = offers_factories.StockFactory(offer=offer)
        data = {"ids_to_delete": [stock.id]}

        # when
        response = client.with_session_auth(pro.email).post(f"/offers/{offer.id}/stocks/delete", json=data)

        # then
        assert response.status_code == 403
