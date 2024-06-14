"""
A client for API Adresse.
Documentation of the API: https://adresse.data.gouv.fr/api-doc/adresse
Further explanations at: https://guides.etalab.gouv.fr/apis-geo/1-api-adresse.html
"""

import csv
import enum
from hashlib import md5
from io import StringIO
import json
import logging
import re

import pydantic.v1 as pydantic_v1

from pcapi import settings
from pcapi.core.geography.constants import MAX_LATITUDE
from pcapi.core.geography.constants import MAX_LONGITUDE
from pcapi.utils import cache as cache_utils
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


class RateLimitExceeded(AdresseApiException):
    pass


class AddressInfo(pydantic_v1.BaseModel):
    id: str
    label: str
    postcode: str
    citycode: str  # inseeCode
    latitude: float
    longitude: float
    score: float
    city: str
    street: str | None

    @pydantic_v1.validator("latitude")
    def validate_latitude(cls, latitude: float) -> float:
        if not -MAX_LATITUDE <= latitude <= MAX_LATITUDE:
            raise ValueError("latitude out of bounds")
        return latitude

    @pydantic_v1.validator("longitude")
    def validate_longitude(cls, longitude: float) -> float:
        if not -MAX_LONGITUDE <= longitude <= MAX_LONGITUDE:
            raise ValueError("longitude out of bounds")
        return longitude


class ResultColumn(enum.Enum):
    LATITUDE = "latitude"
    LONGITUDE = "longitude"
    RESULT_CITY = "result_city"
    RESULT_CITYCODE = "result_citycode"
    RESULT_CONTEXT = "result_context"
    RESULT_DISTRICT = "result_district"
    RESULT_HOUSENUMBER = "result_housenumber"
    RESULT_ID = "result_id"
    RESULT_LABEL = "result_label"
    RESULT_NAME = "result_name"
    RESULT_OLDCITY = "result_oldcity"
    RESULT_OLDCITYCODE = "result_oldcitycode"
    RESULT_POSTCODE = "result_postcode"
    RESULT_SCORE = "result_score"
    RESULT_SCORE_NEXT = "result_score_next"
    RESULT_STATUS = "result_status"
    RESULT_STREET = "result_street"
    RESULT_TYPE = "result_type"


def format_q(address: str, city: str) -> str:
    """
    This method formats the search address (q) in order to get the most accurate results from BAN.

    Hence, this method:
     - only uses address and city, without postcode.
       In several cases, including postcode can induce errors in results.
       Some cities have several postcodes and results may differ depending on the given postcode.
       Examples (q --> result):
       With postcode: '33 Boulevard Clemenceau 38000 Grenoble' --> '33 Boulevard Gambetta 38000 Grenoble'
       Without postcode: '33 Boulevard Clemenceau Grenoble' --> '33 Boulevard Clemenceau 38100 Grenoble'

     - normalizes / formats address and city to get as close as possible to the address format used by BAN.
       It also makes sure neither address nor city contains a comma, as it would break the CSV payload.
       Examples (q --> result):
       Not normalized: '105 RUE DES HAIES PARIS 20' --> 'Voie Ao/20 75020 Paris'
       Normalized: '105 Rue Des Haies Paris' --> '105 Rue des Haies 75020 Paris'
    """
    # Address:
    address = address.strip()
    address = address.replace(",", " ")
    address = " ".join(address.split())  # substitute multiple whitespaces with a single one
    address = address.title()
    # TODO: subs can be improved
    subs = (
        (r"\s*\d{5}.*", ""),  # Remove postcode and city from address
        (" Bd ", " Boulevard "),
        (" Pl ", " Place "),
        (" T ", "ter "),
    )
    for pattern, repl in subs:
        address = re.sub(pattern, repl, address)

    # City:
    city = city.strip()
    city = city.replace(",", "")
    if city and (s := city.split()[0].lower()) in ("paris", "marseille", "lyon"):
        city = s
    city = city.capitalize()

    q = " ".join([address, city])
    return q


def format_payload(headers: list[str], lines: list[dict]) -> str:
    return "\n".join([",".join(headers)] + [",".join([str(line[field]) for field in headers]) for line in lines])


def _get_backend() -> "BaseBackend":
    backend_class = module_loading.import_string(settings.ADRESSE_BACKEND)
    return backend_class()


def get_municipality_centroid(city: str, postcode: str | None = None, citycode: str | None = None) -> AddressInfo:
    """Return information about the requested city."""
    return _get_backend().get_municipality_centroid(postcode=postcode, citycode=citycode, city=city)


def get_address(
    address: str,
    postcode: str | None = None,
    city: str | None = None,
    citycode: str | None = None,
) -> AddressInfo:
    """Return information about the requested address."""
    return _get_backend().get_single_address_result(address=address, postcode=postcode, citycode=citycode, city=city)


def search_address(address: str, limit: int = 10) -> list[AddressInfo]:
    """Search for addresses."""
    return _get_backend().search_address(address, limit)


def search_csv(
    payload: str,
    columns: list[str] | None = None,
    result_columns: list[ResultColumn] | None = None,
) -> csv.DictReader:
    """Search CSV."""
    return _get_backend().search_csv(payload, columns=columns, result_columns=result_columns)


class BaseBackend:
    def get_municipality_centroid(
        self, city: str, postcode: str | None = None, citycode: str | None = None
    ) -> AddressInfo:
        raise NotImplementedError()

    def get_single_address_result(
        self,
        address: str,
        postcode: str | None,
        city: str | None = None,
        citycode: str | None = None,
    ) -> AddressInfo:
        raise NotImplementedError()

    def search_address(self, address: str, limit: int) -> list[AddressInfo]:
        raise NotImplementedError()

    def search_csv(
        self,
        payload: str,
        columns: list[str] | None = None,
        result_columns: list[ResultColumn] | None = None,
    ) -> csv.DictReader:
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
            citycode="06029",
            score=0.9549627272727272,
            latitude=43.555468,
            longitude=7.004585,
            city="Cannes",
            street=None,
        )

    def get_single_address_result(
        self,
        address: str,
        postcode: str | None,
        city: str | None = None,
        citycode: str | None = None,
    ) -> AddressInfo:
        return AddressInfo(
            id="75101_9575_00003",
            label="3 Rue de Valois 75001 Paris",
            postcode="75001",
            citycode="75056",
            score=0.9651727272727272,
            latitude=48.87171,
            longitude=2.308289,
            city="Paris",
            street="3 Rue de Valois",
        )

    def search_address(self, address: str, limit: int) -> list[AddressInfo]:
        return [self.get_single_address_result(address, postcode=None)]

    def search_csv(
        self,
        payload: str,
        columns: list[str] | None = None,
        result_columns: list[ResultColumn] | None = None,
    ) -> csv.DictReader:
        return csv.DictReader("q,result_id\n33 Boulevard Clemenceau Grenoble,38185_1660_00033")


class ApiAdresseBackend(BaseBackend):
    base_url = "https://api-adresse.data.gouv.fr"

    def _request(
        self,
        method: str,
        url: str,
        params: dict | None = None,
        files: list | None = None,
        timeout: int | float | None = None,
    ) -> requests.Response:
        methods = {
            "GET": requests.get,
            "POST": requests.post,
        }
        try:
            response = methods[method](url, params=params, files=files, timeout=timeout)  # type: ignore
        except requests.exceptions.RequestException as exc:
            msg = "Network error on Adresse API"
            logger.exception(msg, extra={"exc": exc, "url": url})
            raise AdresseApiException(msg) from exc

        if response.status_code in (500, 503):
            raise AdresseApiException("Adresse API is unavailable")
        if response.status_code == 400:
            raise InvalidFormatException()
        if response.status_code == 429:
            raise RateLimitExceeded("Rate limit exceeded from API Adresse")
        if response.status_code != 200:
            raise AdresseApiException(f"Unexpected {response.status_code} response from Adresse API: {url}")

        return response

    def _search(self, params: dict) -> dict:
        url = f"{self.base_url}/search"
        response = self._request("GET", url, params=params, timeout=3)
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise AdresseApiException("Unexpected non-JSON response from Adresse API")
        return data

    def _cached_search(self, params: dict) -> dict:
        key_template = "cache:api:addresse:search:%(hash_params)s"
        hash_params = md5(json.dumps(params).encode("utf-8")).hexdigest()
        retriever = lambda: json.dumps(self._search(params))
        cached_data = cache_utils.get_from_cache(
            retriever=retriever,
            key_template=key_template,
            key_args={"hash_params": hash_params},
            expire=60 * 60 * 24 * 7,  # time between 2 PC main releases
        )

        return json.loads(str(cached_data))

    def _search_csv(self, files: list) -> str:
        url = f"{self.base_url}/search/csv"
        response = self._request("POST", url, files=files, timeout=60)
        return response.text

    def get_municipality_centroid(
        self, city: str, postcode: str | None = None, citycode: str | None = None
    ) -> AddressInfo:
        """Fallback to querying the city, because the q parameter must contain part of the address label"""
        params = {
            "q": city,
            "postcode": postcode,
            "citycode": citycode,
            "type": "municipality",
            "autocomplete": 0,
            "limit": 1,
        }
        data = self._cached_search(params=params)
        if self._is_result_empty(data):
            logger.error(
                "No result from API Adresse for a municipality",
                extra={"postcode": postcode, "city": city},
            )
            raise NoResultException
        return self._format_result(data["features"][0])

    def get_single_address_result(
        self,
        address: str,
        postcode: str | None,
        city: str | None = None,
        citycode: str | None = None,
    ) -> AddressInfo:
        """
        No human interaction so we limit to 1 result, and add a filter on the INSEE code (Code Officiel Géographique)
        This will get the highest score result from the query, for a specific INSEE code.
        An incorrect result would still be in the vicinity of the expected result, and can be later edited in pc pro
        see https://forum.etalab.gouv.fr/t/interpretation-du-score/3852/4
        If no result is found, we return the centroid of the municipality
        """
        params = {
            "q": address,
            "postcode": postcode,
            "citycode": citycode,
            "autocomplete": 0,
            "limit": 1,
        }

        data = self._cached_search(params=params)
        if self._is_result_empty(data):
            logger.info(
                "No result from API Adresse for queried address",
                extra={"queried_address": address, "postcode": postcode},
            )
            if city is not None and postcode is not None:
                return self.get_municipality_centroid(city=city, postcode=postcode, citycode=citycode)
            raise NoResultException

        result = self._format_result(data["features"][0])

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
        coordinates = data["geometry"]["coordinates"]
        properties = data["properties"]
        street = None
        if properties["type"] != "municipality":
            # If the API return a complete address, not only a municipality centroid
            # We want the full format of the street (with the housenumber and so on)
            street = properties["name"]

        return AddressInfo(
            id=properties["id"],
            latitude=coordinates[1],
            longitude=coordinates[0],
            score=properties["score"],
            label=properties["label"],
            postcode=properties["postcode"],
            citycode=properties["citycode"],
            city=properties["city"],
            street=street,
        )

    def search_address(self, address: str, limit: int) -> list[AddressInfo]:
        params = {
            "q": address,
            "autocomplete": 0,
            "limit": limit,
        }

        data = self._cached_search(params=params)
        if self._is_result_empty(data):
            raise NoResultException

        return [self._format_result(result) for result in data["features"]]

    def search_csv(
        self,
        payload: str,
        columns: list[str] | None = None,
        result_columns: list[ResultColumn] | None = None,
    ) -> csv.DictReader:
        url = f"{self.base_url}/csv"

        payload_size = len(payload.encode("utf-8"))
        if payload_size > 50 * 1000 * 1000:  # 50 Mb
            raise ValueError("Payload is too large")

        if len(set(line.count(",") for line in payload.split("\n"))) != 1:
            raise ValueError("Malformed payload")

        if columns is None:
            msg = "All columns will be concatenated to build the search address"
            logger.warning(msg, extra={"url": url})
            columns = []

        headers = payload.partition("\n")[0].split(",")
        if not set(columns).issubset(headers):
            raise ValueError("Mismatch between columns and payload headers")

        if result_columns is None:
            result_columns = []
        if any(result_column not in ResultColumn for result_column in result_columns):
            raise ValueError("Invalid result_columns")

        files = [("data", payload)]
        for column in columns:
            files.append(("columns", (None, column)))  # type: ignore
        for result_column in result_columns:
            files.append(("result_columns", (None, result_column.value)))  # type: ignore
        text = self._search_csv(files)
        return csv.DictReader(StringIO(text))
