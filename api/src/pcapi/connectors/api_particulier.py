import datetime
import logging
import typing

from pydantic import BaseModel
from pydantic import field_validator

from pcapi import settings
from pcapi.core.subscription.bonus import schemas as bonus_schemas
from pcapi.core.users import models as users_models
from pcapi.utils import countries as countries_utils
from pcapi.utils import requests


logger = logging.getLogger(__name__)


QUOTIENT_FAMILIAL_ENDPOINT = f"{settings.PARTICULIER_API_URL}/v3/dss/quotient_familial/identite"


class ParticulierApiException(Exception):
    pass


class ParticulierApiQuotientFamilialNotFound(ParticulierApiException):
    pass


class ParticulierApiUnavailable(ParticulierApiException):
    pass


class ParticulierApiQueryError(ParticulierApiException):
    pass


class ParticulierApiRateLimitExceeded(ParticulierApiException):
    pass


class QuotientFamilialPerson(BaseModel):
    nom_naissance: str | None = None
    nom_usage: str | None = None
    prenoms: str | None = None
    date_naissance: datetime.date | None = None
    sexe: users_models.GenderEnum | None = None

    @field_validator("sexe", mode="before")
    @classmethod
    def parse_gender(cls, gender: typing.Any) -> users_models.GenderEnum | None:
        if isinstance(gender, str):
            return users_models.GenderEnum[gender]
        if isinstance(gender, users_models.GenderEnum):
            return gender
        if gender is None:
            return None

        raise ValueError(f"Unexpected {gender = } given")


class QuotientFamilial(BaseModel):
    fournisseur: str
    valeur: int
    annee: int
    mois: int
    annee_calcul: int
    mois_calcul: int


class QuotientFamilialData(BaseModel):
    allocataires: list[QuotientFamilialPerson]
    enfants: list[QuotientFamilialPerson]
    quotient_familial: QuotientFamilial


class QuotientFamilialResponse(BaseModel):
    data: QuotientFamilialData


def get_quotient_familial(
    custodian: bonus_schemas.QuotientFamilialCustodian, at_date: datetime.date | None = None
) -> QuotientFamilialResponse:
    """
    Get the Quotient Familial from a tax household, using a custodian personal information.

    See https://particulier.api.gouv.fr/developpeurs/openapi#tag/Quotient-familial-CAF-and-MSA
    """
    country_insee_code = custodian.birth_country_cog_code
    city_insee_code = custodian.birth_city_cog_code
    if country_insee_code == countries_utils.FRANCE_INSEE_CODE and not city_insee_code:
        raise ValueError("City INSEE code is mandatory when the custodian is born in France")

    if country_insee_code != countries_utils.FRANCE_INSEE_CODE:
        city_insee_code = None

    computation_year = at_date.year if at_date else None
    computation_month = at_date.month if at_date else None

    query_params = {
        "recipient": settings.PASS_CULTURE_SIRET,
        "nomNaissance": custodian.last_name.upper(),
        "prenoms[]": [first_name.upper() for first_name in custodian.first_names],
        "nomUsage": custodian.common_name,
        "anneeDateNaissance": custodian.birth_date.year,
        "moisDateNaissance": custodian.birth_date.month,
        "jourDateNaissance": custodian.birth_date.day,
        "sexeEtatCivil": custodian.gender.name,
        "codeCogInseePaysNaissance": country_insee_code,
        "codeCogInseeCommuneNaissance": city_insee_code,
        "annee": computation_year,
        "mois": computation_month,
    }
    response = requests.get(
        QUOTIENT_FAMILIAL_ENDPOINT,
        headers={"Authorization": f"Bearer {settings.PARTICULIER_API_TOKEN}"},
        params={key: value for (key, value) in query_params.items() if value},
    )

    if response.status_code == 404:
        raise ParticulierApiQuotientFamilialNotFound("Custodian not found")
    if response.status_code == 429:
        raise ParticulierApiRateLimitExceeded("Particulier API rate limit exceeded")

    if response.status_code // 100 == 4:
        raise ParticulierApiQueryError("Invalid query for Particulier API")
    if response.status_code // 100 == 5:
        raise ParticulierApiUnavailable("Particulier API is not responding")
    elif response.status_code // 100 != 2:
        raise ParticulierApiException("Unexpected response from Particulier API")

    return QuotientFamilialResponse.model_validate(response.json())
