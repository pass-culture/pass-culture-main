from datetime import datetime

import pytest
import time_machine

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offer_models
import pcapi.core.users.factories as users_factories
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    @time_machine.travel("2020-10-15 00:00:00")
    def test_delete_filtered_stocks(self, client):
        # Given
        offer = offers_factories.OfferFactory()
        offers_factories.EventStockFactory.create_batch(3, offer=offer, beginningDatetime=datetime.utcnow())
        user = users_factories.UserFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offer.venue.managingOfferer)

        data = {
            "offer_id": offer.id,
            "date": "2020-10-15",
            "time": "00:00:00",
            "price_category_id": None,
        }

        # When
        response = client.with_session_auth(user.email).post(f"/offers/{offer.id}/stocks/all-delete", json=data)

        # Then
        assert response.status_code == 204

        assert len(db.session.query(offer_models.Stock).all()) == 0


@pytest.mark.usefixtures("db_session")
class Returns401Test:
    def test_delete_filtered_stocks_not_connected(self, client):
        offer = offers_factories.OfferFactory()
        offers_factories.StockFactory(offer=offer)
        user = users_factories.UserFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offer.venue.managingOfferer)
        data = {
            "offer_id": offer.id,
            "date": "2020-10-15",
            "time": "00:00:00",
            "price_category_id": None,
        }

        response = client.post(f"/offers/{offer.id}/stocks/all-delete", json=data)

        assert response.status_code == 401


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_delete_stocks_when_current_user_has_no_rights_on_offer(self, client):
        # given
        offer = offers_factories.OfferFactory()
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        offers_factories.EventStockFactory(offer=offer, beginningDatetime=datetime.utcnow())
        data = {
            "offer_id": offer.id,
            "date": "2020-10-15",
            "time": "00:00:00",
            "price_category_id": None,
        }

        response = client.with_session_auth(pro.email).post(f"/offers/{offer.id}/stocks/all-delete", json=data)

        # then
        assert response.status_code == 403
