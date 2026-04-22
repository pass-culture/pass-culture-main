"""
Mostly duplications from the API Particulier response models to prevent breaking changes if
their returned responses ever changes
"""

import datetime
from typing import Annotated

from pydantic import BaseModel as BaseModelV2
from pydantic import StringConstraints

from pcapi.core.users import models as users_models


CogCode = Annotated[str, StringConstraints(strip_whitespace=True, to_upper=True, min_length=5, max_length=5)]


class Person(BaseModelV2):
    last_name: str
    common_name: str | None = None
    first_names: list[str]
    birth_date: datetime.date
    gender: users_models.GenderEnum
    birth_country_cog_code: CogCode
    birth_city_cog_code: CogCode | None = None


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
    custodian: Person
    quotient_familial: QuotientFamilialContent | None = None
    children: list[QuotientFamilialChild] | None = None
    http_status_code: int | None = None
