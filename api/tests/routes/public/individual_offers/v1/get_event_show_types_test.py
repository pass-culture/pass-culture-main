import pytest

from pcapi.core import testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.domain import show_types

from . import utils


pytestmark = pytest.mark.usefixtures("db_session")


def test_returns_all_show_types(client):
    utils.create_offerer_provider_linked_to_venue()

    client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
    with testing.assert_num_queries(2):
        response = client.get("/public/offers/v1/show_types")

    assert response.status_code == 200
    assert set(show_type["id"] for show_type in response.json) == set(show_types.SHOW_SUB_TYPES_BY_SLUG)


def test_show_type_serialization(client):
    utils.create_offerer_provider_linked_to_venue()

    client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
    with testing.assert_num_queries(2):
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            "/public/offers/v1/show_types"
        )

    assert response.status_code == 200
    assert all({"id", "label"} == set(show_type_response.keys()) for show_type_response in response.json)

    musical_response = next(
        show_type for show_type in response.json if show_type["id"] == "SPECTACLE_MUSICAL-COMEDIE_MUSICALE"
    )
    assert musical_response == {"id": "SPECTACLE_MUSICAL-COMEDIE_MUSICALE", "label": "Comédie Musicale"}
