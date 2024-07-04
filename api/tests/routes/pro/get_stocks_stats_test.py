from datetime import datetime
from datetime import timedelta

import pytest
import time_machine

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_access_by_beneficiary(self, client):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        offer = offers_factories.ThingOfferFactory(
            venue__latitude=None, venue__longitude=None, venue__offererAddress=None
        )

        # When
        response = client.with_session_auth(email=beneficiary.email).get(f"/offers/{offer.id}/stocks-stats")

        # Then
        assert response.status_code == 403

    def test_access_by_unauthorized_pro_user(self, client):
        # Given
        pro_user = users_factories.ProFactory()
        offer = offers_factories.ThingOfferFactory(
            venue__latitude=None, venue__longitude=None, venue__offererAddress=None
        )

        # When
        response = client.with_session_auth(email=pro_user.email).get(f"/offers/{offer.id}/stocks-stats")

        # Then
        assert response.status_code == 403


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_basic(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(venue__managingOfferer=user_offerer.offerer)
        offers_factories.StockFactory(offer=offer)

        # When
        response = client.with_session_auth(email=user_offerer.user.email).get(f"/offers/{offer.id}/stocks-stats")

        # Then
        assert response.status_code == 200

    @time_machine.travel("2020-10-15 00:00:00")
    def test_returns_stats(self, client):
        # Given
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

        # When
        response = client.with_session_auth(email=user_offerer.user.email).get(f"/offers/{offer.id}/stocks-stats")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "stockCount": 2,
            "oldestStock": "2020-10-15T01:00:00Z",
            "newestStock": "2020-10-15T02:00:00Z",
            "remainingQuantity": 15,
        }
