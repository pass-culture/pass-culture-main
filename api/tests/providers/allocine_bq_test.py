import copy
from unittest.mock import patch

import pytest

from pcapi.connectors.serialization import allocine_serializers
from pcapi.core.offers.models import Product
from pcapi.core.providers import constants as providers_constants
from pcapi.core.providers.allocine import synchronize_products_with_bigquery
from pcapi.core.providers.models import LocalProviderEvent
from pcapi.core.providers.models import LocalProviderEventType
from pcapi.core.providers.models import Provider
from pcapi.models import db

from tests.domain import fixtures


@pytest.mark.usefixtures("db_session")
class AllocineSynchronizeProductsWithBigQueryTest:
    def setup_method(self):
        self.allocine_provider = (
            db.session.query(Provider)
            .filter(Provider.name == providers_constants.ALLOCINE_PRODUCTS_PROVIDER_NAME)
            .one()
        )

    def _get_movie_from_fixture(self, fixture):
        movie_data = fixture["movieList"]["edges"][0]["node"]
        return allocine_serializers.AllocineMovie.model_validate(movie_data)

    @patch("pcapi.core.providers.allocine.AllocineMovieQuery")
    def test_synchronize_products_creates_products(self, MockAllocineMovieQuery):
        movie = self._get_movie_from_fixture(fixtures.ALLOCINE_MOVIE_LIST_PAGE_1)
        mock_query_instance = MockAllocineMovieQuery.return_value
        mock_query_instance.execute.return_value = [movie]

        synchronize_products_with_bigquery()

        catalogue = db.session.query(Product).order_by(Product.id).all()
        assert len(catalogue) == 1
        product = catalogue[0]
        assert product.lastProviderId == self.allocine_provider.id

        movie_data = product.extraData
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
        assert "eidr" not in movie_data
        assert movie_data["productionYear"] == expected_data["data"]["productionYear"]
        assert "diffusionVersion" not in movie_data
        assert movie_data["genres"] == expected_data["genres"]
        assert movie_data["originalTitle"] == expected_data["originalTitle"]
        assert movie_data["posterUrl"] == expected_data["poster"]["url"]
        assert movie_data["releaseDate"] == expected_data["releases"][0]["releaseDate"]["date"]
        assert movie_data["runtime"] == 21
        assert movie_data["synopsis"] == "Sacha Guitry filme la France de l\u2019\u00e9poque."
        assert "theater" not in movie_data
        assert movie_data["title"] == expected_data["title"]
        assert movie_data["type"] == expected_data["type"]

    @patch("pcapi.core.providers.allocine.AllocineMovieQuery")
    def test_synchronize_products_updates_products(self, MockAllocineMovieQuery):
        original_movie = self._get_movie_from_fixture(fixtures.ALLOCINE_MOVIE_LIST_PAGE_1)
        mock_query_instance = MockAllocineMovieQuery.return_value
        mock_query_instance.execute.return_value = [original_movie]
        synchronize_products_with_bigquery()
        updated_fixture = copy.deepcopy(fixtures.ALLOCINE_MOVIE_LIST_PAGE_1)
        updated_fixture["movieList"]["edges"][0]["node"]["title"] = "Updated Title"
        updated_movie = self._get_movie_from_fixture(updated_fixture)
        mock_query_instance.execute.return_value = [updated_movie]

        synchronize_products_with_bigquery()

        product = db.session.query(Product).one()
        assert product.extraData["title"] == "Updated Title"

    @patch("pcapi.core.providers.allocine.AllocineMovieQuery")
    def test_synchronize_products_is_idempotent(self, MockAllocineMovieQuery):
        movie = self._get_movie_from_fixture(fixtures.ALLOCINE_MOVIE_LIST_PAGE_1)
        mock_query_instance = MockAllocineMovieQuery.return_value
        # Iterator to simulate multiple calls returning same data
        mock_query_instance.execute.side_effect = [[movie], [movie]]

        synchronize_products_with_bigquery()
        old_catalogue = db.session.query(Product).order_by(Product.id).all()
        synchronize_products_with_bigquery()
        new_catalogue = db.session.query(Product).order_by(Product.id).all()

        assert len(new_catalogue) == len(old_catalogue)
        assert all(
            new_product.extraData == old_catalogue[idx].extraData for idx, new_product in enumerate(new_catalogue)
        )

    @patch("pcapi.core.providers.allocine.AllocineMovieQuery")
    def test_logs_sync_start_and_end_on_success(self, MockAllocineMovieQuery):
        mock_query_instance = MockAllocineMovieQuery.return_value
        mock_query_instance.execute.return_value = []

        synchronize_products_with_bigquery()

        events = (
            db.session.query(LocalProviderEvent)
            .filter(LocalProviderEvent.providerId == self.allocine_provider.id)
            .order_by(LocalProviderEvent.date)
            .all()
        )
        assert len(events) == 2
        assert events[0].type == LocalProviderEventType.SyncStart
        assert events[1].type == LocalProviderEventType.SyncEnd

    @patch("pcapi.core.providers.allocine.AllocineMovieQuery")
    def test_logs_sync_error_on_failure(self, MockAllocineMovieQuery):
        mock_query_instance = MockAllocineMovieQuery.return_value
        mock_query_instance.execute.side_effect = Exception("BQ Error")

        with pytest.raises(Exception):
            synchronize_products_with_bigquery()

        events = (
            db.session.query(LocalProviderEvent)
            .filter(LocalProviderEvent.providerId == self.allocine_provider.id)
            .order_by(LocalProviderEvent.date)
            .all()
        )
        assert len(events) == 2
        assert events[0].type == LocalProviderEventType.SyncStart
        assert events[1].type == LocalProviderEventType.SyncError
        assert events[1].payload == "Exception"

    @patch("pcapi.core.providers.allocine.AllocineMovieQuery")
    def test_handles_invalid_release_date(self, MockAllocineMovieQuery):
        fixture = copy.deepcopy(fixtures.ALLOCINE_MOVIE_LIST_PAGE_1)
        edge = fixture["movieList"]["edges"][0]
        edge["node"]["releases"] = edge["node"]["releases"][:1]
        edge["node"]["releases"][0]["releaseDate"]["date"] = "2024"
        movie = allocine_serializers.AllocineMovie.model_validate(edge["node"])
        mock_query_instance = MockAllocineMovieQuery.return_value
        mock_query_instance.execute.return_value = [movie]

        synchronize_products_with_bigquery()

        product = db.session.query(Product).order_by(Product.id).first()
        assert "releaseDate" not in product.extraData
