import pytest

from pcapi.core import testing
from pcapi.routes.public.individual_offers.v1.serialization import ALLOWED_PRODUCT_SUBCATEGORIES

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


pytestmark = pytest.mark.usefixtures("db_session")


class GetProductCategoriesTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/offers/v1/products/categories"
    endpoint_method = "get"

    def test_returns_all_selectable_categories(self):
        plain_api_key, _ = self.setup_provider()

        with testing.assert_num_queries(1):
            response = self.make_request(plain_api_key)
            assert response.status_code == 200

        assert set(subcategory["id"] for subcategory in response.json) == set(
            subcategory.id for subcategory in ALLOWED_PRODUCT_SUBCATEGORIES
        )

    def test_category_serialization(self):
        plain_api_key, _ = self.setup_provider()

        with testing.assert_num_queries(1):
            response = self.make_request(plain_api_key)
            assert response.status_code == 200

        assert all(
            {"id", "conditionalFields", "locationType"} == set(category_response.keys())
            for category_response in response.json
        )

        concert_response = next(
            subcategory for subcategory in response.json if subcategory["id"] == "SPECTACLE_ENREGISTRE"
        )
        assert concert_response["conditionalFields"] == {
            "author": False,
            "showType": True,
            "stageDirector": False,
            "performer": False,
        }
        assert concert_response["locationType"] == "DIGITAL"
