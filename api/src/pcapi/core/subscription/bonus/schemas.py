import datetime

from pydantic import BaseModel
from pydantic import field_validator

from pcapi.core.users import models as users_models


class QuotientFamilialCustodian(BaseModel):
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

    @field_validator("gender", mode="before")
    @classmethod
    def parse_gender(cls, gender: str | users_models.GenderEnum) -> users_models.GenderEnum:
        if isinstance(gender, str):
            return users_models.GenderEnum[gender]
        return gender


class QuotientFamilialContent(BaseModel):
    """
    Duplicated from api_particulier.QuotientFamilial to prevent breaking changes if
    the API Particulier return type ever changes
    """

    provider: str
    value: int
    year: int
    month: int
    computation_year: int
    computation_month: int


class BonusCreditContent(BaseModel):
    custodian: QuotientFamilialCustodian
    quotient_familial: QuotientFamilialContent | None = None
