from datetime import datetime
from datetime import timedelta

from freezegun import freeze_time
import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_access_by_beneficiary(self, app):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        offer = offers_factories.ThingOfferFactory(venue__latitude=None, venue__longitude=None)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=beneficiary.email)
        response = client.get(f"/offers/{offer.id}/stocks")

        # Then
        assert response.status_code == 403

    def test_access_by_unauthorized_pro_user(self, app):
        # Given
        pro_user = users_factories.ProFactory()
        offer = offers_factories.ThingOfferFactory(venue__latitude=None, venue__longitude=None)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=pro_user.email)
        response = client.get(f"/offers/{offer.id}/stocks")

        # Then
        assert response.status_code == 403


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_basic(self, app):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(venue__managingOfferer=user_offerer.offerer)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        response = client.get(f"/offers/{offer.id}/stocks/")

        # Then
        assert response.status_code == 200

    @freeze_time("2020-10-15 00:00:00")
    def test_returns_an_event_stock(self, app):
        # Given
        now = datetime.utcnow()
        user_offerer = offerers_factories.UserOffererFactory()
        event_offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)
        stock = offers_factories.EventStockFactory(
            dateCreated=now,
            dateModified=now,
            dateModifiedAtLastProvider=now,
            beginningDatetime=now + timedelta(hours=1),
            bookingLimitDatetime=now + timedelta(hours=1),
            offer=event_offer,
        )

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        response = client.get(f"/offers/{event_offer.id}/stocks")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "stock_count": 1,
            "stocks": [
                {
                    "activationCodesExpirationDatetime": None,
                    "beginningDatetime": "2020-10-15T01:00:00Z",
                    "bookingLimitDatetime": "2020-10-15T01:00:00Z",
                    "bookingsQuantity": 0,
                    "dateCreated": "2020-10-15T00:00:00Z",
                    "dateModified": "2020-10-15T00:00:00Z",
                    "hasActivationCode": False,
                    "priceCategoryId": stock.priceCategoryId,
                    "id": stock.id,
                    "isBookable": True,
                    "isEventDeletable": True,
                    "isEventExpired": False,
                    "isSoftDeleted": False,
                    "price": 10.1,
                    "quantity": 1000,
                    "remainingQuantity": 1000,
                }
            ],
        }

    @freeze_time("2020-10-15 00:00:00")
    def test_returns_a_thing_stock(self, app):
        # Given
        now = datetime.utcnow()
        user_offerer = offerers_factories.UserOffererFactory()
        thing_offer = offers_factories.ThingOfferFactory(venue__managingOfferer=user_offerer.offerer)
        stock = offers_factories.ThingStockFactory(
            dateCreated=now,
            dateModified=now,
            offer=thing_offer,
        )

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        response = client.get(f"/offers/{thing_offer.id}/stocks")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "stock_count": 1,
            "stocks": [
                {
                    "activationCodesExpirationDatetime": None,
                    "beginningDatetime": None,
                    "bookingLimitDatetime": None,
                    "bookingsQuantity": 0,
                    "dateCreated": "2020-10-15T00:00:00Z",
                    "dateModified": "2020-10-15T00:00:00Z",
                    "hasActivationCode": False,
                    "id": stock.id,
                    "isBookable": True,
                    "isEventDeletable": True,
                    "isEventExpired": False,
                    "isSoftDeleted": False,
                    "price": 10.1,
                    "priceCategoryId": None,
                    "quantity": 1000,
                    "remainingQuantity": 1000,
                },
            ],
        }

    def test_should_not_return_soft_deleted_stock(self, app):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)
        deleted_stock = offers_factories.EventStockFactory(offer=offer, isSoftDeleted=True)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        response = client.get(f"/offers/{deleted_stock.offer.id}/stocks")

        # Then
        assert response.status_code == 200
        assert len(response.json["stocks"]) == 0
