import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.models as provider_models
import pcapi.core.users.factories as user_factories
from pcapi.models import db


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def test_allocine_venue_provider_is_successfully_updated(self, client):
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
            price=10,
            venueIdAtOfferProvider="00000029900263",
        )

        auth_request = client.with_session_auth(email=user.email)

        response = auth_request.put(
            f"/venue-providers/{venue_provider.id}",
            json={
                "isDuo": True,
                "quantity": 77,
                "price": 64,
                "isActive": False,
            },
        )

        assert response.status_code == 200
        assert response.json == {
            "id": venue_provider.id,
            "isActive": False,
            "isDuo": True,
            "isFromAllocineProvider": True,
            "lastSyncDate": None,
            "dateCreated": venue_provider.dateCreated.isoformat() + "Z",
            "price": 64.0,
            "provider": {
                "id": venue_provider.providerId,
                "name": "Allociné",
                "enabledForPro": True,
                "isActive": True,
                "hasOffererProvider": False,
            },
            "quantity": 77,
            "venueId": venue_provider.venueId,
            "venueIdAtOfferProvider": "00000029900263",
        }

    @pytest.mark.usefixtures("db_session")
    def test_cinema_venue_provider_is_successfully_updated(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        user = user_offerer.user
        offerer = user_offerer.offerer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        cds_provider = (
            db.session.query(provider_models.Provider).filter(provider_models.Provider.localClass == "CDSStocks").one()
        )
        venue_provider = providers_factories.VenueProviderFactory(
            venue=venue,
            provider=cds_provider,
            isDuoOffers=False,
            isActive=False,
            venueIdAtOfferProvider="00000030700272",
        )

        auth_request = client.with_session_auth(email=user.email)
        response = auth_request.put(f"/venue-providers/{venue_provider.id}", json={"isDuo": True, "isActive": True})
        print(response.json)
        assert response.status_code == 200
        assert response.json == {
            "id": venue_provider.id,
            "isActive": True,
            "isDuo": True,
            "isFromAllocineProvider": False,
            "lastSyncDate": None,
            "dateCreated": venue_provider.dateCreated.isoformat() + "Z",
            "price": None,
            "provider": {
                "id": venue_provider.providerId,
                "name": "Ciné Office",
                "enabledForPro": True,
                "isActive": True,
                "hasOffererProvider": False,
            },
            "quantity": None,
            "venueId": venue_provider.venueId,
            "venueIdAtOfferProvider": "00000030700272",
        }

    @pytest.mark.usefixtures("db_session")
    def test_provider_is_not_allocine_and_not_cinema_provider(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        user = user_offerer.user
        offerer = user_offerer.offerer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        provider = providers_factories.ProviderFactory()
        venue_provider = providers_factories.VenueProviderFactory(venue=venue, provider=provider, isActive=True)

        auth_request = client.with_session_auth(email=user.email)

        response = auth_request.put(f"/venue-providers/{venue_provider.id}", json={"isActive": False})

        assert response.status_code == 200
        assert not response.json["isActive"]


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def test_user_is_not_logged_in(self, client):
        response = client.put("/venue-providers/1")
        assert response.status_code == 401


class Returns403Test:
    @pytest.mark.usefixtures("db_session")
    def test_user_has_right_on_venue(self, client):
        user = user_factories.ProFactory()
        owner_offerer = offerers_factories.UserOffererFactory()
        offerer = owner_offerer.offerer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        provider = providers_factories.AllocineProviderFactory()
        venue_provider = providers_factories.AllocineVenueProviderFactory(
            venue=venue, provider=provider, isDuo=False, quantity=42, price=10
        )

        auth_request = client.with_session_auth(email=user.email)

        response = auth_request.put(
            f"/venue-providers/{venue_provider.id}",
            json={
                "isDuo": True,
                "quantity": 77,
                "price": 64,
            },
        )

        assert response.status_code == 403
