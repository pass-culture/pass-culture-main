import json
import urllib.parse

import pytest

import pcapi.core.artist.factories as artist_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing
from pcapi.utils import requests


pytestmark = pytest.mark.usefixtures("db_session")


class SimilarOffersTest:
    def test_get_recommendation_playlist(self, requests_mock, client):
        response = client.get("/native/v1/recommendation/similar_offers/2")

        assert response.status_code == 200
        assert response.json["params"] == {
            "abTest": None,
            "callId": "956bd070-cbb1-42d3-bea4-89855bf3b11c",
            "filtered": None,
            "geoLocated": None,
            "modelEndpoint": None,
            "modelName": None,
            "modelOrigin": "default",
            "modelVersion": None,
            "recoOrigin": "unknown",
            "uniqueCallId": None,
        }
        assert response.json["results"]

    def test_anonymous(self, client):
        with testing.assert_num_queries(0):
            response = client.get("/native/v1/recommendation/similar_offers/2")
            assert response.status_code == 200
        assert response.json["results"] == ["20", "21", "22"]

    def test_authenticated(self, client, db_session):
        user = users_factories.UserFactory(id=3)

        client = client.with_token(user)

        # User authentication
        with testing.assert_num_queries(1):
            response = client.get("/native/v1/recommendation/similar_offers/2")
            assert response.status_code == 200

        assert response.json["results"] == ["320", "321", "322"]

    @pytest.mark.settings(
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
        assert query["retrieval_model"] == "coreservation"

    def test_coreservation_explicit_matches_default(self, client):
        default_response = client.get("/native/v1/recommendation/similar_offers/2")
        explicit_response = client.get(
            "/native/v1/recommendation/similar_offers/2",
            params={"retrievalModel": "coreservation"},
        )

        assert default_response.status_code == 200
        assert explicit_response.status_code == 200
        assert explicit_response.json["results"] == default_response.json["results"]

    @pytest.mark.settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_retrieval_model_defaults_to_coreservation(self, requests_mock, client):
        mocked = requests_mock.get("https://example.com/recommendation/similar_offers/2")

        with testing.assert_num_queries(0):
            response = client.get("/native/v1/recommendation/similar_offers/2")
            assert response.status_code == 200
        query = dict(urllib.parse.parse_qsl(mocked.last_request.query))
        assert query["retrieval_model"] == "coreservation"

    @pytest.mark.settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_retrieval_model_graph_is_forwarded(self, requests_mock, client):
        mocked = requests_mock.get("https://example.com/recommendation/similar_offers/2")

        with testing.assert_num_queries(0):
            response = client.get(
                "/native/v1/recommendation/similar_offers/2",
                params={"retrievalModel": "graph"},
            )
            assert response.status_code == 200
        query = dict(urllib.parse.parse_qsl(mocked.last_request.query))
        assert query["retrieval_model"] == "graph"

    @pytest.mark.settings(
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

        assert query == [
            ("categories", "TEST_CATEGORY"),
            ("categories", "TEST_CATEGORY2"),
            ("retrieval_model", "coreservation"),
        ]

    @pytest.mark.settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_timeout_error(self, requests_mock, client):
        requests_mock.get(
            "https://example.com/recommendation/similar_offers/2",
            exc=requests.exceptions.ConnectTimeout("a timeout error"),
        )
        with testing.assert_num_queries(0):
            response = client.get("/native/v1/recommendation/similar_offers/2")
            assert response.status_code == 504
        assert response.json == {"code": "RECOMMENDATION_API_TIMEOUT"}

    @pytest.mark.settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_generic_error(self, requests_mock, client):
        requests_mock.get(
            "https://example.com/recommendation/similar_offers/2",
            exc=requests.exceptions.TooManyRedirects("a redirect error"),
        )
        with testing.assert_num_queries(0):
            response = client.get("/native/v1/recommendation/similar_offers/2")
            assert response.status_code == 502
        assert response.json == {"code": "RECOMMENDATION_API_ERROR"}

    @pytest.mark.settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_from_cache_field_is_forwarded(self, requests_mock, client):
        requests_mock.get(
            "https://example.com/recommendation/similar_offers/2",
            json={
                "results": ["10", "20", "30"],
                "params": {
                    "reco_origin": "algo",
                    "model_origin": "default",
                    "call_id": "1ead08f9-cfb1-4bb2-98ae-86170c36f0a7",
                    "unique_call_id": "450ab635-e477-407f-bc97-63b892e21810",
                },
                "from_cache": True,
            },
        )

        with testing.assert_num_queries(0):
            response = client.get("/native/v1/recommendation/similar_offers/2")
            assert response.status_code == 200

        assert response.json["fromCache"] is True
        assert response.json["params"]["uniqueCallId"] == "450ab635-e477-407f-bc97-63b892e21810"


class PlaylistTest:
    def test_post_recommendation_playlist(self, requests_mock, client):
        user = users_factories.UserFactory()

        response = client.with_token(user).post("/native/v1/recommendation/playlist", json={})

        assert response.status_code == 200
        assert response.json["params"] == {
            "abTest": None,
            "callId": "1dc4c5f2-303c-4d8a-94c3-77c0085c0c70",
            "filtered": None,
            "geoLocated": None,
            "modelEndpoint": None,
            "modelName": None,
            "modelOrigin": "default",
            "modelVersion": None,
            "recoOrigin": "unknown",
            "uniqueCallId": None,
        }
        assert response.json["playlistRecommendedOffers"]

    def test_anonymous(self, client):
        with testing.assert_num_queries(0):
            response = client.post("/native/v1/recommendation/playlist", json={})
            assert response.status_code == 401

    def test_authenticated(self, client, db_session):
        user = users_factories.UserFactory(id=3)

        client = client.with_token(user)
        # User authentication
        with testing.assert_num_queries(1):
            response = client.post("/native/v1/recommendation/playlist", json={})
            assert response.status_code == 200

        assert response.json["playlistRecommendedOffers"] == ["300", "301", "302"]

    @pytest.mark.settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_forward_params_to_recommendation_api(self, requests_mock, client, db_session):
        user = users_factories.UserFactory(id=3)
        mocked = requests_mock.post("https://example.com/recommendation/playlist_recommendation/3")

        client = client.with_token(user)

        # User authentication
        with testing.assert_num_queries(1):
            response = client.post("/native/v1/recommendation/playlist?modelEndpoint=dummy", json={"isEvent": True})
            assert response.status_code == 200
        query = dict(urllib.parse.parse_qsl(mocked.last_request.query))
        assert query["model_endpoint"] == "dummy"
        body = json.loads(mocked.last_request.body)
        assert body["is_event"] is True

    @pytest.mark.settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    @pytest.mark.parametrize("is_qpi", [True, False])
    def test_forward_is_qpi_to_recommendation_api(self, requests_mock, client, db_session, is_qpi):
        user = users_factories.UserFactory(id=3)
        mocked = requests_mock.post("https://example.com/recommendation/playlist_recommendation/3")

        client = client.with_token(user)

        # User authentication
        with testing.assert_num_queries(1):
            response = client.post("/native/v1/recommendation/playlist", json={"isQpi": is_qpi})
            assert response.status_code == 200
        body = json.loads(mocked.last_request.body)
        assert body["is_qpi"] is is_qpi

    @pytest.mark.settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    @pytest.mark.parametrize("payload", [{"isEvent": True}, {"isEvent": True, "isQpi": None}])
    def test_is_qpi_not_forwarded_when_absent_or_null(self, requests_mock, client, db_session, payload):
        user = users_factories.UserFactory(id=3)
        mocked = requests_mock.post("https://example.com/recommendation/playlist_recommendation/3")

        client = client.with_token(user)

        # User authentication
        with testing.assert_num_queries(1):
            response = client.post("/native/v1/recommendation/playlist", json=payload)
            assert response.status_code == 200
        body = json.loads(mocked.last_request.body)
        assert body == {
            "start_date": None,
            "end_date": None,
            "is_event": True,
            "categories": None,
            "price_min": None,
            "price_max": None,
            "subcategories": None,
            "is_duo": None,
            "is_reco_shuffled": None,
            "offer_type_list": None,
        }
        assert response.json == {
            "playlistRecommendedOffers": [],
            "params": {
                "abTest": None,
                "callId": None,
                "filtered": None,
                "geoLocated": None,
                "modelEndpoint": None,
                "modelName": None,
                "modelOrigin": None,
                "modelVersion": None,
                "recoOrigin": None,
                "uniqueCallId": None,
            },
            "fromCache": None,
        }

    @pytest.mark.settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    @pytest.mark.parametrize("invalid_value", ["not a boolean", 2, []])
    def test_is_qpi_invalid_value(self, requests_mock, client, db_session, invalid_value):
        user = users_factories.UserFactory(id=3)
        mocked = requests_mock.post("https://example.com/recommendation/playlist_recommendation/3")

        response = client.with_token(user).post("/native/v1/recommendation/playlist", json={"isQpi": invalid_value})

        assert response.status_code == 400
        assert "isQpi" in response.json
        assert not mocked.called

    @pytest.mark.settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_timeout_error(self, requests_mock, client, db_session):
        user = users_factories.UserFactory(id=3)
        requests_mock.post(
            "https://example.com/recommendation/playlist_recommendation/3",
            exc=requests.exceptions.ConnectTimeout("a timeout error"),
        )

        client = client.with_token(user)
        # User authentication
        with testing.assert_num_queries(1):
            response = client.post("/native/v1/recommendation/playlist", json={})
            assert response.status_code == 504

        assert response.json == {"code": "RECOMMENDATION_API_TIMEOUT"}

    @pytest.mark.settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_generic_error(self, requests_mock, client, db_session):
        user = users_factories.UserFactory(id=3)
        requests_mock.post(
            "https://example.com/recommendation/playlist_recommendation/3",
            exc=requests.exceptions.TooManyRedirects("a redirect error"),
        )

        client = client.with_token(user)
        # User authentication
        with testing.assert_num_queries(1):
            response = client.post("/native/v1/recommendation/playlist", json={})
            assert response.status_code == 502

        assert response.json == {"code": "RECOMMENDATION_API_ERROR"}

    @pytest.mark.settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_from_cache_field_is_forwarded(self, requests_mock, client, db_session):
        user = users_factories.UserFactory(id=3)
        requests_mock.post(
            "https://example.com/recommendation/playlist_recommendation/3",
            json={
                "playlist_recommended_offers": ["10", "20", "30"],
                "params": {
                    "reco_origin": "algo",
                    "model_origin": "default",
                    "call_id": "1ead08f9-cfb1-4bb2-98ae-86170c36f0a7",
                    "unique_call_id": "450ab635-e477-407f-bc97-63b892e21810",
                },
                "from_cache": True,
            },
        )

        client = client.with_token(user)
        # User authentication
        with testing.assert_num_queries(1):
            response = client.post("/native/v1/recommendation/playlist", json={})
            assert response.status_code == 200

        assert response.json["fromCache"] is True
        assert response.json["params"]["uniqueCallId"] == "450ab635-e477-407f-bc97-63b892e21810"


def _link_artist_to_bookable_offer(artist):
    product = offers_factories.ProductFactory()
    artist_factories.ArtistProductLinkFactory(artist_id=artist.id, product_id=product.id)
    offer = offers_factories.ThingOfferFactory(product=product)
    offers_factories.StockFactory(offer=offer)


class TopArtistsPlaylistTest:
    @pytest.mark.settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_returns_artists_in_recommendation_api_order(self, requests_mock, client):
        first = artist_factories.ArtistFactory(name="First artist")
        second = artist_factories.ArtistFactory(name="Second artist")
        _link_artist_to_bookable_offer(first)
        _link_artist_to_bookable_offer(second)
        requests_mock.get(
            "https://example.com/recommendation/playlist_top_artists/MUSIQUE",
            json={
                "playlist_artists": [second.id, first.id],
                "params": {"search_group_name": "MUSIQUE", "score_name": "score", "call_id": "test-call-id"},
            },
        )

        # Fetch eligible artists
        with testing.assert_num_queries(1):
            response = client.get("/native/v1/recommendation/top_artists_playlist/musique")
            assert response.status_code == 200

        assert response.json == {
            "artists": [
                {"id": second.id, "name": second.name, "image": second.thumbUrl},
                {"id": first.id, "name": first.name, "image": first.thumbUrl},
            ]
        }

    @pytest.mark.settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_skips_ineligible_artists(self, requests_mock, client):
        blacklisted = artist_factories.ArtistFactory(is_blacklisted=True)
        _link_artist_to_bookable_offer(blacklisted)
        without_offer = artist_factories.ArtistFactory()
        eligible = artist_factories.ArtistFactory()
        _link_artist_to_bookable_offer(eligible)
        unknown_id = "00000000-0000-0000-0000-000000000001"
        requests_mock.get(
            "https://example.com/recommendation/playlist_top_artists/MUSIQUE",
            json={"playlist_artists": [blacklisted.id, without_offer.id, unknown_id, eligible.id]},
        )

        # Fetch eligible artists
        with testing.assert_num_queries(1):
            response = client.get("/native/v1/recommendation/top_artists_playlist/musique")
            assert response.status_code == 200

        assert [artist["id"] for artist in response.json["artists"]] == [eligible.id]

    @pytest.mark.settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_empty_playlist(self, requests_mock, client):
        requests_mock.get(
            "https://example.com/recommendation/playlist_top_artists/MUSIQUE",
            json={"playlist_artists": []},
        )

        response = client.get("/native/v1/recommendation/top_artists_playlist/musique")

        assert response.status_code == 200
        assert response.json == {"artists": []}

    @pytest.mark.settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_empty_response_body(self, requests_mock, client):
        requests_mock.get("https://example.com/recommendation/playlist_top_artists/MUSIQUE", content=b"")

        with testing.assert_num_queries(0):
            response = client.get("/native/v1/recommendation/top_artists_playlist/musique")
            assert response.status_code == 200

        assert response.json == {"artists": []}

    def test_invalid_search_group_name(self, client):
        with testing.assert_num_queries(0):
            response = client.get("/native/v1/recommendation/top_artists_playlist/unknown")
            assert response.status_code == 400

        assert response.json == {"code": "RECOMMENDATION_API_VALIDATION"}

    @pytest.mark.settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_timeout_error(self, requests_mock, client):
        requests_mock.get(
            "https://example.com/recommendation/playlist_top_artists/MUSIQUE",
            exc=requests.exceptions.ConnectTimeout("a timeout error"),
        )
        with testing.assert_num_queries(0):
            response = client.get("/native/v1/recommendation/top_artists_playlist/musique")
            assert response.status_code == 504
        assert response.json == {"code": "RECOMMENDATION_API_TIMEOUT"}

    @pytest.mark.settings(
        RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
        RECOMMENDATION_API_URL="https://example.com/recommendation/",
    )
    def test_generic_error(self, requests_mock, client):
        requests_mock.get(
            "https://example.com/recommendation/playlist_top_artists/MUSIQUE",
            exc=requests.exceptions.TooManyRedirects("a redirect error"),
        )
        with testing.assert_num_queries(0):
            response = client.get("/native/v1/recommendation/top_artists_playlist/musique")
            assert response.status_code == 502
        assert response.json == {"code": "RECOMMENDATION_API_ERROR"}
