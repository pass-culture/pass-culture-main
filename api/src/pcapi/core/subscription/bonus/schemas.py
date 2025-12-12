"""
Mostly duplications from the API Particulier response models to prevent breaking changes if
their returned responses ever changes
"""

import datetime

from pydantic import BaseModel as BaseModelV2

from pcapi.core.users import models as users_models


class QuotientFamilialCustodian(BaseModelV2):
    """
    Holds every variable needed to call api_particulier.get_quotient_familial
    """

    last_name: str
    common_name: str | None = None
    first_names: list[str]
    birth_date: datetime.date
    gender: users_models.GenderEnum
    birth_country_cog_code: str
    birth_city_cog_code: str | None = None


class QuotientFamilialChild(BaseModelV2):
    last_name: str
    common_name: str | None = None
    first_names: list[str]
    birth_date: datetime.date
    gender: users_models.GenderEnum


class QuotientFamilialContent(BaseModelV2):
    provider: str
    value: int
    year: int
    month: int
    computation_year: int
    computation_month: int


class QuotientFamilialBonusCreditContent(BaseModelV2):
    custodian: QuotientFamilialCustodian
    quotient_familial: QuotientFamilialContent | None = None
    children: list[QuotientFamilialChild] | None = None
