import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
def test_venue_has_known_allocine_id(client):
    user = users_factories.UserFactory()
    venue = offerers_factories.VenueFactory()
    providers_factories.AllocineTheaterFactory(siret=venue.siret)

    allocine_provider = providers_factories.AllocineProviderFactory()
    other_provider = providers_factories.ProviderFactory(localClass="B provider")

    client = client.with_session_auth(email=user.email)
    venue_id = venue.id
    db.session.expire_all()
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select venue
    num_queries += 1  # select cinema_provider_pivot
    num_queries += 1  # select allocine_pivot
    num_queries += 1  # select allocine_theater
    num_queries += 1  # select provider
    with testing.assert_num_queries(num_queries):
        response = client.get(f"/venueProviders/{venue_id}")
        assert response.status_code == 200

    assert len(response.json) == 2
    assert {
        "enabledForPro": True,
        "id": allocine_provider.id,
        "isActive": True,
        "name": "Allociné",
        "hasOffererProvider": False,
    } in response.json
    assert {
        "enabledForPro": True,
        "id": other_provider.id,
        "isActive": True,
        "name": other_provider.name,
        "hasOffererProvider": False,
    } in response.json


@pytest.mark.usefixtures("db_session")
def test_venue_has_no_allocine_id(client):
    user = users_factories.UserFactory(email="user@example.com")
    venue = offerers_factories.VenueFactory()

    allocine_provider = providers_factories.AllocineProviderFactory()
    other_provider = providers_factories.ProviderFactory(localClass="B provider")

    client = client.with_session_auth(email=user.email)
    venue_id = venue.id
    db.session.expire_all()
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select venue
    num_queries += 1  # select cinema_provider_pivot
    num_queries += 1  # select allocine_pivot
    num_queries += 1  # select allocine_theater
    num_queries += 1  # select provider
    with testing.assert_num_queries(num_queries):
        response = client.get(f"/venueProviders/{venue_id}")
        assert response.status_code == 200

    assert len(response.json) == 1
    assert {
        "enabledForPro": True,
        "id": other_provider.id,
        "isActive": True,
        "name": other_provider.name,
        "hasOffererProvider": False,
    } in response.json
    assert allocine_provider.id not in [p["id"] for p in response.json]


@pytest.mark.usefixtures("db_session")
def test_venue_has_offerer_provider(client):
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

    client = client.with_session_auth(email=user.email)
    venue_id = venue.id
    db.session.expire_all()
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select venue
    num_queries += 1  # select cinema_provider_pivot
    num_queries += 1  # select allocine_pivot
    num_queries += 1  # select allocine_theater
    num_queries += 1  # select provider
    with testing.assert_num_queries(num_queries):
        response = client.get(f"/venueProviders/{venue_id}")
        assert response.status_code == 200

    assert response.status_code == 200
    assert len(response.json) == 1
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

    client = client.with_session_auth(email=user.email)
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select venue
    num_queries += 1  # rollback
    with testing.assert_num_queries(num_queries):
        response = client.get("/venueProviders/1234")
        assert response.status_code == 404


@pytest.mark.usefixtures("db_session")
def test_user_is_not_logged_in(client):
    with testing.assert_num_queries(0):
        response = client.get("/venueProviders/1234")
        assert response.status_code == 401
