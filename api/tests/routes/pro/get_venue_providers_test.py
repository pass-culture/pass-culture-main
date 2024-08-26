from datetime import datetime
from decimal import Decimal

import pytest

from pcapi.core import testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.repository import get_provider_by_local_class


class Returns200Test:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # selecte venue
    num_queries += 1  # check user has rights on venue
    num_queries += 1  # check a venue_providers exists

    @pytest.mark.usefixtures("db_session")
    def test_get_list_with_valid_venue_id(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        titelive_things_provider = get_provider_by_local_class("TiteLiveThings")
        venue_provider = providers_factories.VenueProviderFactory(
            venue__name="Librairie Titelive",
            venue__managingOfferer=user_offerer.offerer,
            provider=titelive_things_provider,
            lastSyncDate=datetime(2021, 8, 16),
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        venue_id = venue_provider.venue.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_request.get(f"/venueProviders?venueId={venue_id}")
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

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        venue_id = allocine_venue_provider.venue.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_request.get(f"/venueProviders?venueId={venue_id}")
            assert response.status_code == 200

        assert response.status_code == 200
        assert response.json["venue_providers"][0].get("id") == allocine_venue_provider.id
        assert response.json["venue_providers"][0].get("venueId") == allocine_venue_provider.venue.id
        assert response.json["venue_providers"][0].get("price") == 123.2


class Returns400Test:
    @pytest.mark.usefixtures("db_session")
    def when_listing_all_venues_without_venue_id_argument(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        titelive_things_provider = get_provider_by_local_class("TiteLiveThings")
        providers_factories.VenueProviderFactory(
            venue__name="Librairie Titelive",
            venue__managingOfferer=user_offerer.offerer,
            provider=titelive_things_provider,
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        with testing.assert_num_queries(testing.AUTHENTICATION_QUERIES):
            response = auth_request.get("/venueProviders")
            assert response.status_code == 400
