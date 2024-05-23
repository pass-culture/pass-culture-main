from datetime import datetime
from decimal import Decimal

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.repository import get_provider_by_local_class


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def test_get_list_with_valid_venue_id(self, client):
        # given
        user_offerer = offerers_factories.UserOffererFactory()
        titelive_things_provider = get_provider_by_local_class("TiteLiveThings")
        venue_provider = providers_factories.VenueProviderFactory(
            venue__name="Librairie Titelive",
            venue__managingOfferer=user_offerer.offerer,
            provider=titelive_things_provider,
            lastSyncDate=datetime(2021, 8, 16),
        )

        # when
        auth_request = client.with_session_auth(email=user_offerer.user.email)
        response = auth_request.get(f"/venueProviders?venueId={venue_provider.venue.id}")

        # then
        assert response.status_code == 200
        assert response.json["venue_providers"][0].get("id") == venue_provider.id
        assert response.json["venue_providers"][0].get("venueId") == venue_provider.venue.id
        assert response.json["venue_providers"][0].get("lastSyncDate") == "2021-08-16T00:00:00Z"

    @pytest.mark.usefixtures("db_session")
    def test_get_list_that_include_allocine_with_valid_venue_id(self, client):
        # given
        user_offerer = offerers_factories.UserOffererFactory()
        allocine_stocks_provider = get_provider_by_local_class("AllocineStocks")
        allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(
            venue__name="Whatever cinema",
            venue__managingOfferer=user_offerer.offerer,
            provider=allocine_stocks_provider,
            price=Decimal("123.2"),
        )

        # when
        auth_request = client.with_session_auth(email=user_offerer.user.email)
        response = auth_request.get(f"/venueProviders?venueId={allocine_venue_provider.venue.id}")

        # then
        assert response.status_code == 200
        assert response.json["venue_providers"][0].get("id") == allocine_venue_provider.id
        assert response.json["venue_providers"][0].get("venueId") == allocine_venue_provider.venue.id
        assert response.json["venue_providers"][0].get("price") == 123.2


class Returns400Test:
    @pytest.mark.usefixtures("db_session")
    def when_listing_all_venues_without_venue_id_argument(self, client):
        # given
        user_offerer = offerers_factories.UserOffererFactory()
        titelive_things_provider = get_provider_by_local_class("TiteLiveThings")
        providers_factories.VenueProviderFactory(
            venue__name="Librairie Titelive",
            venue__managingOfferer=user_offerer.offerer,
            provider=titelive_things_provider,
        )

        # when
        auth_request = client.with_session_auth(email=user_offerer.user.email)
        response = auth_request.get("/venueProviders")

        # then
        assert response.status_code == 400
