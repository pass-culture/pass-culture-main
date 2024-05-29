from datetime import datetime

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.providers import factories as providers_factories


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def when_activating_all_existing_offers(self, client):
        # Given
        offer1 = offers_factories.OfferFactory(isActive=False)
        venue = offer1.venue
        offer2 = offers_factories.OfferFactory(venue=venue, isActive=False)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"isActive": True, "page": 1, "venueId": venue.id}
        response = client.patch("/offers/all-active-status", json=data)

        # Then
        assert response.status_code == 202
        assert Offer.query.filter_by(id=offer1.id).one_or_none().isActive
        assert Offer.query.filter_by(id=offer2.id).one_or_none().isActive

    def when_deactivating_all_existing_offers(self, client):
        # Given
        offer1 = offers_factories.OfferFactory()
        venue = offer1.venue
        offer2 = offers_factories.OfferFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"isActive": False}
        response = client.patch("/offers/all-active-status", json=data)

        # Then
        assert response.status_code == 202
        assert not Offer.query.filter_by(id=offer1.id).one_or_none().isActive
        assert not Offer.query.filter_by(id=offer2.id).one_or_none().isActive

    def should_update_offers_by_given_filters(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        matching_offer1 = offers_factories.OfferFactory(name="OKAY 1", venue=venue)
        offers_factories.StockFactory(offer=matching_offer1, beginningDatetime=datetime(2020, 10, 10, 12, 0, 0))
        matching_offer2 = offers_factories.OfferFactory(name="OKAY 2", venue=venue)
        offers_factories.StockFactory(offer=matching_offer2, beginningDatetime=datetime(2020, 10, 10, 12, 0, 0))

        offer_out_of_date_range = offers_factories.OfferFactory(name="OKAY 3", venue=venue)
        offers_factories.StockFactory(
            offer=offer_out_of_date_range,
            beginningDatetime=datetime(2020, 10, 12, 10, 0, 0),
        )
        offer_on_other_venue = offers_factories.OfferFactory(name="OKAY 4")
        offer_with_not_matching_name = offers_factories.OfferFactory(name="Pas celle-ci", venue=venue)

        data = {
            "isActive": False,
            "offererId": user_offerer.offerer.id,
            "venueId": venue.id,
            "name": "OKAY",
            "periodBeginningDate": "2020-10-09",
            "periodEndingDate": "2020-10-11",
        }
        client = client.with_session_auth(user_offerer.user.email)

        # When
        response = client.patch("/offers/all-active-status", json=data)

        # Then
        assert response.status_code == 202
        assert not Offer.query.filter_by(id=matching_offer1.id).one_or_none().isActive
        assert not Offer.query.filter_by(id=matching_offer2.id).one_or_none().isActive
        assert Offer.query.filter_by(id=offer_out_of_date_range.id).one_or_none().isActive
        assert Offer.query.filter_by(id=offer_on_other_venue.id).one_or_none().isActive
        assert Offer.query.filter_by(id=offer_with_not_matching_name.id).one_or_none().isActive

    def test_only_approved_offers_patch(self, client):
        approved_offer = offers_factories.OfferFactory(isActive=False)
        venue = approved_offer.venue
        pending_offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.PENDING)
        rejected_offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.REJECTED)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        client = client.with_session_auth("pro@example.com")
        data = {"isActive": True, "page": 1, "venueId": venue.id}
        response = client.patch("/offers/all-active-status", json=data)

        assert response.status_code == 202
        assert approved_offer.isActive
        assert not pending_offer.isActive
        assert not rejected_offer.isActive

    def test_only_offers_from_active_venue_provider_are_activated(self, client):
        venue = offerers_factories.VenueFactory()
        active_venue_provider = providers_factories.VenueProviderFactory(isActive=True, venue=venue)
        inactive_venue_provider = providers_factories.VenueProviderFactory(isActive=False, venue=venue)
        offer_from_active_venue_provider = offers_factories.OfferFactory(
            lastProvider=active_venue_provider.provider, venue=venue, isActive=False
        )
        offer_not_from_provider = offers_factories.OfferFactory(isActive=False, venue=venue)
        offer_from_inactive_venue_provider = offers_factories.OfferFactory(
            lastProvider=inactive_venue_provider.provider, venue=venue, isActive=False
        )
        offer_from_deleted_venue_provider = offers_factories.OfferFactory(
            lastProvider=providers_factories.ProviderFactory(), isActive=False, venue=venue
        )

        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=venue.managingOfferer)

        client = client.with_session_auth("pro@example.com")
        data = {"isActive": True, "venueId": venue.id}
        response = client.patch("/offers/all-active-status", json=data)

        assert response.status_code == 202

        assert offer_from_active_venue_provider.isActive
        assert offer_not_from_provider.isActive
        assert not offer_from_inactive_venue_provider.isActive
        assert not offer_from_deleted_venue_provider.isActive
