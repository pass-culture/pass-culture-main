import pytest

from pcapi.core.offerers.factories import ProviderFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.providers.factories import AllocinePivotFactory
from pcapi.core.users.factories import UserFactory
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
def test_venue_has_known_allocine_id(app):
    # Given
    user = UserFactory()
    venue = VenueFactory(siret="12345678912345")
    AllocinePivotFactory(siret="12345678912345")

    allocine_provider = ProviderFactory(localClass="AllocineStocks")
    other_provider = ProviderFactory(localClass="B provider")

    # When
    client = TestClient(app.test_client()).with_auth(email=user.email)
    response = client.get(f"/providers/{humanize(venue.id)}")

    # Then
    assert response.status_code == 200
    returned_providers = sorted(response.json, key=lambda d: d["localClass"])
    assert len(returned_providers) == 5
    assert returned_providers[:2] == [
        {
            "enabledForPro": True,
            "id": humanize(allocine_provider.id),
            "isActive": True,
            "localClass": "AllocineStocks",
            "name": "Allociné",
        },
        {
            "enabledForPro": True,
            "id": humanize(other_provider.id),
            "isActive": True,
            "localClass": other_provider.localClass,
            "name": other_provider.name,
        },
    ]


@pytest.mark.usefixtures("db_session")
def test_venue_has_no_allocine_id(app):
    # Given
    user = UserFactory(email="user@example.com")
    venue = VenueFactory()

    allocine_provider = ProviderFactory(localClass="AllocineStocks")
    other_provider = ProviderFactory(localClass="B provider")

    # When
    client = TestClient(app.test_client()).with_auth(email=user.email)
    response = client.get(f"/providers/{humanize(venue.id)}")

    # Then
    assert response.status_code == 200
    returned_providers = sorted(response.json, key=lambda d: d["localClass"])
    assert len(returned_providers) == 4
    assert returned_providers[0] == {
        "enabledForPro": True,
        "id": humanize(other_provider.id),
        "isActive": True,
        "localClass": other_provider.localClass,
        "name": other_provider.name,
    }
    assert humanize(allocine_provider.id) not in [p["id"] for p in returned_providers]


@pytest.mark.usefixtures("db_session")
def test_venue_does_not_exist(app):
    user = UserFactory()

    client = TestClient(app.test_client()).with_auth(email=user.email)
    response = client.get("/providers/AZER")

    assert response.status_code == 404


@pytest.mark.usefixtures("db_session")
def test_user_is_not_logged_in(app):
    client = TestClient(app.test_client())
    response = client.get("/providers/AZER")

    assert response.status_code == 401
