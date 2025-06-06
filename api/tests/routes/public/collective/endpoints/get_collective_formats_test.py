import pytest

from pcapi.core.categories.models import EacFormat

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


pytestmark = pytest.mark.usefixtures("db_session")


class GetCollectiveFormatsTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/v2/collective/offers/formats"
    endpoint_method = "get"

    def test_get_formats(self, client):
        plain_api_key, _ = self.setup_provider()

        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url)

        assert response.status_code == 200
        assert sorted([{"name": fmt.value, "id": fmt.name} for fmt in EacFormat], key=lambda x: x["id"]) == sorted(
            response.json, key=lambda x: x["id"]
        )

    def test_should_raise_401_because_api_key_not_linked_to_provider(self, client):
        num_queries = 2  # Select API key + rollback
        super().test_should_raise_401_because_api_key_not_linked_to_provider(client, num_queries=num_queries)
