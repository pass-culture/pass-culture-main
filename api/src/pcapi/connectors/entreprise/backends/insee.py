"""A client for the Sirene API on api.insee.fr

Documentation of the API: https://api.insee.fr/catalogue/site/themes/wso2/subthemes/insee/pages/item-info.jag?name=Sirene&version=V3&provider=insee
"""

import datetime
import json
import logging
import re
import typing

from pcapi import settings
from pcapi.connectors.entreprise import exceptions
from pcapi.connectors.entreprise import models
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

    def _check_non_public_data(self, info: models.SirenInfo | models.SiretInfo) -> None:
        # If the data is not public (which is known as "non diffusibles"
        # in Insee jargon), some fields are populated with "[ND]".
        #
        # There is also a "statutDiffusionUniteLegale" field in the
        # response that says whether there is non-public data. But
        # perhaps the data we want is public, and the non-public data
        # is something we're not interested in. So it's probably
        # better to look only at the data we use. (Obviously, this
        # will fail badly if a company is named "[ND]". We'll suppose
        # it's unlikely.)
        def _check_values(values: typing.Iterable) -> None:
            for value in values:
                if isinstance(value, dict):
                    _check_values(value.values())
                elif value == "[ND]":
                    raise exceptions.NonPublicDataException()

        _check_values(info.dict().values())

    def _get_head_office(self, siren_data: dict) -> dict:
        today = datetime.date.today().isoformat()
        for periode in siren_data["periodesUniteLegale"]:
            if (not periode["dateDebut"] or periode["dateDebut"] <= today) and (
                not periode["dateFin"] or periode["dateFin"] >= today
            ):
                return periode
        # In case all "periodes" are in the future (or the single period: "dateCreationUniteLegale" in the future):
        # Note that the company will be considered as active even before "dateCreationUniteLegale".
        return [_b for _b in siren_data["periodesUniteLegale"] if not _b["dateFin"]][0]

    def _get_name_from_siren_data(self, data: dict) -> str:
        # /!\ Keep in sync with `_get_name_from_siret_data()` below.
        head_office = self._get_head_office(data)
        # Company
        if head_office.get("denominationUniteLegale"):
            return head_office["denominationUniteLegale"]
        # "Entreprise individuelle" or similar
        return " ".join((data["prenom1UniteLegale"], head_office["nomUniteLegale"]))

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

    def _get_name_from_siret_data(self, data: dict) -> str:
        # /!\ Keep in sync with `_get_name_from_siren_data()` above.
        block = data["uniteLegale"]
        # Company
        if block.get("denominationUniteLegale"):
            return block["denominationUniteLegale"]
        # "Entreprise individuelle" or similar
        return " ".join((block["prenom1UniteLegale"], block["nomUniteLegale"]))

    def _get_address_from_siret_data(self, data: dict) -> models.SireneAddress:
        block = data["adresseEtablissement"]
        # Every field is in the response but may be null, for example
        # for foreign addresses, which we don't support.
        # The API includes the arrondissement (e.g. "PARIS 1"), remove it.
        city = re.sub(r" \d+ *$", "", block["libelleCommuneEtablissement"] or "")

        # Until Sirene API return postalCode of Saint-Martin
        # we need to do this hacky thing, otherwise Saint-Martin
        # users won't be able to create offerers.
        postal_code = block["codePostalEtablissement"] or ""
        if not postal_code and block["codeCommuneEtablissement"] == "97801":
            postal_code = "97150"

        return models.SireneAddress(
            street=" ".join(
                (
                    block["numeroVoieEtablissement"] or "",
                    block["typeVoieEtablissement"] or "",
                    block["libelleVoieEtablissement"] or "",
                )
            ).strip(),
            postal_code=postal_code,
            city=city,
            insee_code=block["codeCommuneEtablissement"] or "",
        )

    def _format_ape_code(self, ape_code: str | None) -> str | None:
        if not ape_code:
            return None
        return ape_code.replace(".", "")

    def get_siren(self, siren: str, with_address: bool = True, raise_if_non_public: bool = True) -> models.SirenInfo:
        subpath = f"/siren/{siren}"
        data = self._cached_get(subpath)["uniteLegale"]
        head_office = self._get_head_office(data)
        head_office_siret = siren + head_office["nicSiegeUniteLegale"]
        address = (
            self.get_siret(head_office_siret, raise_if_non_public=raise_if_non_public).address if with_address else None
        )
        info = models.SirenInfo(
            siren=siren,
            name=self._get_name_from_siren_data(data),
            head_office_siret=head_office_siret,
            legal_category_code=head_office["categorieJuridiqueUniteLegale"],
            ape_code=self._format_ape_code(head_office.get("activitePrincipaleUniteLegale")),
            address=address,
            active=head_office["etatAdministratifUniteLegale"] == "A",
            diffusible=data["statutDiffusionUniteLegale"] == "O",
            creation_date=datetime.date.fromisoformat(data["dateCreationUniteLegale"]),
            closure_date=self._get_closure_date_from_siren_data(data),
        )
        if raise_if_non_public:
            self._check_non_public_data(info)
        return info

    def get_siret(self, siret: str, raise_if_non_public: bool = True) -> models.SiretInfo:
        subpath = f"/siret/{siret}"
        data = self._cached_get(subpath)["etablissement"]
        legal_unit_block = data["uniteLegale"]
        try:
            block = [_b for _b in data["periodesEtablissement"] if _b["dateFin"] is None][0]
            active = block["etatAdministratifEtablissement"] == "A"
        except IndexError:
            active = False
        info = models.SiretInfo(
            siret=siret,
            siren=siret[:9],
            active=active,
            diffusible=legal_unit_block["statutDiffusionUniteLegale"] == "O",
            name=self._get_name_from_siret_data(data),
            address=self._get_address_from_siret_data(data),
            ape_code=self._format_ape_code(legal_unit_block.get("activitePrincipaleUniteLegale")),
            legal_category_code=legal_unit_block["categorieJuridiqueUniteLegale"],
        )
        if raise_if_non_public:
            self._check_non_public_data(info)
        return info

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
