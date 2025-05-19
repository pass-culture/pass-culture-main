from datetime import datetime
from datetime import timedelta

import pytest
import time_machine

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select offer
    num_queries += 1  # select venue
    num_queries += 1  # check user has rights on venue
    num_queries += 1  # rollback

    def test_access_by_beneficiary(self, client):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        offer = offers_factories.ThingOfferFactory()

        client = client.with_session_auth(email=beneficiary.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offers/{offer_id}/stocks-stats")
            assert response.status_code == 403

    def test_access_by_unauthorized_pro_user(self, client):
        pro_user = users_factories.ProFactory()
        offer = offers_factories.ThingOfferFactory()

        client = client.with_session_auth(email=pro_user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offers/{offer_id}/stocks-stats")
            assert response.status_code == 403


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select offer
    num_queries += 1  # select venue
    num_queries += 1  # check user has rights on venue
    num_queries += 1  # select stock stats (min and max begininngDatetime + count stocks)

    def test_basic(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(venue__managingOfferer=user_offerer.offerer)
        offers_factories.StockFactory(offer=offer)

        client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offers/{offer_id}/stocks-stats")
            assert response.status_code == 200

    @time_machine.travel("2020-10-15 00:00:00")
    def test_returns_stats(self, client):
        now = datetime.utcnow()
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)
        offers_factories.StockFactory(
            beginningDatetime=now + timedelta(hours=1),
            quantity=20,
            dnBookedQuantity=10,
            offer=offer,
        )
        offers_factories.StockFactory(
            beginningDatetime=now + timedelta(hours=2),
            quantity=30,
            dnBookedQuantity=25,
            offer=offer,
        )

        client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offers/{offer_id}/stocks-stats")
            assert response.status_code == 200

        assert response.json == {
            "stockCount": 2,
            "oldestStock": "2020-10-15T01:00:00Z",
            "newestStock": "2020-10-15T02:00:00Z",
            "remainingQuantity": 15,
        }
