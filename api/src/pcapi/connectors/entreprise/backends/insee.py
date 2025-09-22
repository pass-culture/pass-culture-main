"""A client for the Sirene API on api.insee.fr

Documentation of the API: https://api.insee.fr/catalogue/site/themes/wso2/subthemes/insee/pages/item-info.jag?name=Sirene&version=V3&provider=insee
"""

import datetime
import json
import logging

from pcapi import settings
from pcapi.connectors.entreprise import exceptions
from pcapi.connectors.entreprise.backends.base import BaseBackend
from pcapi.utils import cache as cache_utils
from pcapi.utils import requests


logger = logging.getLogger(__name__)

CACHE_DURATION = datetime.timedelta(minutes=15)


class InseeBackend(BaseBackend):
    base_url = settings.INSEE_SIRENE_API_URL
    timeout = 3

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": "Bearer " + settings.INSEE_SIRENE_API_TOKEN}

    def _get(self, subpath: str) -> dict:
        url = self.base_url + subpath
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
        except requests.exceptions.RequestException as exc:
            logger.exception("Network error on Sirene API", extra={"exc": exc, "url": url})
            raise exceptions.ApiException(f"Network error on Sirene API: {url}") from exc
        if response.status_code == 400:
            raise exceptions.InvalidFormatException()
        if response.status_code == 403:
            raise exceptions.NonPublicDataException()
        if response.status_code in (301, 404):
            raise exceptions.UnknownEntityException()
        if response.status_code == 429:
            raise ValueError("Pass Culture exceeded Sirene API rate limit")
        if response.status_code in (500, 503):
            raise exceptions.ApiException("Sirene API is unavailable")
        if response.status_code != 200:
            raise exceptions.ApiException(f"Unexpected {response.status_code} response from Sirene API: {url}")
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            raise exceptions.ApiException(f"Unexpected non-JSON response from Sirene API: {url}")

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
