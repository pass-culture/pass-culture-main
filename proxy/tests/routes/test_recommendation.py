import asyncio
import datetime
from unittest.mock import AsyncMock
from unittest.mock import patch

from fastapi.testclient import TestClient
import jwt

from pcproxy import settings
from pcproxy.connectors.recommendation import RecommendationException
from pcproxy.main import app


client = TestClient(app)


def get_valid_jwt(user_id: int):
    return jwt.encode(
        payload={
            "iat": int((datetime.datetime.now() - datetime.timedelta(seconds=10)).timestamp()),
            "nbf": int((datetime.datetime.now() - datetime.timedelta(seconds=10)).timestamp()),
            "exp": int((datetime.datetime.now() + datetime.timedelta(seconds=10)).timestamp()),
            "user_claims": {"user_id": user_id},
        },
        key=settings.JWT_SECRET_KEY,
        algorithm="HS256",
    )


class SimilarOffersTest:
    route = "/native/v1/recommendation/similar_offers/246"

    def test_minimal(self):
        class BackendMock:
            get_similar_offers = AsyncMock(
                return_value={
                    "results": ["1", "2", "3"],
                    "params": {
                        "abTest": "plouf",
                        "callId": "my id",
                        "filtered": True,
                        "geoLocated": False,
                        "modelEndpoint": "endpoint",
                        "modelName": "name",
                        "modelVersion": "version",
                        "recoOrigin": "origin",
                    },
                },
            )

        with patch("pcproxy.routes.recommendation.RecommendationBackend", BackendMock):
            response = client.get(self.route)
            assert response.status_code == 200
            BackendMock.get_similar_offers.assert_called_once_with(
                offer_id=246,
                params={
                    "categories": None,
                    "latitude": None,
                    "longitude": None,
                    "subcategories": None,
                    "search_group_names": None,
                },
                user_id=None,
            )

        assert response.json() == {
            "results": ["1", "2", "3"],
            "params": {
                "ab_test": "plouf",
                "call_id": "my id",
                "filtered": True,
                "geo_located": False,
                "model_endpoint": "endpoint",
                "model_name": "name",
                "model_version": "version",
                "reco_origin": "origin",
            },
        }

    def test_full(self):
        class BackendMock:
            get_similar_offers = AsyncMock(
                return_value={
                    "results": ["1", "2", "3"],
                    "params": {
                        "abTest": "plouf",
                        "callId": "my id",
                        "filtered": True,
                        "geoLocated": False,
                        "modelEndpoint": "endpoint",
                        "modelName": "name",
                        "modelVersion": "version",
                        "recoOrigin": "origin",
                    },
                },
            )

        params = {
            "categories": "ABC,DEF,GHI",
            "latitude": 12.3456,
            "longitude": 65.4321,
            "subcategories": "ZYX,WVU",
            "search_group_names": "JKL,MNO,PQR",
        }
        with patch("pcproxy.routes.recommendation.RecommendationBackend", BackendMock):
            response = client.get(
                self.route,
                headers={"Authorization": f"Bearer {get_valid_jwt(user_id=123)}"},
                params=params,
            )
            assert response.status_code == 200
            BackendMock.get_similar_offers.assert_called_once_with(
                offer_id=246,
                params={
                    "categories": ["ABC", "DEF", "GHI"],
                    "latitude": 12.3456,
                    "longitude": 65.4321,
                    "subcategories": ["ZYX", "WVU"],
                    "search_group_names": ["JKL", "MNO", "PQR"],
                },
                user_id=123,
            )

        assert response.json() == {
            "results": ["1", "2", "3"],
            "params": {
                "ab_test": "plouf",
                "call_id": "my id",
                "filtered": True,
                "geo_located": False,
                "model_endpoint": "endpoint",
                "model_name": "name",
                "model_version": "version",
                "reco_origin": "origin",
            },
        }

    def test_timeout(self):
        class BackendMock:
            get_similar_offers = AsyncMock(side_effect=asyncio.TimeoutError)

        with patch("pcproxy.routes.recommendation.RecommendationBackend", BackendMock):
            response = client.get(self.route)
            assert response.status_code == 504

        assert response.json() == {"code": "RECOMMENDATION_API_TIMEOUT"}

    def test_backend_unavailable(self):
        class BackendMock:
            get_similar_offers = AsyncMock(side_effect=RecommendationException)

        with patch("pcproxy.routes.recommendation.RecommendationBackend", BackendMock):
            response = client.get(self.route)
            assert response.status_code == 502

        assert response.json() == {"code": "RECOMMENDATION_API_ERROR"}


class PlaylistTest:
    route = "/native/v1/recommendation/playlist"

    def test_full(self):
        class BackendMock:
            get_playlist = AsyncMock(
                return_value={
                    "playlistRecommendedOffers": ["1", "2", "3"],
                    "params": {
                        "abTest": "plouf",
                        "callId": "my id",
                        "filtered": True,
                        "geoLocated": False,
                        "modelEndpoint": "endpoint",
                        "modelName": "name",
                        "modelVersion": "version",
                        "recoOrigin": "origin",
                    },
                },
            )

        with patch("pcproxy.routes.recommendation.RecommendationBackend", BackendMock):
            response = client.post(
                self.route,
                headers={"Authorization": f"Bearer {get_valid_jwt(user_id=123)}"},
                params={
                    "modelEndpoint": "some endpoint",
                    "longitude": 12.3456,
                    "latitude": 65.321,
                },
                json={
                    "startDate": "1970-01-01",
                    "endDate": "2040-12-12",
                    "isEvent": True,
                    "categories": ["ABC, DEF"],
                    "priceMin": 12.30,
                    "priceMax": 30.12,
                    "subcategories": ["ZXW", "WVU"],
                    "isDuo": True,
                    "isRecoShuffled": True,
                    "offerTypeList": [{"a": "1"}, {"b": "2"}],
                },
            )
            assert response.status_code == 200
            BackendMock.get_playlist.assert_called_once_with(
                params={
                    "modelEndpoint": "some endpoint",
                    "longitude": 12.3456,
                    "latitude": 65.321,
                },
                body={
                    "startDate": "1970-01-01",
                    "endDate": "2040-12-12",
                    "isEvent": True,
                    "categories": ["ABC, DEF"],
                    "priceMin": 12.30,
                    "priceMax": 30.12,
                    "subcategories": ["ZXW", "WVU"],
                    "isDuo": True,
                    "isRecoShuffled": True,
                    "offerTypeList": [{"a": "1"}, {"b": "2"}],
                },
                user_id=123,
            )

        assert response.json() == {
            "playlist_recommended_offers": ["1", "2", "3"],
            "params": {
                "ab_test": "plouf",
                "call_id": "my id",
                "filtered": True,
                "geo_located": False,
                "model_endpoint": "endpoint",
                "model_name": "name",
                "model_version": "version",
                "reco_origin": "origin",
            },
        }

    def test_minimal(self):
        class BackendMock:
            get_playlist = AsyncMock(
                return_value={
                    "playlistRecommendedOffers": ["1", "2", "3"],
                    "params": {
                        "abTest": "plouf",
                        "callId": "my id",
                        "filtered": True,
                        "geoLocated": False,
                        "modelEndpoint": "endpoint",
                        "modelName": "name",
                        "modelVersion": "version",
                        "recoOrigin": "origin",
                    },
                },
            )

        with patch("pcproxy.routes.recommendation.RecommendationBackend", BackendMock):
            response = client.post(
                self.route,
                headers={"Authorization": f"Bearer {get_valid_jwt(user_id=123)}"},
                json={},
            )
            assert response.status_code == 200
            BackendMock.get_playlist.assert_called_once_with(
                params={
                    "latitude": None,
                    "longitude": None,
                    "modelEndpoint": None,
                },
                body={
                    "categories": None,
                    "endDate": None,
                    "isDuo": None,
                    "isEvent": None,
                    "isRecoShuffled": None,
                    "offerTypeList": None,
                    "priceMax": None,
                    "priceMin": None,
                    "startDate": None,
                    "subcategories": None,
                },
                user_id=123,
            )

        assert response.json() == {
            "playlist_recommended_offers": ["1", "2", "3"],
            "params": {
                "ab_test": "plouf",
                "call_id": "my id",
                "filtered": True,
                "geo_located": False,
                "model_endpoint": "endpoint",
                "model_name": "name",
                "model_version": "version",
                "reco_origin": "origin",
            },
        }

    def test_no_result(self):
        class BackendMock:
            get_playlist = AsyncMock(return_value={})

        with patch("pcproxy.routes.recommendation.RecommendationBackend", BackendMock):
            response = client.post(
                self.route,
                headers={"Authorization": f"Bearer {get_valid_jwt(user_id=123)}"},
                json={},
            )
            assert response.status_code == 200
            BackendMock.get_playlist.assert_called_once_with(
                params={
                    "latitude": None,
                    "longitude": None,
                    "modelEndpoint": None,
                },
                body={
                    "categories": None,
                    "endDate": None,
                    "isDuo": None,
                    "isEvent": None,
                    "isRecoShuffled": None,
                    "offerTypeList": None,
                    "priceMax": None,
                    "priceMin": None,
                    "startDate": None,
                    "subcategories": None,
                },
                user_id=123,
            )

        assert response.json() == {
            "playlist_recommended_offers": [],
            "params": {
                "ab_test": None,
                "call_id": None,
                "filtered": None,
                "geo_located": None,
                "model_endpoint": None,
                "model_name": None,
                "model_version": None,
                "reco_origin": None,
            },
        }

    def test_no_user(self):
        class BackendMock:
            get_playlist = AsyncMock(side_effect=asyncio.TimeoutError)

        with patch("pcproxy.routes.recommendation.RecommendationBackend", AsyncMock()) as mock:
            response = client.post(
                self.route,
                json={},
            )
            mock.assert_not_called()
            assert response.status_code == 401

        assert response.json() == {"code": "BAD_JWT"}

    def test_timeout(self):
        class BackendMock:
            get_playlist = AsyncMock(side_effect=asyncio.TimeoutError)

        with patch("pcproxy.routes.recommendation.RecommendationBackend", BackendMock):
            response = client.post(
                self.route,
                headers={"Authorization": f"Bearer {get_valid_jwt(user_id=123)}"},
                json={},
            )
            assert response.status_code == 504

        assert response.json() == {"code": "RECOMMENDATION_API_TIMEOUT"}

    def test_backend_unavailable(self):
        class BackendMock:
            get_playlist = AsyncMock(side_effect=RecommendationException)

        with patch("pcproxy.routes.recommendation.RecommendationBackend", BackendMock):
            response = client.post(
                self.route,
                headers={"Authorization": f"Bearer {get_valid_jwt(user_id=123)}"},
                json={},
            )
            assert response.status_code == 502

        assert response.json() == {"code": "RECOMMENDATION_API_ERROR"}
