"""
Mostly duplications from the API Particulier response models to prevent breaking changes if
their returned responses ever changes
"""

import datetime
import typing

from pydantic import BaseModel as BaseModelV2
from pydantic import StringConstraints

from pcapi.core.users import models as users_models


if typing.TYPE_CHECKING:
    from pcapi.connectors import api_particulier


CogCode = typing.Annotated[str, StringConstraints(strip_whitespace=True, to_upper=True, min_length=5, max_length=5)]


class BonusCreditPerson(BaseModelV2):
    last_name: str
    common_name: str | None = None
    first_names: list[str]
    birth_date: datetime.date
    gender: users_models.GenderEnum
    birth_country_cog_code: CogCode | None = None
    birth_city_cog_code: CogCode | None = None
    birth_city: str | None = None

    @classmethod
    def from_api_particulier_person(cls, child: "api_particulier.ApiParticulierPerson") -> typing.Self:
        return cls(
            last_name=child.nom_naissance,
            common_name=child.nom_usage,
            first_names=child.prenoms.split(" ") if child.prenoms else [],
            birth_date=child.date_naissance,
            gender=child.sexe,
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
    householders: list[BonusCreditPerson] | None = None
    children: list[BonusCreditPerson] | None = None
    http_status_code: int | None = None
    error_code: str | None = None


class DisabilityBonusCreditContent(BaseModelV2):
    person: BonusCreditPerson
    http_status_code: int | None = None
    error_code: str | None = None
