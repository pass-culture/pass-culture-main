from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
from pcapi.utils import requests


class SimilarOffersTest:
    def test_anonymous(self, client):
        response = client.get("/native/v1/recommendation/similar_offers/2")
        assert response.status_code == 200
        assert response.json["results"] == ["20", "21", "22"]

    def test_authenticated(self, client, db_session):
        user = users_factories.UserFactory(id=3)

        client = client.with_token(user.email)
        response = client.get("/native/v1/recommendation/similar_offers/2")

        assert response.status_code == 200
        assert response.json["results"] == ["320", "321", "322"]

    @override_settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_AUTHENTICATION_TOKEN="secret token",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_failure(self, requests_mock, client):
        requests_mock.get(
            "https://example.com/recommendation/similar_offers/2",
            exc=requests.exceptions.ConnectTimeout("a timeout error"),
        )

        response = client.get("/native/v1/recommendation/similar_offers/2")

        assert response.status_code == 400
        assert response.json == {"code": "RECOMMENDATION_API_ERROR"}


class PlaylistTest:
    def test_anonymous(self, client):
        response = client.post("/native/v1/recommendation/playlist")
        assert response.status_code == 401

    def test_authenticated(self, client, db_session):
        user = users_factories.UserFactory(id=3)

        client = client.with_token(user.email)
        response = client.post("/native/v1/recommendation/playlist")

        assert response.status_code == 200
        assert response.json["playlist_recommended_offers"] == ["300", "301", "302"]

    @override_settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_AUTHENTICATION_TOKEN="secret token",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_failure(self, requests_mock, client):
        user = users_factories.UserFactory(id=3)
        requests_mock.post(
            "https://example.com/recommendation/playlist_recommendation/3",
            exc=requests.exceptions.ConnectTimeout("a timeout error"),
        )

        client = client.with_token(user.email)
        response = client.post("/native/v1/recommendation/playlist")

        assert response.status_code == 400
        assert response.json == {"code": "RECOMMENDATION_API_ERROR"}
