import json
import urllib.parse

import pytest

from pcapi.connectors import recommendation
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
from pcapi.utils import requests


@override_settings(
    RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
    RECOMMENDATION_API_AUTHENTICATION_TOKEN="secret token",
    RECOMMENDATION_API_URL="https://example.com/recommendation/",
)
class GetSimilarOffersTest:
    def test_with_user(self, requests_mock, db_session):
        user = users_factories.UserFactory()
        mocked = requests_mock.get(
            "https://example.com/recommendation/similar_offers/1",
            content=b"raw response",
        )

        response = recommendation.get_similar_offers(offer_id=1, user=user)

        assert response == b"raw response"
        query = dict(urllib.parse.parse_qsl(mocked.last_request.query))
        assert query["userId"] == str(user.id)
        assert query["token"] == "secret token"

    def test_without_user(self, requests_mock):
        mocked = requests_mock.get(
            "https://example.com/recommendation/similar_offers/1",
            content=b"raw response",
        )

        response = recommendation.get_similar_offers(
            offer_id=1, user=None, params={"userId": "overridden", "user_id": "overridden"}
        )

        assert response == b"raw response"
        query = dict(urllib.parse.parse_qsl(mocked.last_request.query))
        assert query == {"token": "secret token"}

    def test_params(self, requests_mock):
        mocked = requests_mock.get(
            "https://example.com/recommendation/similar_offers/1",
            content=b"raw response",
        )

        response = recommendation.get_similar_offers(offer_id=1, params={"foo": "bar"})

        assert response == b"raw response"
        query = dict(urllib.parse.parse_qsl(mocked.last_request.query))
        assert query == {"token": "secret token", "foo": "bar"}

    def test_timeout_failure(self, requests_mock):
        requests_mock.get(
            "https://example.com/recommendation/similar_offers/1",
            exc=requests.exceptions.ConnectTimeout("a timeout error"),
        )

        with pytest.raises(recommendation.RecommendationApiTimeoutException) as err:
            recommendation.get_similar_offers(
                offer_id=1, user=None, params={"userId": "overridden", "user_id": "overridden"}
            )
        assert str(err.value) == ""

    def test_generic_failure(self, requests_mock):
        requests_mock.get(
            "https://example.com/recommendation/similar_offers/1",
            exc=requests.exceptions.TooManyRedirects("too many redirects"),
        )

        with pytest.raises(recommendation.RecommendationApiException) as err:
            recommendation.get_similar_offers(
                offer_id=1, user=None, params={"userId": "overridden", "user_id": "overridden"}
            )
        assert str(err.value) == "too many redirects"


@override_settings(
    RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
    RECOMMENDATION_API_AUTHENTICATION_TOKEN="secret token",
    RECOMMENDATION_API_URL="https://example.com/recommendation/",
)
@pytest.mark.usefixtures("db_session")
class GetPlaylistTest:
    def test_basics(self, requests_mock):
        user = users_factories.UserFactory(id=1)
        mocked = requests_mock.post(
            "https://example.com/recommendation/playlist_recommendation/1",
            content=b"raw response",
        )

        response = recommendation.get_playlist(user)

        assert response == b"raw response"
        query = dict(urllib.parse.parse_qsl(mocked.last_request.query))
        assert query["token"] == "secret token"

    def test_params(self, requests_mock):
        user = users_factories.UserFactory(id=1)
        mocked = requests_mock.post(
            "https://example.com/recommendation/playlist_recommendation/1",
            content=b"raw response",
        )

        response = recommendation.get_playlist(
            user,
            params={"query_param": "foo"},
            body={"body_param": "bar"},
        )

        assert response == b"raw response"
        query = dict(urllib.parse.parse_qsl(mocked.last_request.query))
        assert query["token"] == "secret token"
        assert query["query_param"] == "foo"
        body = json.loads(mocked.last_request.body)
        assert body == {"body_param": "bar"}

    def test_timeout_failure(self, requests_mock):
        requests_mock.post(
            "https://example.com/recommendation/playlist_recommendation/1",
            exc=requests.exceptions.ConnectTimeout("a timeout error"),
        )
        user = users_factories.UserFactory(id=1)

        with pytest.raises(recommendation.RecommendationApiTimeoutException) as err:
            recommendation.get_playlist(user)
        assert str(err.value) == ""

    def test_generic_failure(self, requests_mock):
        requests_mock.post(
            "https://example.com/recommendation/playlist_recommendation/1",
            exc=requests.exceptions.TooManyRedirects("too many requests"),
        )
        user = users_factories.UserFactory(id=1)

        with pytest.raises(recommendation.RecommendationApiException) as err:
            recommendation.get_playlist(user)
        assert str(err.value) == "too many requests"
