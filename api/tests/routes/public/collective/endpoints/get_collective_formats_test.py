import pytest

from pcapi.core.categories.models import EacFormat

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


pytestmark = pytest.mark.usefixtures("db_session")


class GetCollectiveFormatsTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/v2/collective/offers/formats"
    endpoint_method = "get"

    def test_get_formats(self):
        plain_api_key, _ = self.setup_provider()

        response = self.make_request(plain_api_key)

        assert response.status_code == 200
        assert sorted([{"name": fmt.value, "id": fmt.name} for fmt in EacFormat], key=lambda x: x["id"]) == sorted(
            response.json, key=lambda x: x["id"]
        )
