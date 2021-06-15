import pytest

from pcapi.core import testing
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.models import Offer
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def when_activating_existing_offers(self, app):
        # Given
        offer1 = offers_factories.OfferFactory(isActive=False)
        venue = offer1.venue
        offer2 = offers_factories.OfferFactory(venue=venue, isActive=False)
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = TestClient(app.test_client()).with_auth("pro@example.com")
        data = {"ids": [humanize(offer1.id), humanize(offer2.id)], "isActive": True}
        response = client.patch("/offers/active-status", json=data)

        # Then
        assert response.status_code == 204
        assert Offer.query.get(offer1.id).isActive
        assert Offer.query.get(offer2.id).isActive

    def when_deactivating_existing_offers(self, app):
        # Given
        offer1 = offers_factories.OfferFactory()
        venue = offer1.venue
        offer2 = offers_factories.OfferFactory(venue=venue)
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        offers_update_queries = 3

        # When
        client = TestClient(app.test_client()).with_auth("pro@example.com")
        data = {"ids": [humanize(offer1.id), humanize(offer2.id)], "isActive": False}
        with testing.assert_num_queries(testing.AUTHENTICATION_QUERIES + offers_update_queries):
            response = client.patch("/offers/active-status", json=data)

        # Then
        assert response.status_code == 204
        assert not Offer.query.get(offer1.id).isActive
        assert not Offer.query.get(offer2.id).isActive

    def test_only_approved_offers_patch(self, app):
        approved_offer = offers_factories.OfferFactory(isActive=False)
        venue = approved_offer.venue
        pending_offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.PENDING)
        rejected_offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.REJECTED)
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        client = TestClient(app.test_client()).with_auth("pro@example.com")
        data = {
            "ids": [humanize(approved_offer.id), humanize(pending_offer.id), humanize(rejected_offer.id)],
            "isActive": True,
        }
        response = client.patch("/offers/active-status", json=data)

        assert response.status_code == 204
        assert approved_offer.isActive
        assert not pending_offer.isActive
        assert not rejected_offer.isActive
