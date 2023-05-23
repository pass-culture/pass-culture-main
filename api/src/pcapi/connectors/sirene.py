"""A client for the Sirene API on api.insee.fr

Documentation of the API: https://api.insee.fr/catalogue/site/themes/wso2/subthemes/insee/pages/item-info.jag?name=Sirene&version=V3&provider=insee
"""

from collections import defaultdict
import json
import logging
import re
import typing

import pydantic

from pcapi import settings
from pcapi.models import feature
from pcapi.utils import module_loading
from pcapi.utils import requests


logger = logging.getLogger(__name__)


class SireneException(Exception):
    pass  # base class, never raised directly


class SireneApiException(SireneException):
    pass  # error from the API itself


class UnknownEntityException(SireneException):
    pass  # SIREN or SIRET that does not exist


class InvalidFormatException(SireneException):
    pass  # likely a SIREN or SIRET with the wrong number of digits


class NonPublicDataException(SireneException):
    # Some SIREN/SIRET is marked as "non diffusibles", which means
    # that we cannot access information about them from the Sirene
    # API.
    pass


class _Address(pydantic.BaseModel):
    if typing.TYPE_CHECKING:  # https://github.com/pydantic/pydantic/issues/156
        street: str
        postal_code: str
        city: str
        insee_code: str
    else:
        street: pydantic.constr(strip_whitespace=True)
        postal_code: pydantic.constr(strip_whitespace=True)
        city: pydantic.constr(strip_whitespace=True)
        insee_code: pydantic.constr(strip_whitespace=True)


class SirenInfo(pydantic.BaseModel):
    if typing.TYPE_CHECKING:  # https://github.com/pydantic/pydantic/issues/156
        siren: str
    else:
        siren: pydantic.constr(strip_whitespace=True, min_length=9, max_length=9)
    name: str
    if typing.TYPE_CHECKING:  # https://github.com/pydantic/pydantic/issues/156
        head_office_siret: str
    else:
        head_office_siret: pydantic.constr(strip_whitespace=True, min_length=14, max_length=14)
    ape_code: str
    legal_category_code: str
    address: _Address | None


class SiretInfo(pydantic.BaseModel):
    if typing.TYPE_CHECKING:  # https://github.com/pydantic/pydantic/issues/156
        siret: str
    else:
        siret: pydantic.constr(strip_whitespace=True, min_length=14, max_length=14)
    active: bool
    name: str
    address: _Address
    ape_code: str
    legal_category_code: str


def get_siren(siren: str, with_address: bool = True) -> SirenInfo:
    """Return information about the requested SIREN.

    Getting the address requires a second HTTP request to the Sirene
    API. Ask it only if needed.
    """
    _check_feature_flag()
    return _get_backend().get_siren(siren, with_address=with_address)


def get_siret(siret: str) -> SiretInfo:
    """Return information about the requested SIRET."""
    _check_feature_flag()
    return _get_backend().get_siret(siret)


def get_legal_category_code(siren: str) -> str:
    """Return the code of the legal category."""
    return get_siren(siren, with_address=False).legal_category_code


def siret_is_active(siret: str) -> bool:
    """Return whether the requested SIRET is active."""
    siret_info = get_siret(siret)
    return siret_info.active


def _get_backend() -> "BaseBackend":
    backend_class = module_loading.import_string(settings.SIRENE_BACKEND)
    return backend_class()


def _check_feature_flag() -> None:
    if feature.FeatureToggle.DISABLE_ENTERPRISE_API.is_active():
        raise feature.DisabledFeatureError("DISABLE_ENTERPRISE_API is activated")


class BaseBackend:
    def get_siren(self, siren: str, with_address: bool = True) -> SirenInfo:
        raise NotImplementedError()

    def get_siret(self, siret: str) -> SiretInfo:
        raise NotImplementedError()


class TestingBackend(BaseBackend):
    address = _Address(
        street="3 RUE DE VALOIS",
        postal_code="75001",
        city="Paris",
        insee_code="75101",
    )

    def get_siren(self, siren: str, with_address: bool = True) -> SirenInfo:
        assert len(siren) == 9
        if siren == "000000000":
            raise UnknownEntityException()

        # allows to get an offerer with a specific APE code using specific siren
        siren_ape = defaultdict(
            lambda: "90.03A",
            {
                "777084112": "84.11Z",
                "777084122": "84.12Z",
                "777091032": "91.03Z",
            },
        )

        return SirenInfo(
            siren=siren,
            name="MINISTERE DE LA CULTURE",
            head_office_siret=siren + "00001",
            ape_code=siren_ape[siren],
            legal_category_code="1000",
            address=self.address if with_address else None,
        )

    def get_siret(self, siret: str) -> SiretInfo:
        assert len(siret) == 14

        siret_ape = defaultdict(
            lambda: "90.03A",
            {
                "77708411211111": "85.31Z",
                "77708411211112": "85.32Z",
                "77708411211113": "91.03Z",
            },
        )

        return SiretInfo(
            siret=siret,
            active=True,
            name="MINISTERE DE LA CULTURE",
            address=self.address,
            ape_code=siret_ape[siret],
            legal_category_code="1000",
        )


class InseeBackend(BaseBackend):
    base_url = "https://api.insee.fr/entreprises/sirene/V3"
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
            raise SireneApiException(f"Network error on Sirene API: {url}") from exc
        if response.status_code == 400:
            raise InvalidFormatException()
        if response.status_code == 403:
            raise NonPublicDataException()
        if response.status_code in (301, 404):
            raise UnknownEntityException()
        if response.status_code == 429:
            raise ValueError("Pass Culture exceeded Sirene API rate limit")
        if response.status_code in (500, 503):
            raise SireneApiException("Sirene API is unavailable")
        if response.status_code != 200:
            raise SireneApiException(f"Unexpected {response.status_code} response from Sirene API: {url}")
        try:
            return response.json()
        except json.JSONDecodeError:
            raise SireneApiException(f"Unexpected non-JSON response from Sirene API: {url}")

    def _check_non_public_data(self, info: SirenInfo | SiretInfo) -> None:
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
                    raise NonPublicDataException()

        _check_values(info.dict().values())

    def _get_head_office(self, siren_data: dict) -> dict:
        return [_b for _b in siren_data["periodesUniteLegale"] if not _b["dateFin"]][0]

    def _get_name_from_siren_data(self, data: dict) -> str:
        # /!\ Keep in sync with `_get_name_from_siret_data()` below.
        head_office = self._get_head_office(data)
        # Company
        if head_office.get("denominationUniteLegale"):
            return head_office["denominationUniteLegale"]
        # "Entreprise individuelle" or similar
        return " ".join((data["prenom1UniteLegale"], head_office["nomUniteLegale"]))

    def _get_name_from_siret_data(self, data: dict) -> str:
        # /!\ Keep in sync with `_get_name_from_siren_data()` above.
        block = data["uniteLegale"]
        # Company
        if block.get("denominationUniteLegale"):
            return block["denominationUniteLegale"]
        # "Entreprise individuelle" or similar
        return " ".join((block["prenom1UniteLegale"], block["nomUniteLegale"]))

    def _get_address_from_siret_data(self, data: dict) -> _Address:
        block = data["adresseEtablissement"]
        # Every field is in the response but may be null, for example
        # for foreign addresses, which we don't support.
        # The API includes the arrondissement (e.g. "PARIS 1"), remove it.
        city = re.sub(r" \d+ *$", "", block["libelleCommuneEtablissement"] or "")
        return _Address(
            street=" ".join(
                (
                    block["numeroVoieEtablissement"] or "",
                    block["typeVoieEtablissement"] or "",
                    block["libelleVoieEtablissement"] or "",
                )
            ).strip(),
            postal_code=block["codePostalEtablissement"] or "",
            city=city,
            insee_code=block["codeCommuneEtablissement"] or "",
        )

    def get_siren(self, siren: str, with_address: bool = True) -> SirenInfo:
        subpath = f"/siren/{siren}"
        data = self._get(subpath)["uniteLegale"]
        head_office = self._get_head_office(data)
        head_office_siret = siren + head_office["nicSiegeUniteLegale"]
        address = self.get_siret(head_office_siret).address if with_address else None
        info = SirenInfo(
            siren=siren,
            name=self._get_name_from_siren_data(data),
            head_office_siret=head_office_siret,
            legal_category_code=int(head_office["categorieJuridiqueUniteLegale"]),  # type: ignore [arg-type]
            ape_code=head_office["activitePrincipaleUniteLegale"],
            address=address,
        )
        self._check_non_public_data(info)
        return info

    def get_siret(self, siret: str) -> SiretInfo:
        subpath = f"/siret/{siret}"
        data = self._get(subpath)["etablissement"]
        legal_unit_block = data["uniteLegale"]
        try:
            block = [_b for _b in data["periodesEtablissement"] if _b["dateFin"] is None][0]
            active = block["etatAdministratifEtablissement"] == "A"
        except IndexError:
            active = False
        info = SiretInfo(
            siret=siret,
            active=active,
            name=self._get_name_from_siret_data(data),
            address=self._get_address_from_siret_data(data),
            ape_code=legal_unit_block["activitePrincipaleUniteLegale"],
            legal_category_code=legal_unit_block["categorieJuridiqueUniteLegale"],
        )
        self._check_non_public_data(info)
        return info
