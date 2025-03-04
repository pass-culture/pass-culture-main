import pytest

from pcapi.core import testing
from pcapi.core.providers.constants import GTL_ID_BY_TITELIVE_MUSIC_GENRE

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


pytestmark = pytest.mark.usefixtures("db_session")


class GetAllTiteliveMusicTypesTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/offers/v1/music_types/event"
    endpoint_method = "get"

    num_queries = 1  # select api_key, offerer and provider

    def test_returns_event_titelive_music_types(self, client):
        plain_api_key, _ = self.setup_provider()

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url)
            assert response.status_code == 200

        assert set(music_type["id"] for music_type in response.json) == {
            genre
            for genre, gtl_id in GTL_ID_BY_TITELIVE_MUSIC_GENRE.items()
            if gtl_id[:2] not in ["03", "15", "16", "18"]
        }

    def test_music_serialization(self, client):
        plain_api_key, _ = self.setup_provider()

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url)
            assert response.status_code == 200

        response = next(music_type for music_type in response.json if music_type["id"] == "FUNK-SOUL-RNB-DISCO")
        assert response == {"id": "FUNK-SOUL-RNB-DISCO", "label": "Funk / Soul / RnB / Disco"}
