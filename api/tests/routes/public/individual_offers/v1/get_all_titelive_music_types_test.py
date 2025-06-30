import pytest

from pcapi.core import testing
from pcapi.core.providers.constants import GTL_ID_BY_TITELIVE_MUSIC_GENRE

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


pytestmark = pytest.mark.usefixtures("db_session")


class GetAllTiteliveMusicTypesTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/offers/v1/music_types/all"
    endpoint_method = "get"

    num_queries = 1  # select api_key, offerer and provider

    def test_returns_all_titelive_music_types(self):
        plain_api_key, _ = self.setup_provider()
        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key=plain_api_key)
            assert response.status_code == 200

        assert set(music_type["id"] for music_type in response.json) == set(GTL_ID_BY_TITELIVE_MUSIC_GENRE)

    def test_music_serialization(self, client):
        plain_api_key, _ = self.setup_provider()

        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key=plain_api_key)
            assert response.status_code == 200

        response = next(music_type for music_type in response.json if music_type["id"] == "VIDEOS_MUSICALES")
        assert response == {"id": "VIDEOS_MUSICALES", "label": "Vidéos musicales"}
