import datetime

from pydantic import BaseModel

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


class QuotientFamilialBonusCreditContent(BaseModel):
    custodian: QuotientFamilialCustodian
    quotient_familial: QuotientFamilialContent | None = None
