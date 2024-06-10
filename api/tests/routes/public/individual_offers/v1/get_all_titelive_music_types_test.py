import pytest

from pcapi.core import testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers.constants import GTL_ID_BY_TITELIVE_MUSIC_GENRE

from . import utils


pytestmark = pytest.mark.usefixtures("db_session")


def test_returns_all_titelive_music_types(client):
    utils.create_offerer_provider_linked_to_venue()

    client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)

    # Verifiying api_key
    # Feature Flag, should be deleted with WIP_ENABLE_NEW_HASHING_ALGORITHM
    with testing.assert_num_queries(2):
        response = client.get("/public/offers/v1/music_types/all")

        assert response.status_code == 200
        assert set(music_type["id"] for music_type in response.json) == set(GTL_ID_BY_TITELIVE_MUSIC_GENRE)


def test_music_serialization(client):
    utils.create_offerer_provider_linked_to_venue()

    client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)

    # Verifiying api_key
    # Feature Flag, should be deleted with WIP_ENABLE_NEW_HASHING_ALGORITHM
    with testing.assert_num_queries(2):
        response = client.get("/public/offers/v1/music_types/all")

        assert response.status_code == 200

        response = next(music_type for music_type in response.json if music_type["id"] == "VIDEOS_MUSICALES")
        assert response == {"id": "VIDEOS_MUSICALES", "label": "Vidéos musicales"}
