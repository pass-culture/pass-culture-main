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


logger = logging.getLogger(__name__)


QUOTIENT_FAMILIAL_ENDPOINT = f"{settings.PARTICULIER_API_URL}/v3/dss/quotient_familial/identite"
AAH_ENDPOINT = f"{settings.PARTICULIER_API_URL}/v3/dss/allocation_adulte_handicape/identite"
AEEH_ENDPOINT = f"{settings.PARTICULIER_API_URL}/v3/dss/allocation_enfant_handicape/identite"


class ParticulierApiException(Exception):
    pass


class ParticulierApiForbidden(ParticulierApiException):
    pass


class ParticulierApiNotFound(ParticulierApiException):
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
    custodian: bonus_schemas.Person, at_date: datetime.date | None = None
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
        "annee": at_date.year if at_date else None,
        "mois": at_date.month if at_date else None,
    }
    response = requests.get(
        QUOTIENT_FAMILIAL_ENDPOINT,
        headers={"Authorization": f"Bearer {settings.PARTICULIER_API_TOKEN}"},
        params={key: value for (key, value) in query_params.items() if value},
    )

    if response.status_code == 403:
        raise ParticulierApiForbidden("The API token does not have the correct permissions")
    if response.status_code == 404:
        raise ParticulierApiNotFound("Custodian not found")
    if response.status_code == 429:
        raise ParticulierApiRateLimitExceeded("Particulier API rate limit exceeded")

    if response.status_code // 100 == 4:
        logger.error(
            "Invalid query for Particulier API",
            extra={"response": response.content, "status_code": response.status_code},
        )
        raise ParticulierApiQueryError("Invalid query for Particulier API")
    if response.status_code // 100 == 5:
        logger.error(
            "Particulier API is not responding",
            extra={"response": response.content, "status_code": response.status_code},
        )
        raise ParticulierApiUnavailable("Particulier API is not responding")
    elif not response.ok:
        logger.error(
            "Unexpected response from Particulier API",
            extra={"response": response.content, "status_code": response.status_code},
        )
        raise ParticulierApiException("Unexpected response from Particulier API")

    return QuotientFamilialResponse.model_validate(response.json())


class DisabledAdultAllowanceData(BaseModel):
    """
    WARN: The following model is considered user health data.
    Under GDPR, this data is considered *extremely* sensitive and a positive result *must never* be saved anywhere that is not especially secured.
    When the French government finally releases their secure server (SecNumCloud), we will be able to write it there.
    Until then, NO STORING ANYWHERE if the user is eligible to that allowance: in any database, in any logs or in any error stacktrace.

    If the user is not eligible, then the data is less sensitive because the user is in good health. However, all health-related data
    *must be deleted* when the bonus credit is granted, to avoid retro-engineering the user health if the relational database ever leaks.
    """

    est_beneficiaire: bool
    date_debut_droit: datetime.date | None


class DisabledAdultAllowanceResponse(BaseModel):
    data: DisabledAdultAllowanceData


def get_disabled_adult_allowance(person: bonus_schemas.Person) -> DisabledAdultAllowanceResponse:
    """
    Get whether the person benefits from the disabled adult allowance.

    See https://particulier.api.gouv.fr/developpeurs/openapi#tag/Statut-Allocation-Adulte-Handicape-(AAH)
    """
    country_insee_code = person.birth_country_cog_code
    city_insee_code = person.birth_city_cog_code
    if country_insee_code == countries_utils.FRANCE_INSEE_CODE and not city_insee_code:
        raise ValueError("City INSEE code is mandatory when the custodian is born in France")

    if country_insee_code != countries_utils.FRANCE_INSEE_CODE:
        city_insee_code = None

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
    }
    response = requests.get(
        AAH_ENDPOINT,
        headers={"Authorization": f"Bearer {settings.PARTICULIER_API_TOKEN}"},
        params={key: value for (key, value) in query_params.items() if value},
    )

    if response.status_code == 403:
        raise ParticulierApiForbidden("The API token does not have the correct permissions")
    if response.status_code == 404:
        raise ParticulierApiNotFound("Person not found")
    if response.status_code == 429:
        raise ParticulierApiRateLimitExceeded("Particulier API rate limit exceeded")

    if response.status_code // 100 == 4:
        logger.error(
            "Invalid query for Particulier API",
            extra={"response": response.content, "status_code": response.status_code},
        )
        raise ParticulierApiQueryError("Invalid query for Particulier API")
    if response.status_code // 100 == 5:
        logger.error(
            "Particulier API is not responding",
            extra={"response": response.content, "status_code": response.status_code},
        )
        raise ParticulierApiUnavailable("Particulier API is not responding")
    elif not response.ok:
        logger.error(
            "Unexpected response from Particulier API",
            extra={"response": response.content, "status_code": response.status_code},
        )
        raise ParticulierApiException("Unexpected response from Particulier API")

    return DisabledAdultAllowanceResponse.model_validate(response.json())


class DisabledChildEducationAllowanceStatus(enum.StrEnum):
    BENEFICIARY = "allocataire"
    PENDING = "ouvrant_droit"
    NON_BENEFICIARY = "non_beneficiaire"


class DisabledChildEducationAllowanceData(BaseModel):
    """
    WARN: The following model is considered user health data.
    Under GDPR, this data is considered *extremely* sensitive and a positive result *must never* be saved anywhere that is not especially secured.
    When the French government finally releases their secure server (SecNumCloud), we will be able to write it there.
    Until then, NO STORING ANYWHERE if the user is eligible to that allowance: in any database, in any logs or in any error stacktrace.

    If the user is not eligible, then the data is less sensitive because the user is in good health. However, all health-related data
    *must be deleted* when the bonus credit is granted, to avoid retro-engineering the user health if the relational database ever leaks.
    """

    status: DisabledChildEducationAllowanceStatus
    date_debut_droit: datetime.date | None


class DisabledChildEducationAllowanceResponse(BaseModel):
    data: DisabledChildEducationAllowanceData


def get_disabled_child_education_allowance(person: bonus_schemas.Person) -> DisabledChildEducationAllowanceResponse:
    """
    Get whether the person benefits from the disabled child education allowance.

    See https://particulier.api.gouv.fr/developpeurs/openapi#tag/Statut-Allocation-d'Education-de-l'Enfant-Handicape-(AEEH)
    """
    country_insee_code = person.birth_country_cog_code
    city_insee_code = person.birth_city_cog_code
    if country_insee_code == countries_utils.FRANCE_INSEE_CODE and not city_insee_code:
        raise ValueError("City INSEE code is mandatory when the custodian is born in France")

    if country_insee_code != countries_utils.FRANCE_INSEE_CODE:
        city_insee_code = None

    query_params = {
        "recipient": settings.PASS_CULTURE_SIRET,
        "nomNaissance": person.last_name.upper(),
        "prenoms[]": [first_name.upper() for first_name in person.first_names],
        "nomUsage": person.common_name,
        "anneeDateNaissance": person.birth_date.year,
        "moisDateNaissance": person.birth_date.month,
        "jourDateNaissance": person.birth_date.day,
        "sexeEtatCivil": person.gender.name,
        "codeCogInseePaysNaissance": country_insee_code,
        "codeCogInseeCommuneNaissance": city_insee_code,
    }
    response = requests.get(
        AEEH_ENDPOINT,
        headers={"Authorization": f"Bearer {settings.PARTICULIER_API_TOKEN}"},
        params={key: value for (key, value) in query_params.items() if value},
    )

    if response.status_code == 403:
        raise ParticulierApiForbidden("The API token does not have the correct permissions")
    if response.status_code == 404:
        raise ParticulierApiNotFound("Person not found")
    if response.status_code == 429:
        raise ParticulierApiRateLimitExceeded("Particulier API rate limit exceeded")

    if response.status_code // 100 == 4:
        logger.error("Invalid query for Particulier API", extra={"response": response.content})
        raise ParticulierApiQueryError("Invalid query for Particulier API")
    if response.status_code // 100 == 5:
        logger.error("Particulier API is not responding", extra={"response": response.content})
        raise ParticulierApiUnavailable("Particulier API is not responding")
    elif not response.ok:
        logger.error("Unexpected response from Particulier API", extra={"response": response.content})
        raise ParticulierApiException("Unexpected response from Particulier API")

    return DisabledChildEducationAllowanceResponse.model_validate(response.json())
