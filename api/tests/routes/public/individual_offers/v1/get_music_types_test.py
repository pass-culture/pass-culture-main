import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers.constants import MUSIC_SLUG_BY_GTL_ID
from pcapi.domain import music_types

from . import utils


pytestmark = pytest.mark.usefixtures("db_session")


def test_returns_all_music_types(client):
    utils.create_offerer_provider_linked_to_venue()

    response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get("/public/offers/v1/music_types")

    assert response.status_code == 200
    assert set(music_type["id"] for music_type in response.json) == set(music_types.MUSIC_SUB_TYPES_BY_SLUG)
    reponse_gtl_ids = set(music_type["gtlId"] for music_type in response.json)
    assert all(gtl_id in MUSIC_SLUG_BY_GTL_ID if gtl_id else True for gtl_id in reponse_gtl_ids)


def test_music_serialization(client):
    utils.create_offerer_provider_linked_to_venue()

    response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get("/public/offers/v1/music_types")

    assert response.status_code == 200

    response = next(music_type for music_type in response.json if music_type["id"] == "JAZZ-MANOUCHE")
    assert response == {"gtlId": "02070000", "id": "JAZZ-MANOUCHE", "label": "Manouche"}
