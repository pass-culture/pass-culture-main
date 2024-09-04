import pytest

from pcapi.core import testing
from pcapi.domain import show_types

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


pytestmark = pytest.mark.usefixtures("db_session")


class GetShowTypesTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/offers/v1/show_types"
    endpoint_method = "get"

    num_queries = 1  # select api_key, offerer and provider
    num_queries += 1  # select features

    def test_returns_all_show_types(self, client):
        plain_api_key, _ = self.setup_provider()
        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url)
            assert response.status_code == 200

        assert set(show_type["id"] for show_type in response.json) == set(show_types.SHOW_SUB_TYPES_BY_SLUG)

    def test_show_type_serialization(self, client):
        plain_api_key, _ = self.setup_provider()

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url)
            assert response.status_code == 200

        assert all({"id", "label"} == set(show_type_response.keys()) for show_type_response in response.json)
        musical_response = next(
            show_type for show_type in response.json if show_type["id"] == "SPECTACLE_MUSICAL-COMEDIE_MUSICALE"
        )
        assert musical_response == {"id": "SPECTACLE_MUSICAL-COMEDIE_MUSICALE", "label": "Comédie Musicale"}
