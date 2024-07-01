import json
import urllib.parse

from pcapi.core import testing
import pcapi.core.users.factories as users_factories
from pcapi.utils import requests


class SimilarOffersTest:
    def test_anonymous(self, client):
        with testing.assert_num_queries(0):
            response = client.get("/native/v1/recommendation/similar_offers/2")
            assert response.status_code == 200
        assert response.json["results"] == ["20", "21", "22"]

    def test_authenticated(self, client, db_session):
        user = users_factories.UserFactory(id=3)

        client = client.with_token(user.email)

        # User authentication
        with testing.assert_num_queries(1):
            response = client.get("/native/v1/recommendation/similar_offers/2")
            assert response.status_code == 200

        assert response.json["results"] == ["320", "321", "322"]

    @testing.override_settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_forward_params_to_recommendation_api(self, requests_mock, client):
        mocked = requests_mock.get("https://example.com/recommendation/similar_offers/2")

        with testing.assert_num_queries(0):
            response = client.get("/native/v1/recommendation/similar_offers/2", params={"longitude": 12.23})
            assert response.status_code == 200
        query = dict(urllib.parse.parse_qsl(mocked.last_request.query))
        assert query["longitude"] == "12.23"

    @testing.override_settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_forward_params_as_list_to_recommendation_api(self, requests_mock, client):
        mocked = requests_mock.get("https://example.com/recommendation/similar_offers/2")
        with testing.assert_num_queries(0):
            response = client.get(
                "/native/v1/recommendation/similar_offers/2", params={"categories": "TEST_CATEGORY,TEST_CATEGORY2"}
            )
            assert response.status_code == 200
        query = urllib.parse.parse_qsl(mocked.last_request.query)
        assert query == [("categories", "TEST_CATEGORY"), ("categories", "TEST_CATEGORY2")]

    @testing.override_settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_failure(self, requests_mock, client):
        requests_mock.get(
            "https://example.com/recommendation/similar_offers/2",
            exc=requests.exceptions.ConnectTimeout("a timeout error"),
        )
        with testing.assert_num_queries(0):
            response = client.get("/native/v1/recommendation/similar_offers/2")
            assert response.status_code == 400
        assert response.json == {"code": "RECOMMENDATION_API_ERROR"}


class PlaylistTest:
    def test_anonymous(self, client):
        with testing.assert_num_queries(0):
            response = client.post("/native/v1/recommendation/playlist")
            assert response.status_code == 401

    def test_authenticated(self, client, db_session):
        user = users_factories.UserFactory(id=3)

        client = client.with_token(user.email)
        # User authentication
        with testing.assert_num_queries(1):
            response = client.post("/native/v1/recommendation/playlist")
            assert response.status_code == 200

        assert response.json["playlistRecommendedOffers"] == ["300", "301", "302"]

    @testing.override_settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_forward_params_to_recommendation_api(self, requests_mock, client, db_session):
        user = users_factories.UserFactory(id=3)
        mocked = requests_mock.post("https://example.com/recommendation/playlist_recommendation/3")

        client = client.with_token(user.email)

        # User authentication
        with testing.assert_num_queries(1):
            response = client.post("/native/v1/recommendation/playlist?modelEndpoint=dummy", json={"isEvent": True})
            assert response.status_code == 200
        query = dict(urllib.parse.parse_qsl(mocked.last_request.query))
        assert query["modelEndpoint"] == "dummy"
        body = json.loads(mocked.last_request.body)
        assert body["isEvent"] is True

    @testing.override_settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_failure(self, requests_mock, client, db_session):
        user = users_factories.UserFactory(id=3)
        requests_mock.post(
            "https://example.com/recommendation/playlist_recommendation/3",
            exc=requests.exceptions.ConnectTimeout("a timeout error"),
        )

        client = client.with_token(user.email)
        # User authentication
        with testing.assert_num_queries(1):
            response = client.post("/native/v1/recommendation/playlist")
            assert response.status_code == 400

        assert response.json == {"code": "RECOMMENDATION_API_ERROR"}
