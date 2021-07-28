import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.users import factories as users_factories
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def test_get_list_with_valid_venue_id(self, app):
        # given
        user = users_factories.ProFactory()
        titelive_things_provider = get_provider_by_local_class("TiteLiveThings")
        venue_provider = offerers_factories.VenueProviderFactory(
            venue__name="Librairie Titelive",
            provider=titelive_things_provider,
        )

        # when
        auth_request = TestClient(app.test_client()).with_auth(email=user.email)
        response = auth_request.get("/venueProviders?venueId=" + humanize(venue_provider.venue.id))

        # then
        assert response.status_code == 200
        assert response.json["venue_providers"][0].get("id") == humanize(venue_provider.id)
        assert response.json["venue_providers"][0].get("venueId") == humanize(venue_provider.venue.id)

    @pytest.mark.usefixtures("db_session")
    def test_get_list_that_include_allocine_with_valid_venue_id(self, app):
        # given
        user = users_factories.ProFactory()
        allocine_stocks_provider = get_provider_by_local_class("AllocineStocks")
        allocine_venue_provider = offerers_factories.VenueProviderFactory(
            venue__name="Whatever cinema",
            provider=allocine_stocks_provider,
        )

        # when
        auth_request = TestClient(app.test_client()).with_auth(email=user.email)
        response = auth_request.get("/venueProviders?venueId=" + humanize(allocine_venue_provider.venue.id))

        # then
        assert response.status_code == 200
        assert response.json["venue_providers"][0].get("id") == humanize(allocine_venue_provider.id)
        assert response.json["venue_providers"][0].get("venueId") == humanize(allocine_venue_provider.venue.id)


class Returns400Test:
    @pytest.mark.usefixtures("db_session")
    def when_listing_all_venues_without_venue_id_argument(self, app):
        # given
        user = users_factories.ProFactory()
        titelive_things_provider = get_provider_by_local_class("TiteLiveThings")
        offerers_factories.VenueProviderFactory(
            venue__name="Librairie Titelive",
            provider=titelive_things_provider,
        )

        # when
        auth_request = TestClient(app.test_client()).with_auth(email=user.email)
        response = auth_request.get("/venueProviders")

        # then
        assert response.status_code == 400
