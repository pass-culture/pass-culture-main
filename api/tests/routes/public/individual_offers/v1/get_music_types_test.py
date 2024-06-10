import pytest

from pcapi.core import testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.domain import music_types

from . import utils


pytestmark = pytest.mark.usefixtures("db_session")


def test_returns_all_music_types(client):
    utils.create_offerer_provider_linked_to_venue()

    client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
    with testing.assert_num_queries(2):
        response = client.get("/public/offers/v1/music_types")

        assert response.status_code == 200
        assert set(music_type["id"] for music_type in response.json) == set(music_types.MUSIC_SUB_TYPES_BY_SLUG)


def test_music_serialization(client):
    utils.create_offerer_provider_linked_to_venue()

    client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
    with testing.assert_num_queries(2):
        response = client.get("/public/offers/v1/music_types")

        assert response.status_code == 200

        response = next(music_type for music_type in response.json if music_type["id"] == "JAZZ-MANOUCHE")
        assert response == {"id": "JAZZ-MANOUCHE", "label": "Manouche"}
