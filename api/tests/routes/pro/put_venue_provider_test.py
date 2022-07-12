import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.models as provider_models
import pcapi.core.users.factories as user_factories
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def test_allocine_venue_provider_is_successfully_updated(self, app):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        user = user_offerer.user
        offerer = user_offerer.offerer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        provider = providers_factories.AllocineProviderFactory()
        venue_provider = providers_factories.AllocineVenueProviderFactory(
            venue=venue,
            provider=provider,
            isDuo=False,
            quantity=42,
            isActive=True,
        )
        providers_factories.AllocineVenueProviderPriceRuleFactory(allocineVenueProvider=venue_provider, price=10)

        updated_venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
            "isDuo": True,
            "quantity": 77,
            "price": 64,
            "isActive": False,
        }

        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

        # When
        response = auth_request.put("/venueProviders", json=updated_venue_provider_data)

        # Then
        assert response.status_code == 200
        assert response.json["provider"]["id"] == humanize(provider.id)
        assert response.json["venueId"] == humanize(venue.id)
        assert response.json["quantity"] == updated_venue_provider_data["quantity"]
        assert response.json["price"] == updated_venue_provider_data["price"]
        assert response.json["isDuo"] == updated_venue_provider_data["isDuo"]
        assert response.json["isActive"] == updated_venue_provider_data["isActive"]

    @pytest.mark.usefixtures("db_session")
    def test_cinema_venue_provider_is_successfully_updated(self, app):
        user_offerer = offerers_factories.UserOffererFactory()
        user = user_offerer.user
        offerer = user_offerer.offerer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        cds_provider = provider_models.Provider.query.filter(provider_models.Provider.localClass == "CDSStocks").one()
        providers_factories.VenueProviderFactory(venue=venue, provider=cds_provider, isDuoOffers=False, isActive=False)

        updated_venue_provider_data = {
            "providerId": humanize(cds_provider.id),
            "venueId": humanize(venue.id),
            "isDuo": True,
            "isActive": True,
        }
        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

        response = auth_request.put("/venueProviders", json=updated_venue_provider_data)

        assert response.status_code == 200
        assert response.json["provider"]["id"] == humanize(cds_provider.id)
        assert response.json["venueId"] == humanize(venue.id)
        assert response.json["isDuo"] == updated_venue_provider_data["isDuo"]
        assert response.json["isActive"] == updated_venue_provider_data["isActive"]

    @pytest.mark.usefixtures("db_session")
    def test_provider_is_not_allocine_and_not_cinema_provider(self, app):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        user = user_offerer.user
        offerer = user_offerer.offerer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        provider = providers_factories.ProviderFactory()
        providers_factories.VenueProviderFactory(venue=venue, provider=provider, isActive=True)

        updated_venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
            "isActive": False,
        }

        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

        # When
        response = auth_request.put("/venueProviders", json=updated_venue_provider_data)

        # then
        assert response.status_code == 200
        assert not response.json["isActive"]


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def test_user_is_not_logged_in(self, app):
        # when
        response = TestClient(app.test_client()).put("/venueProviders")

        # then
        assert response.status_code == 401


class Returns403Test:
    @pytest.mark.usefixtures("db_session")
    def test_user_has_right_on_venue(self, app):
        # Given
        user = user_factories.ProFactory()
        owner_offerer = offerers_factories.UserOffererFactory()
        offerer = owner_offerer.offerer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        provider = providers_factories.AllocineProviderFactory()
        venue_provider = providers_factories.AllocineVenueProviderFactory(
            venue=venue,
            provider=provider,
            isDuo=False,
            quantity=42,
        )
        providers_factories.AllocineVenueProviderPriceRuleFactory(allocineVenueProvider=venue_provider, price=10)

        updated_venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
            "isDuo": True,
            "quantity": 77,
            "price": 64,
        }

        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

        # When
        response = auth_request.put("/venueProviders", json=updated_venue_provider_data)

        # Then
        assert response.status_code == 403
