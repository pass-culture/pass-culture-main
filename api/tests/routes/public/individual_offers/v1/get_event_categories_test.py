import pytest

from pcapi.core import testing
from pcapi.core.categories import subcategories

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


pytestmark = pytest.mark.usefixtures("db_session")

num_queries = 1  # select api_key, offerer and provider


@pytest.mark.usefixtures("db_session")
class GetEventCategoriesTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/offers/v1/events/categories"
    endpoint_method = "get"

    def test_returns_all_selectable_categories(self, client):
        plain_api_key, _ = self.setup_provider()

        with testing.assert_num_queries(num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url)
            assert response.status_code == 200

        assert set(subcategory["id"] for subcategory in response.json) == set(
            subcategory_id
            for subcategory_id, subcategory in subcategories.EVENT_SUBCATEGORIES.items()
            if subcategory.is_selectable
        )

    def test_category_serialization(self, client):
        plain_api_key, _ = self.setup_provider()

        with testing.assert_num_queries(num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url)
            assert response.status_code == 200

        assert all({"id", "conditionalFields"} == set(category_response.keys()) for category_response in response.json)

        concert_response = next(subcategory for subcategory in response.json if subcategory["id"] == "CONCERT")
        assert concert_response["conditionalFields"] == {
            "author": False,
            "musicSubType": False,
            "musicType": True,
            "gtl_id": False,
            "performer": False,
        }
