import pytest

from pcapi.core import testing
from pcapi.core.categories.genres import music

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


pytestmark = pytest.mark.usefixtures("db_session")


class GetMusicTypesTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/offers/v1/music_types"
    endpoint_method = "get"

    num_queries = 1  # select api_key, offerer and provider

    def test_returns_all_music_types(self, client):
        plain_api_key, _ = self.setup_provider()

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url)
            assert response.status_code == 200

        assert set(music_type["id"] for music_type in response.json) == set(music.MUSIC_SUB_TYPES_BY_SLUG)

    def test_music_serialization(self, client):
        plain_api_key, _ = self.setup_provider()

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url)
            assert response.status_code == 200

        response = next(music_type for music_type in response.json if music_type["id"] == "JAZZ-MANOUCHE")
        assert response == {"id": "JAZZ-MANOUCHE", "label": "Manouche"}
