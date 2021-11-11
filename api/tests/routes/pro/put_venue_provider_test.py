import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offer_factories
from pcapi.core.users import factories as user_factories
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def test_allocine_venue_provider_is_successfully_updated(self, app):
        # Given
        user_offerer = offer_factories.UserOffererFactory()
        user = user_offerer.user
        offerer = user_offerer.offerer
        venue = offer_factories.VenueFactory(managingOfferer=offerer)
        provider = offerers_factories.AllocineProviderFactory()
        venue_provider = offerers_factories.AllocineVenueProviderFactory(
            venue=venue,
            provider=provider,
            isDuo=False,
            quantity=42,
        )
        offerers_factories.AllocineVenueProviderPriceRuleFactory(allocineVenueProvider=venue_provider, price=10)

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
        assert response.status_code == 200
        assert response.json["provider"]["id"] == humanize(provider.id)
        assert response.json["venueId"] == humanize(venue.id)
        assert response.json["quantity"] == updated_venue_provider_data["quantity"]
        assert response.json["price"] == updated_venue_provider_data["price"]
        assert response.json["isDuo"] == updated_venue_provider_data["isDuo"]


class Returns400Test:
    @pytest.mark.usefixtures("db_session")
    def test_provider_is_not_allocine(self, app):
        # Given
        user_offerer = offer_factories.UserOffererFactory()
        user = user_offerer.user
        offerer = user_offerer.offerer
        venue = offer_factories.VenueFactory(managingOfferer=offerer)
        provider = offerers_factories.ProviderFactory()
        offerers_factories.VenueProviderFactory(venue=venue, provider=provider)

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

        # then
        assert response.status_code == 400


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
        owner_offerer = offer_factories.UserOffererFactory()
        offerer = owner_offerer.offerer
        venue = offer_factories.VenueFactory(managingOfferer=offerer)
        provider = offerers_factories.AllocineProviderFactory()
        venue_provider = offerers_factories.AllocineVenueProviderFactory(
            venue=venue,
            provider=provider,
            isDuo=False,
            quantity=42,
        )
        offerers_factories.AllocineVenueProviderPriceRuleFactory(allocineVenueProvider=venue_provider, price=10)

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
