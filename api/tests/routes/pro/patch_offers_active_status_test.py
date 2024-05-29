import pytest

from pcapi.core import testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationStatus
import pcapi.core.providers.factories as providers_factories


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def when_activating_existing_offers(self, client):
        # Given
        offer1 = offers_factories.OfferFactory(isActive=False)
        venue = offer1.venue
        offer2 = offers_factories.OfferFactory(venue=venue, isActive=False)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"ids": [offer1.id, offer2.id], "isActive": True}
        response = client.patch("/offers/active-status", json=data)

        # Then
        assert response.status_code == 204
        assert Offer.query.filter_by(id=offer1.id).one().isActive
        assert Offer.query.filter_by(id=offer2.id).one().isActive

    def when_deactivating_existing_offers(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offer = offers_factories.OfferFactory(venue=venue)
        synchronized_offer = offers_factories.OfferFactory(
            lastProvider=providers_factories.ProviderFactory(), venue=venue
        )
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=venue.managingOfferer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"ids": [offer.id, synchronized_offer.id], "isActive": False}
        with testing.assert_no_duplicated_queries():
            response = client.patch("/offers/active-status", json=data)

        # Then
        assert response.status_code == 204
        assert not Offer.query.filter_by(id=offer.id).one().isActive
        assert not Offer.query.filter_by(id=synchronized_offer.id).one().isActive

    def test_only_approved_offers_patch(self, client):
        approved_offer = offers_factories.OfferFactory(isActive=False)
        venue = approved_offer.venue
        pending_offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.PENDING)
        rejected_offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.REJECTED)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        client = client.with_session_auth("pro@example.com")
        data = {
            "ids": [approved_offer.id, pending_offer.id, rejected_offer.id],
            "isActive": True,
        }
        response = client.patch("/offers/active-status", json=data)

        assert response.status_code == 204
        assert approved_offer.isActive
        assert not pending_offer.isActive
        assert not rejected_offer.isActive

    def when_activating_synchronized_offer(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offer = offers_factories.OfferFactory(venue=venue, isActive=False)

        provider = providers_factories.ProviderFactory()
        offer_that_should_stay_deactivated = offers_factories.OfferFactory(
            lastProvider=provider, venue=venue, isActive=False
        )
        providers_factories.VenueProviderFactory(provider=provider, venue=venue, isActive=False)

        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=venue.managingOfferer)

        # When
        client = client.with_session_auth("pro@example.com")
        response = client.patch(
            "/offers/active-status",
            json={"ids": [offer_that_should_stay_deactivated.id, offer.id], "isActive": True},
        )

        # Then
        assert response.status_code == 204
        assert not offer_that_should_stay_deactivated.isActive
        assert offer.isActive
