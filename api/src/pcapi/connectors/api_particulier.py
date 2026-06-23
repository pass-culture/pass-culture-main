import datetime
import enum
import logging
import typing

from pydantic import BaseModel
from pydantic import field_validator

from pcapi import settings
from pcapi.core.subscription.bonus import schemas as bonus_schemas
from pcapi.core.users import models as users_models
from pcapi.utils import countries as countries_utils
from pcapi.utils import requests
from pcapi.utils.requests import Response


logger = logging.getLogger(__name__)


QUOTIENT_FAMILIAL_ENDPOINT = f"{settings.PARTICULIER_API_URL}/v3/dss/quotient_familial/identite"
AAH_ENDPOINT = f"{settings.PARTICULIER_API_URL}/v3/dss/allocation_adulte_handicape/identite"
AEEH_ENDPOINT = f"{settings.PARTICULIER_API_URL}/v3/dss/allocation_enfant_handicape/identite"


class ParticulierApiException(Exception):
    def __init__(
        self,
        message: str = "",
        *,
        status_code: int,
        error_code: str | None = None,
        error_title: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.error_title = error_title


class ParticulierApiForbidden(ParticulierApiException):
    pass


class ParticulierApiApplicationNotFound(ParticulierApiException):
    pass


class ParticulierApiPersonNotFound(ParticulierApiException):
    pass


class ParticulierApiUnavailable(ParticulierApiException):
    pass


class ParticulierApiQueryError(ParticulierApiException):
    pass


class ParticulierApiRateLimitExceeded(ParticulierApiException):
    pass


class ApiParticulierPerson(BaseModel):
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
    allocataires: list[ApiParticulierPerson]
    enfants: list[ApiParticulierPerson]
    quotient_familial: QuotientFamilial


class QuotientFamilialResponse(BaseModel):
    data: QuotientFamilialData


def get_quotient_familial(
    custodian: bonus_schemas.BonusCreditPerson, at_date: datetime.date | None = None
) -> QuotientFamilialResponse:
    """
    Get the Quotient Familial from a tax household, using a custodian personal information.

    See https://particulier.api.gouv.fr/developpeurs/openapi#tag/Quotient-familial-CAF-and-MSA
    """
    country_insee_code = custodian.birth_country_cog_code
    city_insee_code = custodian.birth_city_cog_code

    if country_insee_code not in [None, countries_utils.FRANCE_INSEE_CODE]:
        city_insee_code = None

    if country_insee_code is None:
        country_insee_code = countries_utils.FRANCE_INSEE_CODE

    query_params = {
        "recipient": settings.PASS_CULTURE_SIRET,
        "nomNaissance": custodian.last_name.upper(),
        "prenoms[]": [first_name.upper() for first_name in custodian.first_names],
        "nomUsage": custodian.common_name.upper() if custodian.common_name else None,
        "anneeDateNaissance": custodian.birth_date.year,
        "moisDateNaissance": custodian.birth_date.month,
        "jourDateNaissance": custodian.birth_date.day,
        "sexeEtatCivil": custodian.gender.name,
        "codeCogInseePaysNaissance": country_insee_code,
        "codeCogInseeCommuneNaissance": city_insee_code,
        "nomCommuneNaissance": custodian.birth_city,
        "annee": at_date.year if at_date else None,
        "mois": at_date.month if at_date else None,
    }
    response = requests.get(
        QUOTIENT_FAMILIAL_ENDPOINT,
        headers={"Authorization": f"Bearer {settings.PARTICULIER_API_TOKEN}"},
        params={key: value for (key, value) in query_params.items() if value},
        log_info=False,
    )

    _raise_for_status(response, "quotient familial")

    return QuotientFamilialResponse.model_validate(response.json())


class DisabledAdultAllowanceData(BaseModel):
    """
    WARN: The following model is considered user health data.
    Under GDPR, this data is considered *extremely* sensitive and a positive result *must never* be saved anywhere that is not especially secured.
    When the French government finally releases their secure server (SecNumCloud), we will be able to write it there.
    Until then, NO STORING ANYWHERE if the user is recipient to that allowance: in any database, in any logs or in any error stacktrace.

    If the user is not recipient, then the data is less sensitive because the user is in good health. However, all health-related data
    *must be deleted* when the bonus credit is granted, to avoid retro-engineering the user health if the relational database ever leaks.
    """

    est_beneficiaire: bool
    date_debut_droit: datetime.date | None


class DisabledAdultAllowanceResponse(BaseModel):
    data: DisabledAdultAllowanceData


def get_disabled_adult_allowance(person: bonus_schemas.BonusCreditPerson) -> DisabledAdultAllowanceResponse:
    """
    Get whether the person benefits from the disabled adult allowance.

    See https://particulier.api.gouv.fr/developpeurs/openapi#tag/Statut-Allocation-Adulte-Handicape-(AAH)
    """
    country_insee_code = person.birth_country_cog_code
    city_insee_code = person.birth_city_cog_code

    if country_insee_code not in [None, countries_utils.FRANCE_INSEE_CODE]:
        city_insee_code = None

    if country_insee_code is None:
        country_insee_code = countries_utils.FRANCE_INSEE_CODE

    query_params = {
        "recipient": settings.PASS_CULTURE_SIRET,
        "nomNaissance": person.last_name.upper(),
        "prenoms[]": [first_name.upper() for first_name in person.first_names],
        "nomUsage": person.common_name.upper() if person.common_name else None,
        "anneeDateNaissance": person.birth_date.year,
        "moisDateNaissance": person.birth_date.month,
        "jourDateNaissance": person.birth_date.day,
        "sexeEtatCivil": person.gender.name,
        "codeCogInseePaysNaissance": country_insee_code,
        "codeCogInseeCommuneNaissance": city_insee_code,
        "nomCommuneNaissance": person.birth_city,
    }
    response = requests.get(
        AAH_ENDPOINT,
        headers={"Authorization": f"Bearer {settings.PARTICULIER_API_TOKEN}"},
        params={key: value for (key, value) in query_params.items() if value},
        log_info=False,
    )

    _raise_for_status(response, "aah")

    return DisabledAdultAllowanceResponse.model_validate(response.json())


class DisabledChildEducationAllowanceStatus(enum.StrEnum):
    RECIPIENT = "allocataire"
    RIGHT_OPENING = "ouvrant_droit"
    NON_RECIPIENT = "non_beneficiaire"


class DisabledChildEducationAllowanceData(BaseModel):
    """
    WARN: The following model is considered user health data.
    Under GDPR, this data is considered *extremely* sensitive and a positive result *must never* be saved anywhere that is not especially secured.
    When the French government finally releases their secure server (SecNumCloud), we will be able to write it there.
    Until then, NO STORING ANYWHERE if the user is recipient to that allowance: in any database, in any logs or in any error stacktrace.

    If the user is not recipient, then the data is less sensitive because the user is in good health. However, all health-related data
    *must be deleted* when the bonus credit is granted, to avoid retro-engineering the user health if the relational database ever leaks.
    """

    status: DisabledChildEducationAllowanceStatus
    date_debut_droit: datetime.date | None


class DisabledChildEducationAllowanceResponse(BaseModel):
    data: DisabledChildEducationAllowanceData


def get_disabled_child_education_allowance(
    person: bonus_schemas.BonusCreditPerson,
) -> DisabledChildEducationAllowanceResponse:
    """
    Get whether the person benefits from the disabled child education allowance.

    See https://particulier.api.gouv.fr/developpeurs/openapi#tag/Statut-Allocation-d'Education-de-l'Enfant-Handicape-(AEEH)
    """
    country_insee_code = person.birth_country_cog_code
    city_insee_code = person.birth_city_cog_code

    if country_insee_code not in [None, countries_utils.FRANCE_INSEE_CODE]:
        city_insee_code = None

    if country_insee_code is None:
        country_insee_code = countries_utils.FRANCE_INSEE_CODE

    query_params = {
        "recipient": settings.PASS_CULTURE_SIRET,
        "nomNaissance": person.last_name.upper(),
        "prenoms[]": [first_name.upper() for first_name in person.first_names],
        "nomUsage": person.common_name.upper() if person.common_name else None,
        "anneeDateNaissance": person.birth_date.year,
        "moisDateNaissance": person.birth_date.month,
        "jourDateNaissance": person.birth_date.day,
        "sexeEtatCivil": person.gender.name,
        "codeCogInseePaysNaissance": country_insee_code,
        "codeCogInseeCommuneNaissance": city_insee_code,
        "nomCommuneNaissance": person.birth_city,
    }
    response = requests.get(
        AEEH_ENDPOINT,
        headers={"Authorization": f"Bearer {settings.PARTICULIER_API_TOKEN}"},
        params={key: value for (key, value) in query_params.items() if value},
        log_info=False,
    )

    _raise_for_status(response, "aeeh")

    return DisabledChildEducationAllowanceResponse.model_validate(response.json())


def _raise_for_status(response: Response, endpoint_label: str) -> None:
    if response.ok:
        return

    try:
        api_particulier_error = response.json()["errors"][0]
        error_code, error_title = api_particulier_error["code"], api_particulier_error["title"]
        message = f"{endpoint_label} {int(response.status_code)} error_code={error_code} error_title={error_title}"
    except (ValueError, KeyError):  # JSON decode error
        error_code, error_title = None, None
        message = f"{endpoint_label} unparsable error"

    ExceptionClass = ParticulierApiException
    if response.status_code == 403:
        ExceptionClass = ParticulierApiForbidden
    elif response.status_code == 404:
        # the person was found, but no application was found
        ExceptionClass = ParticulierApiApplicationNotFound
    elif response.status_code == 422:
        # what we usually think of 404 not found: either nobody or more than one person was found
        ExceptionClass = ParticulierApiPersonNotFound
    elif response.status_code == 429:
        ExceptionClass = ParticulierApiRateLimitExceeded
    elif response.status_code // 100 == 4:
        ExceptionClass = ParticulierApiQueryError
    elif response.status_code // 100 == 5:
        ExceptionClass = ParticulierApiUnavailable

    raise ExceptionClass(
        message,
        status_code=response.status_code,
        error_code=error_code,
        error_title=error_title,
    )
