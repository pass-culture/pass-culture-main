"""
A client for Insee Sirene API, configured in SIRENE_BACKEND
Documentation: https://www.sirene.fr/static-resources/documentation/sommaire_311.html
Usage: Search Open Data about legal entities and structures with multiple criteria
Use Enterprise API instead to find:
- Open Data about a legal entity or structure with simple criteria, such as SIREN or SIRET,
- Protected Data (for internal use only)
"""

import datetime
import json
import logging

from pcapi import settings
from pcapi.utils import cache as cache_utils
from pcapi.utils import module_loading
from pcapi.utils import requests


logger = logging.getLogger(__name__)

CACHE_DURATION = datetime.timedelta(minutes=15)


class InseeException(Exception):
    pass


class ApiException(InseeException):
    pass  # error from the API itself


class RateLimitExceeded(ApiException):
    pass


class InvalidFormatException(InseeException):
    pass  # likely a SIREN or SIRET with the wrong number of digits


class UnknownEntityException(InseeException):
    pass  # SIREN or SIRET that does not exist


class NonPublicDataException(InseeException):
    # Some SIREN/SIRET is marked as "non diffusibles", which means
    # that we cannot access information about them from the Sirene
    # API.
    pass


def _get_backend() -> "BaseBackend":
    backend_class = module_loading.import_string(settings.SIRENE_BACKEND)
    return backend_class()


def get_siren_closed_at_date(date_closed: datetime.date) -> list[str]:
    """Returns the list of SIREN which closure has been declared on the given date.
    Closure date may be the same day, in the past or in the future.
    """
    return _get_backend().get_siren_closed_at_date(date_closed)


class BaseBackend:
    def get_siren_closed_at_date(self, date_closed: datetime.date) -> list[str]:
        raise NotImplementedError()


class TestingBackend(BaseBackend):
    def get_siren_closed_at_date(self, date_closed: datetime.date) -> list[str]:
        return ["000099002", "900099003", "109599001"]


class InseeBackend(BaseBackend):
    base_url = settings.INSEE_SIRENE_API_URL
    timeout = 3

    @property
    def headers(self) -> dict[str, str]:
        return {"X-INSEE-Api-Key-Integration": settings.INSEE_SIRENE_API_TOKEN}

    def _get(self, subpath: str) -> dict:
        url = self.base_url + subpath
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
        except requests.exceptions.RequestException as exc:
            logger.exception("Network error on Sirene API", extra={"exc": exc, "url": url})
            raise ApiException(f"Network error on Sirene API: {url}") from exc
        if response.status_code == 400:
            raise InvalidFormatException()
        if response.status_code == 403:
            raise NonPublicDataException()
        if response.status_code in (301, 404):
            raise UnknownEntityException()
        if response.status_code == 429:
            raise ValueError("Pass Culture exceeded Sirene API rate limit")
        if response.status_code in (500, 503):
            raise ApiException("Sirene API is unavailable")
        if response.status_code != 200:
            raise ApiException(f"Unexpected {response.status_code} response from Sirene API: {url}")
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            raise ApiException(f"Unexpected non-JSON response from Sirene API: {url}")

    def _cached_get(self, subpath: str) -> dict:
        key_template = f"cache:sirene:{subpath}"
        cached = cache_utils.get_from_cache(
            retriever=lambda: json.dumps(self._get(subpath)),
            key_template=key_template,
            expire=CACHE_DURATION.seconds,
        )
        assert isinstance(cached, str)  # help mypy
        return json.loads(cached)

    def _get_closure_date_from_siren_data(self, siren_data: dict) -> datetime.date | None:
        # Several "periodesUniteLegale" can be closed.
        # This method may return a date in the future, when active is still True.
        closure_date = None
        sorted_periodes = sorted(
            siren_data["periodesUniteLegale"], key=lambda periode: periode["dateDebut"], reverse=True
        )
        for periode in sorted_periodes:
            if periode["etatAdministratifUniteLegale"] != "C":
                break
            closure_date = periode["dateDebut"]
        return datetime.date.fromisoformat(closure_date) if closure_date else None

    def get_siren_closed_at_date(self, date_closed: datetime.date) -> list[str]:
        results = []
        cursor = "*"
        while True:
            subpath = (
                f"/siren?q=dateDernierTraitementUniteLegale:{date_closed.isoformat()}"
                "+AND+periode(etatAdministratifUniteLegale:C+AND+changementEtatAdministratifUniteLegale:true)"
                "&champs=siren,dateDebut,dateFin,etatAdministratifUniteLegale"
                f"&curseur={cursor}&nombre=1000"
            )
            data = self._cached_get(subpath)
            for item in data["unitesLegales"]:
                closure_date = self._get_closure_date_from_siren_data(item)
                if closure_date is not None:
                    results.append(item["siren"])
            if (
                data["header"]["nombre"] == data["header"]["total"]
                or data["header"]["curseurSuivant"] == data["header"]["curseur"]
            ):
                break
            cursor = data["header"]["curseurSuivant"]
        return results
