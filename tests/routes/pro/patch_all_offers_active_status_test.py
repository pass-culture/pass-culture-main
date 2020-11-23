from datetime import datetime

import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.models import Offer
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns204:
    def when_activating_all_existing_offers(self, app):
        # Given
        offer1 = offers_factories.OfferFactory(isActive=False)
        venue = offer1.venue
        offer2 = offers_factories.OfferFactory(venue=venue, isActive=False)
        offerer = venue.managingOfferer
        user_offerer = offers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = TestClient(app.test_client()).with_auth("pro@example.com")
        data = {"isActive": True}
        response = client.patch("/offers/all-active-status", json=data)

        # Then
        assert response.status_code == 204
        assert Offer.query.get(offer1.id).isActive
        assert Offer.query.get(offer2.id).isActive

    def when_deactivating_all_existing_offers(self, app):
        # Given
        offer1 = offers_factories.OfferFactory()
        venue = offer1.venue
        offer2 = offers_factories.OfferFactory(venue=venue)
        offerer = venue.managingOfferer
        user_offerer = offers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = TestClient(app.test_client()).with_auth("pro@example.com")
        data = {"isActive": False}
        response = client.patch("/offers/all-active-status", json=data)

        # Then
        assert response.status_code == 204
        assert not Offer.query.get(offer1.id).isActive
        assert not Offer.query.get(offer2.id).isActive

    def should_update_offers_by_given_filters(self, app):
        # Given
        matching_offer1 = offers_factories.OfferFactory(name="OK 1")
        offers_factories.StockFactory(
            offer=matching_offer1,
            beginningDatetime=datetime(2020, 10, 10, 12, 0, 0),
        )
        venue = matching_offer1.venue
        offerer = venue.managingOfferer
        user_offerer = offers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # This offer matches the offer-related criteria...
        matching_offer2 = offers_factories.OfferFactory(name="OK 1")
        # but its stock does NOT match stock-related criteria.
        offers_factories.StockFactory(
            offer=matching_offer2,
            beginningDatetime=datetime(2020, 10, 10, 12, 0, 0),
        )

        # When
        data = {
            "isActive": False,
            "offererId": humanize(offerer.id),
            "venueId": humanize(venue.id),
            "name": "OK",
            "periodBeginningDate": "2020-10-09T00:00:00Z",
            "periodEndingDate": "2020-10-11T23:59:59Z",
        }
        client = TestClient(app.test_client()).with_auth("pro@example.com")
        response = client.patch("/offers/all-active-status", json=data)

        # Then
        assert response.status_code == 204
        assert not Offer.query.get(matching_offer1.id).isActive
