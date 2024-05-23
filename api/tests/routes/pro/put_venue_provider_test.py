import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.models as provider_models
import pcapi.core.users.factories as user_factories


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def test_allocine_venue_provider_is_successfully_updated(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        user = user_offerer.user
        offerer = user_offerer.offerer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        provider = providers_factories.AllocineProviderFactory()
        providers_factories.AllocineVenueProviderFactory(
            venue=venue, provider=provider, isDuo=False, quantity=42, isActive=True, price=10
        )

        updated_venue_provider_data = {
            "providerId": provider.id,
            "venueId": venue.id,
            "isDuo": True,
            "quantity": 77,
            "price": 64,
            "isActive": False,
        }

        auth_request = client.with_session_auth(email=user.email)

        # When
        response = auth_request.put("/venueProviders", json=updated_venue_provider_data)

        # Then
        assert response.status_code == 200
        assert response.json["provider"]["id"] == provider.id
        assert response.json["venueId"] == venue.id
        assert response.json["quantity"] == updated_venue_provider_data["quantity"]
        assert response.json["price"] == updated_venue_provider_data["price"]
        assert response.json["isDuo"] == updated_venue_provider_data["isDuo"]
        assert response.json["isActive"] == updated_venue_provider_data["isActive"]

    @pytest.mark.usefixtures("db_session")
    def test_cinema_venue_provider_is_successfully_updated(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        user = user_offerer.user
        offerer = user_offerer.offerer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        cds_provider = provider_models.Provider.query.filter(provider_models.Provider.localClass == "CDSStocks").one()
        providers_factories.VenueProviderFactory(venue=venue, provider=cds_provider, isDuoOffers=False, isActive=False)

        updated_venue_provider_data = {
            "providerId": cds_provider.id,
            "venueId": venue.id,
            "isDuo": True,
            "isActive": True,
        }
        auth_request = client.with_session_auth(email=user.email)

        response = auth_request.put("/venueProviders", json=updated_venue_provider_data)

        assert response.status_code == 200
        assert response.json["provider"]["id"] == cds_provider.id
        assert response.json["venueId"] == venue.id
        assert response.json["isDuo"] == updated_venue_provider_data["isDuo"]
        assert response.json["isActive"] == updated_venue_provider_data["isActive"]

    @pytest.mark.usefixtures("db_session")
    def test_provider_is_not_allocine_and_not_cinema_provider(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        user = user_offerer.user
        offerer = user_offerer.offerer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        provider = providers_factories.ProviderFactory()
        providers_factories.VenueProviderFactory(venue=venue, provider=provider, isActive=True)

        updated_venue_provider_data = {
            "providerId": provider.id,
            "venueId": venue.id,
            "isActive": False,
        }

        auth_request = client.with_session_auth(email=user.email)

        # When
        response = auth_request.put("/venueProviders", json=updated_venue_provider_data)

        # then
        assert response.status_code == 200
        assert not response.json["isActive"]


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def test_user_is_not_logged_in(self, client):
        # when
        response = client.put("/venueProviders")

        # then
        assert response.status_code == 401


class Returns403Test:
    @pytest.mark.usefixtures("db_session")
    def test_user_has_right_on_venue(self, client):
        # Given
        user = user_factories.ProFactory()
        owner_offerer = offerers_factories.UserOffererFactory()
        offerer = owner_offerer.offerer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        provider = providers_factories.AllocineProviderFactory()
        providers_factories.AllocineVenueProviderFactory(
            venue=venue, provider=provider, isDuo=False, quantity=42, price=10
        )

        updated_venue_provider_data = {
            "providerId": provider.id,
            "venueId": venue.id,
            "isDuo": True,
            "quantity": 77,
            "price": 64,
        }

        auth_request = client.with_session_auth(email=user.email)

        # When
        response = auth_request.put("/venueProviders", json=updated_venue_provider_data)

        # Then
        assert response.status_code == 403
