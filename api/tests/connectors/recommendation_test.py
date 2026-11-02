import json
import urllib.parse

import pytest

import pcapi.core.artist.factories as artist_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.connectors import recommendation
from pcapi.utils import requests


@pytest.mark.settings(
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
        assert query["user_id"] == str(user.id)
        assert mocked.last_request.headers["X-API-Key"] == "secret token"

    def test_without_user(self, requests_mock):
        mocked = requests_mock.get(
            "https://example.com/recommendation/similar_offers/1",
            content=b"raw response",
        )

        response = recommendation.get_similar_offers(offer_id=1, user=None)

        assert response == b"raw response"
        query = dict(urllib.parse.parse_qsl(mocked.last_request.query))
        assert query == {}
        assert mocked.last_request.headers["X-API-Key"] == "secret token"

    def test_params(self, requests_mock):
        mocked = requests_mock.get(
            "https://example.com/recommendation/similar_offers/1",
            content=b"raw response",
        )

        response = recommendation.get_similar_offers(offer_id=1, params={"foo": "bar"})

        assert response == b"raw response"
        query = dict(urllib.parse.parse_qsl(mocked.last_request.query))
        assert query == {"foo": "bar"}
        assert mocked.last_request.headers["X-API-Key"] == "secret token"

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


@pytest.mark.settings(
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
        assert mocked.last_request.headers["X-API-Key"] == "secret token"

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
        assert mocked.last_request.headers["X-API-Key"] == "secret token"
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


@pytest.mark.usefixtures("db_session")
@pytest.mark.settings(RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.LocalBackend")
class LocalBackendTest:
    def test_get_similar_offers(self):
        offer_ids = {str(offer.id) for offer in offers_factories.OfferFactory.create_batch(5)}

        response = json.loads(recommendation.get_similar_offers(offer_id=1))

        assert len(response["results"]) == 3
        assert len(set(response["results"])) == 3
        assert set(response["results"]) <= offer_ids

    def test_get_offer_page_playlists(self):
        offer_ids = {str(offer.id) for offer in offers_factories.OfferFactory.create_batch(12)}

        response = json.loads(recommendation.get_offer_page_playlists(offer_id=42))

        assert response["offer_id"] == "42"
        assert len(response["playlists"]) == 2
        for playlist in response["playlists"]:
            assert len(playlist["results"]) == 10
            assert set(playlist["results"]) <= offer_ids

    def test_get_playlist(self):
        user = users_factories.UserFactory()
        offer_ids = {str(offer.id) for offer in offers_factories.OfferFactory.create_batch(5)}

        response = json.loads(recommendation.get_playlist(user))

        assert len(response["playlist_recommended_offers"]) == 3
        assert set(response["playlist_recommended_offers"]) <= offer_ids

    def test_get_similar_artists(self):
        artist_ids = {artist.id for artist in artist_factories.ArtistFactory.create_batch(5)}

        response = json.loads(recommendation.get_similar_artists(artist_id="some-artist-id"))

        # the route reads `artist_id_match` from each item
        assert len(response["similar_artists"]) == 3
        assert {item["artist_id_match"] for item in response["similar_artists"]} <= artist_ids
        assert response["params"]["artist_id"] == "some-artist-id"

    def test_get_top_artists_playlist(self):
        artist_ids = {artist.id for artist in artist_factories.ArtistFactory.create_batch(5)}

        response = json.loads(recommendation.get_top_artists_playlist("musique"))

        assert len(response["playlist_artists"]) == 3
        assert set(response["playlist_artists"]) <= artist_ids
        assert response["params"]["search_group_name"] == "musique"

    def test_get_top_artists_playlist_unknown_category(self):
        with pytest.raises(recommendation.RecommendationApiValidationException):
            recommendation.get_top_artists_playlist("unknown")

    def test_empty_database(self):
        assert json.loads(recommendation.get_similar_offers(offer_id=1))["results"] == []
        assert json.loads(recommendation.get_similar_artists(artist_id="some-artist-id"))["similar_artists"] == []
