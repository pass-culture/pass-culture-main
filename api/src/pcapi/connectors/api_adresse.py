"""
A client for API Adresse.
Documentation of the API: https://adresse.data.gouv.fr/api-doc/adresse
Further explanations at: https://guides.etalab.gouv.fr/apis-geo/1-api-adresse.html
"""

import json
import logging

import pydantic

from pcapi import settings
from pcapi.utils import module_loading
from pcapi.utils import requests


logger = logging.getLogger(__name__)


RELIABLE_SCORE_THRESHOLD = 0.8


class AdresseException(Exception):
    pass  # base class, never raised directly


class AdresseApiException(AdresseException):
    pass  # error from the API itself


class NoResultException(AdresseException):
    pass  # address is not referenced


class InvalidFormatException(AdresseException):
    pass


class _Properties(pydantic.BaseModel):
    id: str
    score: float
    label: str


class _Geometry(pydantic.BaseModel):
    latitude: float
    longitude: float


class AddressInfo(pydantic.BaseModel):
    id: str
    label: str
    latitude: float
    longitude: float
    score: float


def _get_backend() -> "BaseBackend":
    backend_class = module_loading.import_string(settings.ADRESSE_BACKEND)
    return backend_class()


def get_address(address: str, city: str, insee_code: str) -> AddressInfo:
    """Return information about the requested address."""
    return _get_backend().get_single_address_result(address, city, insee_code)


class BaseBackend:
    def get_single_address_result(self, query: str, city: str, insee_code: str) -> AddressInfo:
        raise NotImplementedError()


class TestingBackend(BaseBackend):
    def get_single_address_result(self, query: str, city: str, insee_code: str) -> AddressInfo:
        return AddressInfo(
            id="75101_9575_00003",
            label="3 Rue de Valois 75001 Paris",
            score=0.9651727272727272,
            latitude=2.308289,
            longitude=48.87171,
        )


class ApiAdresseBackend(BaseBackend):
    base_url = "https://api-adresse.data.gouv.fr/search"
    timeout = 3

    def _send_search_request(self, parameters: dict) -> dict:
        url = self.base_url
        try:
            response = requests.get(
                url,
                params=parameters,
                timeout=self.timeout,
            )
        except requests.exceptions.RequestException as exc:
            logger.exception("Network error on Adresse API", extra={"exc": exc, "url": url})
            raise AdresseApiException("Network error on Adresse API") from exc

        if response.status_code == 400:
            raise InvalidFormatException()
        if response.status_code in (500, 503):
            raise AdresseApiException("Adresse API is unavailable")
        if response.status_code != 200:
            raise AdresseApiException(f"Unexpected {response.status_code} response from Adresse API: {url}")
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise AdresseApiException("Unexpected non-JSON response from Adresse API")
        return data

    def _get_municipality_centroid(self, city: str, insee_code: str) -> AddressInfo:
        """Fallback to querying the city, because the q parameter must contain part of the address label"""
        parameters = {
            "q": city,
            "citycode": insee_code,
            "type": "municipality",
            "autocomplete": 0,
            "limit": 1,
        }
        data = self._send_search_request(parameters=parameters)
        if self._is_result_empty(data):
            logger.error(
                "No result from API Adresse for a municipality",
                extra={"insee_code": insee_code, "city": city},
            )
            raise NoResultException
        return self._format_result(data)

    def get_single_address_result(self, query: str, city: str, insee_code: str) -> AddressInfo:
        """
        No human interaction so we limit to 1 result, and add a filter on the INSEE code (Code Officiel Géographique)
        This will get the highest score result from the query, for a specific INSEE code.
        An incorrect result would still be in the vicinity of the expected result, and can be later edited in pc pro
        see https://forum.etalab.gouv.fr/t/interpretation-du-score/3852/4
        If no result is found, we return the centroid of the municipality
        """
        parameters = {
            "q": query,
            "citycode": insee_code,
            "autocomplete": 0,
            "limit": 1,
        }

        data = self._send_search_request(parameters=parameters)
        if self._is_result_empty(data):
            logger.info(
                "No result from API Adresse for queried address",
                extra={"queried_address": query, "citycode": insee_code},
            )
            return self._get_municipality_centroid(city=city, insee_code=insee_code)

        result = self._format_result(data)

        extra = {
            "id": result.id,
            "label": result.label,
            "latitude": result.latitude,
            "longitude": result.longitude,
            "queried_address": query,
            "score": result.score,
        }
        # TODO(fseguin, 2023-03-15): monitor the results, and maybe use municipality centroid if results are too wrong
        if result.score < RELIABLE_SCORE_THRESHOLD:
            logger.info("Result from API Adresse has a low score", extra=extra)
        else:
            logger.info("Retrieved details from API Adresse for query", extra=extra)
        return result

    def _is_result_empty(self, result: dict) -> bool:
        return len(result["features"]) == 0

    def _format_result(self, data: dict) -> AddressInfo:
        coordinates = data["features"][0]["geometry"]["coordinates"]
        properties = data["features"][0]["properties"]
        return AddressInfo(
            id=properties["id"],
            latitude=coordinates[0],
            longitude=coordinates[1],
            score=properties["score"],
            label=properties["label"],
        )
