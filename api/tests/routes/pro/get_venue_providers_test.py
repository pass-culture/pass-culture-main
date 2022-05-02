from datetime import datetime

import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def test_get_list_with_valid_venue_id(self, app):
        # given
        user_offerer = offerers_factories.UserOffererFactory()
        titelive_things_provider = get_provider_by_local_class("TiteLiveThings")
        venue_provider = providers_factories.VenueProviderFactory(
            venue__name="Librairie Titelive",
            venue__managingOfferer=user_offerer.offerer,
            provider=titelive_things_provider,
            lastSyncDate=datetime(2021, 8, 16),
        )

        # test that nOffers only containe active offers
        offers_factories.OfferFactory(
            venue=venue_provider.venue,
            lastProviderId=venue_provider.provider.id,
            idAtProvider="testIdAtProvider1",
            isActive=True,
        )
        offers_factories.OfferFactory(
            venue=venue_provider.venue,
            lastProviderId=venue_provider.provider.id,
            idAtProvider="testIdAtProvider2",
            isActive=False,
        )

        # when
        auth_request = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        response = auth_request.get("/venueProviders?venueId=" + humanize(venue_provider.venue.id))

        # then
        assert response.status_code == 200
        assert response.json["venue_providers"][0].get("nOffers") == 1
        assert response.json["venue_providers"][0].get("id") == humanize(venue_provider.id)
        assert response.json["venue_providers"][0].get("venueId") == humanize(venue_provider.venue.id)
        assert response.json["venue_providers"][0].get("lastSyncDate") == "2021-08-16T00:00:00Z"

    @pytest.mark.usefixtures("db_session")
    def test_get_list_that_include_allocine_with_valid_venue_id(self, app):
        # given
        user_offerer = offerers_factories.UserOffererFactory()
        allocine_stocks_provider = get_provider_by_local_class("AllocineStocks")
        allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(
            venue__name="Whatever cinema",
            venue__managingOfferer=user_offerer.offerer,
            provider=allocine_stocks_provider,
        )
        providers_factories.AllocineVenueProviderPriceRuleFactory(
            price=123.2, allocineVenueProvider=allocine_venue_provider
        )

        # when
        auth_request = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        response = auth_request.get("/venueProviders?venueId=" + humanize(allocine_venue_provider.venue.id))

        # then
        assert response.status_code == 200
        assert response.json["venue_providers"][0].get("id") == humanize(allocine_venue_provider.id)
        assert response.json["venue_providers"][0].get("venueId") == humanize(allocine_venue_provider.venue.id)
        assert response.json["venue_providers"][0].get("price") == 123.2


class Returns400Test:
    @pytest.mark.usefixtures("db_session")
    def when_listing_all_venues_without_venue_id_argument(self, app):
        # given
        user_offerer = offerers_factories.UserOffererFactory()
        titelive_things_provider = get_provider_by_local_class("TiteLiveThings")
        providers_factories.VenueProviderFactory(
            venue__name="Librairie Titelive",
            venue__managingOfferer=user_offerer.offerer,
            provider=titelive_things_provider,
        )

        # when
        auth_request = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        response = auth_request.get("/venueProviders")

        # then
        assert response.status_code == 400
