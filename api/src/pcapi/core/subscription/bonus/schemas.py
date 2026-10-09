"""
Mostly duplications from the API Particulier response models to prevent breaking changes if
their returned responses ever changes
"""

import datetime
import enum
import typing

from pydantic import BaseModel as BaseModelV2
from pydantic import StringConstraints

from pcapi.core.subscription.bonus import common_types
from pcapi.core.users import models as users_models


if typing.TYPE_CHECKING:
    from pcapi.connectors import api_particulier


CogCode = typing.Annotated[str, StringConstraints(strip_whitespace=True, to_upper=True, min_length=5, max_length=5)]


class _PersonWithoutBirthDate(BaseModelV2):
    last_name: str
    common_name: str | None = None
    first_names: list[str]
    gender: users_models.GenderEnum
    birth_country_cog_code: CogCode | None = None
    birth_city_cog_code: CogCode | None = None
    birth_city: str | None = None


class BonusCreditPerson(_PersonWithoutBirthDate):
    birth_date: datetime.date

    @classmethod
    def from_api_particulier_person(cls, person: "api_particulier.ApiParticulierPerson") -> typing.Self:
        if not person.nom_naissance:
            raise TypeError("A last name was expected")

        if not person.sexe:
            raise TypeError("A gender was expected")

        if not person.date_naissance:
            raise TypeError("A birth date was expected")

        return cls(
            last_name=person.nom_naissance,
            common_name=person.nom_usage,
            first_names=person.prenoms.split(" ") if person.prenoms else [],
            birth_date=person.date_naissance,
            gender=person.sexe,
        )


class BonusCreditHouseholder(_PersonWithoutBirthDate):
    birth_date: common_types.ApiParticulierDate = None

    @classmethod
    def from_api_particulier_person(cls, person: "api_particulier.ApiParticulierPerson") -> typing.Self:
        if not person.nom_naissance:
            raise TypeError("A last name was expected")

        if not person.sexe:
            raise TypeError("A gender was expected")

        return cls(
            last_name=person.nom_naissance,
            common_name=person.nom_usage,
            first_names=person.prenoms.split(" ") if person.prenoms else [],
            birth_date=person.date_naissance,
            gender=person.sexe,
        )


class QuotientFamilialContent(BaseModelV2):
    provider: str
    value: int
    year: int
    month: int
    computation_year: int
    computation_month: int

    @classmethod
    def from_api_particulier_quotient_familial(
        cls, quotient_familial: "api_particulier.QuotientFamilial"
    ) -> typing.Self:
        return cls(
            provider=quotient_familial.fournisseur,
            value=quotient_familial.valeur,
            year=quotient_familial.annee,
            month=quotient_familial.mois,
            computation_year=quotient_familial.annee_calcul,
            computation_month=quotient_familial.mois_calcul,
        )


class QuotientFamilialBonusCreditContent(BaseModelV2):
    custodian: BonusCreditPerson
    quotient_familial: QuotientFamilialContent | None = None
    householders: list[BonusCreditHouseholder] | None = None
    children: list[BonusCreditPerson] | None = None
    http_status_code: int | None = None
    error_code: str | None = None
    next_retry_at: datetime.datetime


class AdultDisabilityBonusCreditContent(BaseModelV2):
    person: BonusCreditPerson
    is_disability_recipient: bool | None = None
    http_status_code: int | None = None
    error_code: str | None = None
    next_retry_at: datetime.datetime


class DisabledChildEducationRecipientStatus(enum.StrEnum):
    RECIPIENT = "recipient"
    RIGHT_OPENING = "right_opening"
    NON_RECIPIENT = "non_recipient"


class DisabledChildEducationBonusCreditContent(BaseModelV2):
    person: BonusCreditPerson
    disability_recipient_status: DisabledChildEducationRecipientStatus | None = None
    http_status_code: int | None = None
    error_code: str | None = None
    next_retry_at: datetime.datetime


class QFBonificationStatus(enum.Enum):
    ELIGIBLE = "eligible"
    NOT_ELIGIBLE = "not_eligible"
    STARTED = "started"
    CUSTODIAN_NOT_FOUND = "custodian_not_found"
    APPLICATION_NOT_FOUND = "application_not_found"
    NOT_IN_TAX_HOUSEHOLD = "not_in_tax_household"
    QUOTIENT_FAMILIAL_TOO_HIGH = "quotient_familial_too_high"
    TOO_MANY_RETRIES = "too_many_retries"
    GRANTED = "granted"
    KO = "ko"


class DisabilityBonificationStatus(enum.Enum):
    ELIGIBLE = "eligible"
    NOT_ELIGIBLE = "not_eligible"
    STARTED = "started"
    TOO_MANY_RETRIES = "too_many_retries"
    PERSON_NOT_FOUND = "person_not_found"
    APPLICATION_NOT_FOUND = "application_not_found"
    NOT_RECIPIENT = "not_recipient"
    GRANTED = "granted"
    KO = "ko"
