import pytest

from pcapi.connectors.api_allocine import ALLOCINE_API_URL
from pcapi.core.offers.models import Product
from pcapi.core.providers import constants as providers_constants
from pcapi.core.providers.allocine_movie_list import synchronize_products
from pcapi.core.providers.models import Provider

from tests.domain import fixtures


@pytest.mark.usefixtures("db_session")
class AllocineMovieListTest:
    def _configure_api_responses(self, requests_mock):
        requests_mock.get(f"{ALLOCINE_API_URL}/movieList?after=", json=fixtures.ALLOCINE_MOVIE_LIST_PAGE_1)
        requests_mock.get(
            f"{ALLOCINE_API_URL}/movieList?after=YXJyYXljb25uZWN0aW9uOjQ5",
            json=fixtures.ALLOCINE_MOVIE_LIST_PAGE_2,
        )

    def test_synchronize_products_creates_products(self, requests_mock):
        # Given
        self._configure_api_responses(requests_mock)
        assert Product.query.count() == 0

        # When
        synchronize_products()

        # Then
        catalogue = Product.query.order_by(Product.id).all()
        assert len(catalogue) == 5

        allocine_products_provider = Provider.query.filter(
            Provider.name == providers_constants.ALLOCINE_PRODUCTS_PROVIDER_NAME
        ).one()
        assert all(product.lastProviderId == allocine_products_provider.id for product in catalogue)
        assert all(
            product.idAtProviders == f"{allocine_products_provider.id}:{product.extraData['allocineId']}"
            for product in catalogue
        )

        movie_data = catalogue[0].extraData
        expected_data = fixtures.ALLOCINE_MOVIE_LIST_PAGE_1["movieList"]["edges"][0]["node"]
        assert movie_data["allocineId"] == expected_data["internalId"]
        assert movie_data["backlink"] == expected_data["backlink"]["url"]
        assert movie_data["cast"] == [
            f"{item['node']['actor']['firstName']} {item['node']['actor']['lastName']}"
            for item in expected_data["cast"]["edges"]
        ]
        assert movie_data["companies"] == [
            {"activity": company["activity"], "name": company["company"]["name"]}
            for company in expected_data["companies"]
        ]
        assert movie_data["countries"] == [country["name"] for country in expected_data["countries"]]
        assert movie_data["credits"] == [expected_data["credits"]["edges"][0]["node"]]
        assert movie_data["eidr"] == expected_data["data"]["eidr"]
        assert movie_data["productionYear"] == expected_data["data"]["productionYear"]
        assert "diffusionVersion" not in movie_data
        assert movie_data["genres"] == expected_data["genres"]
        assert movie_data["originalTitle"] == expected_data["originalTitle"]
        assert movie_data["posterUrl"] == expected_data["poster"]["url"]
        assert movie_data["releaseDate"] == expected_data["releases"][0]["releaseDate"]["date"]
        assert movie_data["runtime"] == 21
        assert movie_data["synopsis"] == expected_data["synopsis"]
        assert "theater" not in movie_data
        assert movie_data["title"] == expected_data["title"]
        assert movie_data["type"] == expected_data["type"]

    def test_synchronize_products_updates_products(self, requests_mock):
        # Given
        self._configure_api_responses(requests_mock)
        assert Product.query.count() == 0
        synchronize_products()
        requests_mock.get(f"{ALLOCINE_API_URL}/movieList?after=", json=fixtures.ALLOCINE_MOVIE_LIST_PAGE_1_UPDATED)

        # When
        synchronize_products()

        # Then
        updated_product = Product.query.order_by(Product.id).first()
        assert updated_product.extraData["title"] == "Nouveau titre pour ceux de chez nous"

    def test_synchronize_products_is_idempotent(self, requests_mock):
        # Given
        self._configure_api_responses(requests_mock)
        assert Product.query.count() == 0

        # When
        synchronize_products()
        old_catalogue = Product.query.order_by(Product.id).all()
        synchronize_products()
        new_catalogue = Product.query.order_by(Product.id).all()

        # Then
        assert all(new_product.__dict__ == old_catalogue[idx].__dict__ for idx, new_product in enumerate(new_catalogue))
