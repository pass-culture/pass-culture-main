"""
A client for Geo API "Découpage administratif", which is able to search for cities in France.
Same API as used in bonus request in pass-culture-app-native.
API Adresse can't search by INSEE code.

Documentation: https://geo.api.gouv.fr/decoupage-administratif
"""

import json
import logging
from hashlib import md5

import pydantic

from pcapi import settings
from pcapi.utils import cache as cache_utils
from pcapi.utils import module_loading
from pcapi.utils import requests


logger = logging.getLogger(__name__)


class GeoException(Exception):
    pass  # base class, never raised directly


class GeoApiException(GeoException):
    pass  # error from the API itself


class GeoApiServerErrorException(GeoApiException):
    pass


class InvalidFormatException(GeoException):
    pass


class RateLimitExceeded(GeoApiException):
    pass


class GeoCity(pydantic.BaseModel):
    name: str
    insee_code: str


def _get_backend() -> "BaseBackend":
    backend_class = module_loading.import_string(settings.GEO_API_BACKEND)
    return backend_class()


def search_city(name: str | None = None, *, insee_code: str | None = None, limit: int = 20) -> list[GeoCity]:
    if not name and not insee_code:
        return []
    return _get_backend().search_city(name, insee_code, limit)


class BaseBackend:
    def search_city(self, name: str | None, insee_code: str | None, limit: int) -> list[GeoCity]:
        raise NotImplementedError()


class TestingBackend(BaseBackend):
    def search_city(self, name: str | None, insee_code: str | None, limit: int) -> list[GeoCity]:
        return [
            GeoCity(
                name="Ville" if name is None else f"{name}ville",
                insee_code="12345" if insee_code is None else insee_code,
            )
        ]


class GeoApiBackend(BaseBackend):
    base_url = "https://geo.api.gouv.fr/"

    def _request(self, url: str, *, params: dict | None = None) -> requests.Response:
        try:
            response = requests.get(url, params=params, timeout=5)
        except requests.exceptions.RequestException as exc:
            msg = "Network error on Geo API"
            logger.exception(msg, extra={"exc": exc, "url": url})
            raise GeoApiException(msg) from exc

        if response.status_code in (500, 503):
            raise GeoApiServerErrorException("Geo API is unavailable")
        if response.status_code == 400:
            raise InvalidFormatException()
        if response.status_code == 429:
            raise RateLimitExceeded("Rate limit exceeded from API Geo")
        if response.status_code != 200:
            raise GeoApiException(f"Unexpected {response.status_code} response from Geo API: {url}")

        return response

    def _search(self, endpoint: str, params: dict) -> dict:
        url = f"{self.base_url}{endpoint}"
        response = self._request(url, params=params)
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            raise GeoApiException("Unexpected non-JSON response from Geo API")
        return data

    def _cached_search(self, endpoint: str, params: dict) -> dict:
        def retriever() -> str:
            return json.dumps(self._search(endpoint, params))

        key_template = "cache:api:geo:%(endpoint)s:%(hash_params)s"
        hash_params = md5(json.dumps(params).encode("utf-8")).hexdigest()

        cached_data = cache_utils.get_from_cache(
            retriever=retriever,
            key_template=key_template,
            key_args={"endpoint": endpoint, "hash_params": hash_params},
            expire=60 * 60 * 24 * 7,  # 1 week
        )

        return json.loads(str(cached_data))

    def search_city(self, name: str | None, insee_code: str | None, limit: int) -> list[GeoCity]:
        params = {
            "boost": "population",
            "limit": limit,
        }
        if name:
            params["nom"] = name.strip()
        if insee_code:
            params["code"] = insee_code

        data = self._cached_search("communes", params)
        return [GeoCity(name=result["nom"], insee_code=result["code"]) for result in data]
