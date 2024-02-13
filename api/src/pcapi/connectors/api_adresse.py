"""
A client for API Adresse.
Documentation of the API: https://adresse.data.gouv.fr/api-doc/adresse
Further explanations at: https://guides.etalab.gouv.fr/apis-geo/1-api-adresse.html
"""

import json
import logging

import pydantic.v1 as pydantic_v1

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


class AddressInfo(pydantic_v1.BaseModel):
    id: str
    label: str
    postcode: str
    latitude: float
    longitude: float
    score: float


def _get_backend() -> "BaseBackend":
    backend_class = module_loading.import_string(settings.ADRESSE_BACKEND)
    return backend_class()


def get_municipality_centroid(city: str, postcode: str | None = None, citycode: str | None = None) -> AddressInfo:
    """Return information about the requested city."""
    return _get_backend().get_municipality_centroid(postcode=postcode, citycode=citycode, city=city)


def get_address(address: str, postcode: str | None = None, city: str | None = None) -> AddressInfo:
    """Return information about the requested address."""
    return _get_backend().get_single_address_result(address=address, postcode=postcode, city=city)


class BaseBackend:
    def get_municipality_centroid(
        self, city: str, postcode: str | None = None, citycode: str | None = None
    ) -> AddressInfo:
        raise NotImplementedError()

    def get_single_address_result(self, address: str, postcode: str | None, city: str | None = None) -> AddressInfo:
        raise NotImplementedError()


class TestingBackend(BaseBackend):
    def get_municipality_centroid(
        self, city: str, postcode: str | None = None, citycode: str | None = None
    ) -> AddressInfo:
        # Used to check non-diffusible SIREN/SIRET
        return AddressInfo(
            id="06029",
            label="Cannes",
            postcode="06400",
            score=0.9549627272727272,
            latitude=43.555468,
            longitude=7.004585,
        )

    def get_single_address_result(self, address: str, postcode: str | None, city: str | None = None) -> AddressInfo:
        return AddressInfo(
            id="75101_9575_00003",
            label="3 Rue de Valois 75001 Paris",
            postcode="75001",
            score=0.9651727272727272,
            latitude=48.87171,
            longitude=2.308289,
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

    def get_municipality_centroid(
        self, city: str, postcode: str | None = None, citycode: str | None = None
    ) -> AddressInfo:
        """Fallback to querying the city, because the q parameter must contain part of the address label"""
        parameters = {
            "q": city,
            "postcode": postcode,
            "citycode": citycode,
            "type": "municipality",
            "autocomplete": 0,
            "limit": 1,
        }
        data = self._send_search_request(parameters=parameters)
        if self._is_result_empty(data):
            logger.error(
                "No result from API Adresse for a municipality",
                extra={"postcode": postcode, "city": city},
            )
            raise NoResultException
        return self._format_result(data)

    def get_single_address_result(self, address: str, postcode: str | None, city: str | None = None) -> AddressInfo:
        """
        No human interaction so we limit to 1 result, and add a filter on the INSEE code (Code Officiel Géographique)
        This will get the highest score result from the query, for a specific INSEE code.
        An incorrect result would still be in the vicinity of the expected result, and can be later edited in pc pro
        see https://forum.etalab.gouv.fr/t/interpretation-du-score/3852/4
        If no result is found, we return the centroid of the municipality
        """
        parameters = {
            "q": address,
            "postcode": postcode,
            "autocomplete": 0,
            "limit": 1,
        }

        data = self._send_search_request(parameters=parameters)
        if self._is_result_empty(data):
            logger.info(
                "No result from API Adresse for queried address",
                extra={"queried_address": address, "postcode": postcode},
            )
            if city is not None and postcode is not None:
                return self.get_municipality_centroid(city=city, postcode=postcode)
            raise NoResultException

        result = self._format_result(data)

        extra = {
            "id": result.id,
            "label": result.label,
            "latitude": result.latitude,
            "longitude": result.longitude,
            "queried_address": address,
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
        # GeoJSON defines Point as [longitude, latitude]
        # https://datatracker.ietf.org/doc/html/rfc7946#appendix-A.1
        coordinates = data["features"][0]["geometry"]["coordinates"]
        properties = data["features"][0]["properties"]
        return AddressInfo(
            id=properties["id"],
            latitude=coordinates[1],
            longitude=coordinates[0],
            score=properties["score"],
            label=properties["label"],
            postcode=properties["postcode"],
        )
