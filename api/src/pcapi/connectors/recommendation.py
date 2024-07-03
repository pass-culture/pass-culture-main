"""Connector for our recommendation API

This is a mere proxy. Input validation is done by the recommendation
API, and this module returns the raw response.
"""

import json
import logging

from pcapi import settings
import pcapi.core.users.models as users_models
from pcapi.utils import module_loading
from pcapi.utils import requests


logger = logging.getLogger(__name__)
HTTP_TIMEOUT = 5


class RecommendationApiException(Exception):
    pass


def _get_backend() -> "BaseBackend":
    backend_class = module_loading.import_string(settings.RECOMMENDATION_BACKEND)
    return backend_class()


def get_similar_offers(offer_id: int, user: users_models.User | None = None, params: dict | None = None) -> bytes:
    backend = _get_backend()
    params = params or {}
    return backend.get_similar_offers(offer_id, user, params)


def get_playlist(user: users_models.User, params: dict | None = None, body: dict | None = None) -> bytes:
    backend = _get_backend()
    params = params or {}
    body = body or {}
    return backend.get_playlist(user, params, body)


class BaseBackend:
    def get_similar_offers(self, offer_id: int, user: users_models.User | None, params: dict) -> bytes:
        raise NotImplementedError()

    def get_playlist(self, user: users_models.User, params: dict, body: dict) -> bytes:
        raise NotImplementedError()


class TestingBackend:
    def get_similar_offers(self, offer_id: int, user: users_models.User | None, params: dict) -> bytes:
        offers = [i + 10 * offer_id + 100 * (user.id if user else 0) for i in range(3)]
        response = {"results": [str(id_) for id_ in offers], "params": {}}
        return bytes(json.dumps(response), encoding="utf-8")

    def get_playlist(self, user: users_models.User, params: dict, body: dict) -> bytes:
        offers = [i + 100 * user.id for i in range(3)]
        response = {
            "playlist_recommended_offers": [str(id_) for id_ in offers],
            "params": {},
        }
        return bytes(json.dumps(response), encoding="utf-8")


class HttpBackend:
    def _request(self, method: str, path: str, params: dict, body: dict | None = None) -> bytes:
        params["token"] = settings.RECOMMENDATION_API_AUTHENTICATION_TOKEN
        url = "/".join((settings.RECOMMENDATION_API_URL.rstrip("/"), path.lstrip("/")))
        try:
            if method == "get":
                response = requests.get(url, params=params, timeout=HTTP_TIMEOUT, disable_synchronous_retry=True)
            elif method == "post":
                response = requests.post(
                    url, params=params, json=body, timeout=HTTP_TIMEOUT, disable_synchronous_retry=True
                )
            else:
                raise ValueError(f"Unexpected method: {method}")
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            logger.info("Got error from Recommendation API", extra={"exc": str(exc)}, exc_info=True)
            raise RecommendationApiException(str(exc)) from exc
        return response.content

    def get_similar_offers(self, offer_id: int, user: users_models.User | None, params: dict) -> bytes:
        path = f"/similar_offers/{offer_id}"
        # The `user_id` param (in snake_case) is currently ignored by
        # the Recommendation API, but let's be defensive.
        params.pop("user_id", None)
        params["userId"] = str(user.id) if user else None
        return self._request("get", path, params=params)

    def get_playlist(self, user: users_models.User, params: dict, body: dict) -> bytes:
        path = f"/playlist_recommendation/{user.id}"
        return self._request("post", path, params=params, body=body)
