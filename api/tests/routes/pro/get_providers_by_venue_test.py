import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
def test_venue_has_known_allocine_id(client):
    # Given
    user = users_factories.UserFactory()
    venue = offerers_factories.VenueFactory()
    providers_factories.AllocineTheaterFactory(siret=venue.siret)

    allocine_provider = providers_factories.ProviderFactory(localClass="AllocineStocks")
    other_provider = providers_factories.ProviderFactory(localClass="B provider")

    # When
    response = client.with_session_auth(email=user.email).get(f"/providers/{venue.id}")

    # Then
    assert response.status_code == 200
    assert len(response.json) == 5
    assert response.json[:2] == [
        {
            "enabledForPro": True,
            "id": allocine_provider.id,
            "isActive": True,
            "name": "Allociné",
            "hasOffererProvider": False,
        },
        {
            "enabledForPro": True,
            "id": other_provider.id,
            "isActive": True,
            "name": other_provider.name,
            "hasOffererProvider": False,
        },
    ]


@pytest.mark.usefixtures("db_session")
def test_venue_has_no_allocine_id(client):
    # Given
    user = users_factories.UserFactory(email="user@example.com")
    venue = offerers_factories.VenueFactory()

    allocine_provider = providers_factories.ProviderFactory(localClass="AllocineStocks")
    other_provider = providers_factories.ProviderFactory(localClass="B provider")

    # When
    response = client.with_session_auth(email=user.email).get(f"/providers/{venue.id}")

    # Then
    assert response.status_code == 200
    assert len(response.json) == 4
    assert response.json[0] == {
        "enabledForPro": True,
        "id": other_provider.id,
        "isActive": True,
        "name": other_provider.name,
        "hasOffererProvider": False,
    }
    assert allocine_provider.id not in [p["id"] for p in response.json]


@pytest.mark.usefixtures("db_session")
def test_venue_has_offerer_provider(client):
    # Given
    name = "MangoMusic"
    user = users_factories.UserFactory(email="user@example.com")
    venue = offerers_factories.VenueFactory()
    provider = providers_factories.ProviderFactory(
        name=name,
        localClass=None,
    )
    offerer_provider = providers_factories.OffererProviderFactory(
        provider=provider,
    )
    offerers_factories.ApiKeyFactory(offerer=offerer_provider.offerer)

    providers_factories.VenueProviderFactory(venue=venue, provider=provider)

    # When
    response = client.with_session_auth(email=user.email).get(f"/providers/{venue.id}")

    # Then
    assert response.status_code == 200
    assert len(response.json) == 4
    mango_provider = list(filter(lambda x: x["name"] == name, response.json))
    assert mango_provider == [
        {
            "enabledForPro": True,
            "id": provider.id,
            "isActive": True,
            "name": provider.name,
            "hasOffererProvider": True,
        }
    ]


@pytest.mark.usefixtures("db_session")
def test_venue_does_not_exist(client):
    user = users_factories.UserFactory()

    response = client.with_session_auth(email=user.email).get("/providers/1234")

    assert response.status_code == 404


@pytest.mark.usefixtures("db_session")
def test_user_is_not_logged_in(client):
    response = client.get("/providers/1234")

    assert response.status_code == 401
