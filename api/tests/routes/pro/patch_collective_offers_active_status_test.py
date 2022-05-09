import pytest

from pcapi.core import testing
from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.models import CollectiveOffer
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def when_activating_existing_offers(self, client):
        # Given
        offer1 = CollectiveOfferFactory(isActive=False)
        venue = offer1.venue
        offer2 = CollectiveOfferFactory(venue=venue, isActive=False)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"ids": [humanize(offer1.id), humanize(offer2.id)], "isActive": True}
        response = client.patch("/collective/offers/active-status", json=data)

        # Then
        assert response.status_code == 204
        assert CollectiveOffer.query.get(offer1.id).isActive
        assert CollectiveOffer.query.get(offer2.id).isActive

    def when_deactivating_existing_offers(self, client):
        # Given
        offer1 = CollectiveOfferFactory()
        venue = offer1.venue
        offer2 = CollectiveOfferFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        collective_offers_update_queries = 3  # collective + release savepoint

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"ids": [humanize(offer1.id), humanize(offer2.id)], "isActive": False}
        with testing.assert_num_queries(testing.AUTHENTICATION_QUERIES + collective_offers_update_queries):
            response = client.patch("/collective/offers/active-status", json=data)

        # Then
        assert response.status_code == 204
        assert not CollectiveOffer.query.get(offer1.id).isActive
        assert not CollectiveOffer.query.get(offer2.id).isActive

    def test_only_approved_offers_patch(self, client):
        approved_offer = CollectiveOfferFactory(isActive=False)
        venue = approved_offer.venue
        pending_offer = CollectiveOfferFactory(venue=venue, validation=OfferValidationStatus.PENDING)
        rejected_offer = CollectiveOfferFactory(venue=venue, validation=OfferValidationStatus.REJECTED)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        client = client.with_session_auth("pro@example.com")
        data = {
            "ids": [humanize(approved_offer.id), humanize(pending_offer.id), humanize(rejected_offer.id)],
            "isActive": True,
        }
        response = client.patch("/collective/offers/active-status", json=data)

        assert response.status_code == 204
        assert approved_offer.isActive
        assert not pending_offer.isActive
        assert not rejected_offer.isActive
