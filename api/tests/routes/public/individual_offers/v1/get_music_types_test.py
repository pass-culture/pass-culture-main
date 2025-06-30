import pytest

from pcapi.core import testing
from pcapi.core.categories.genres import music

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


pytestmark = pytest.mark.usefixtures("db_session")


class GetMusicTypesTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/offers/v1/music_types"
    endpoint_method = "get"

    def test_returns_all_music_types(self):
        plain_api_key, _ = self.setup_provider()

        with testing.assert_num_queries(1):
            response = self.make_request(plain_api_key)
            assert response.status_code == 200

        assert set(music_type["id"] for music_type in response.json) == set(music.MUSIC_SUB_TYPES_BY_SLUG)

    def test_music_serialization(self):
        plain_api_key, _ = self.setup_provider()

        with testing.assert_num_queries(1):
            response = self.make_request(plain_api_key)
            assert response.status_code == 200

        response = next(music_type for music_type in response.json if music_type["id"] == "JAZZ-MANOUCHE")
        assert response == {"id": "JAZZ-MANOUCHE", "label": "Manouche"}
