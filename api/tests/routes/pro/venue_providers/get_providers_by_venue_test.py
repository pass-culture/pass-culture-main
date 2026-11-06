import pytest

from pcapi.core import testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as providers_factories
from pcapi.core.users import factories as users_factories
from pcapi.models.api_errors import OBJECT_NOT_FOUND_ERROR_MESSAGE

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")

NUM_QUERIES = testing.AUTHENTICATION_QUERIES
NUM_QUERIES += 1  # select venue
NUM_QUERIES += 1  # check venue access
NUM_QUERIES += 1  # select cinema_provider_pivot
NUM_QUERIES += 1  # select allocine_pivot
NUM_QUERIES += 1  # select allocine_theater
NUM_QUERIES += 1  # select provider


def test_venue_has_known_allocine_id(client: TestClient):
    user = users_factories.ProFactory()
    user_offerer = offerers_factories.UserOffererFactory(user=user)
    venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    providers_factories.AllocineTheaterFactory(siret=venue.siret)

    allocine_provider = providers_factories.AllocineProviderFactory()
    other_provider = providers_factories.ProviderFactory(localClass="B provider")

    client = client.with_session_auth(email=user.email)
    venue_id = venue.id
    with testing.assert_num_queries(NUM_QUERIES):
        response = client.get(f"/venues/{venue_id}/providers")
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


def test_venue_has_no_allocine_id(client: TestClient):
    user = users_factories.ProFactory()
    user_offerer = offerers_factories.UserOffererFactory(user=user)
    venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

    allocine_provider = providers_factories.AllocineProviderFactory()
    other_provider = providers_factories.ProviderFactory(localClass="B provider")

    client = client.with_session_auth(email=user.email)
    venue_id = venue.id
    with testing.assert_num_queries(NUM_QUERIES):
        response = client.get(f"/venues/{venue_id}/providers")
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


def test_venue_has_offerer_provider(client: TestClient):
    name = "MangoMusic"
    user = users_factories.ProFactory()
    user_offerer = offerers_factories.UserOffererFactory(user=user)
    venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    provider = providers_factories.ProviderFactory(
        name=name,
        localClass=None,
    )
    providers_factories.OffererProviderFactory(provider=provider)

    providers_factories.VenueProviderFactory(venue=venue, provider=provider)

    client = client.with_session_auth(email=user.email)
    venue_id = venue.id
    with testing.assert_num_queries(NUM_QUERIES):
        response = client.get(f"/venues/{venue_id}/providers")
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


def test_venue_does_not_exist(client: TestClient):
    user = users_factories.ProFactory()

    client = client.with_session_auth(email=user.email)
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select venue
    num_queries += 1  # rollback
    num_queries += 1  # rollback
    with testing.assert_num_queries(num_queries):
        response = client.get("/venues/1234/providers")
        assert response.status_code == 404


def test_user_is_not_logged_in(client: TestClient):
    with testing.assert_num_queries(0):
        response = client.get("/venues/1234/providers")
        assert response.status_code == 401


def test_user_no_access_to_venue(client: TestClient):
    user = users_factories.ProFactory()
    venue = offerers_factories.VenueFactory()
    venue_id = venue.id

    client = client.with_session_auth(email=user.email)
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select venue
    num_queries += 1  # check access to venue
    num_queries += 1  # rollback
    num_queries += 1  # rollback
    with testing.assert_num_queries(num_queries):
        response = client.get(f"/venues/{venue_id}/providers")

    assert response.status_code == 404
    assert response.json == {"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]}
