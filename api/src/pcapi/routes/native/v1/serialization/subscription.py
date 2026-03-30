import datetime

import pydantic as pydantic_v2

from pcapi.core.subscription import profile_options
from pcapi.core.subscription import utils as subscription_utils
from pcapi.core.users import models as users_models
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel
from pcapi.serialization.exceptions import PydanticError


class ProfileContent(HttpBodyModel):
    activity: profile_options.ActivityValueEnum
    address: str | None = None  # Address is nullable for backward compatibility
    city: str
    first_name: str
    last_name: str
    postal_code: str
    school_type: profile_options.SchoolTypeValueEnum | None = None

    model_config = pydantic_v2.ConfigDict(
        use_enum_values=True,
    )


class ProfileResponse(HttpBodyModel):
    profile: ProfileContent | None = None


class ProfileUpdateRequest(HttpQueryParamsModel):
    activity_id: profile_options.ActivityIdEnum
    address: str
    city: str
    first_name: str
    last_name: str
    postal_code: str
    school_type_id: profile_options.SchoolTypeIdEnum | None = None

    @pydantic_v2.field_validator("first_name", "last_name", "address", "city", "postal_code", mode="after")
    @classmethod
    def mandatory_string_fields_cannot_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise PydanticError("This field cannot be empty")
        return v

    @pydantic_v2.field_validator("first_name", "last_name", mode="after")
    @classmethod
    def string_must_contain_latin_characters(cls, v: str) -> str:
        subscription_utils.validate_name(v)
        return v

    @pydantic_v2.field_validator("city", mode="after")
    @classmethod
    def city_must_be_valid(cls, v: str) -> str:
        subscription_utils.validate_city(v)
        return v

    @pydantic_v2.field_validator("address", mode="after")
    @classmethod
    def address_must_be_valid(cls, v: str) -> str:
        subscription_utils.validate_address(v)
        return v


class ActivityResponseModel(HttpBodyModel):
    id: profile_options.ActivityIdEnum
    label: str
    description: str | None = None


class ActivityTypesResponse(HttpBodyModel):
    activities: list[ActivityResponseModel]


class IdentificationSessionResponse(HttpBodyModel):
    identificationUrl: str


class IdentificationSessionRequest(HttpQueryParamsModel):
    redirectUrl: str


class BonusCreditRequest(HttpQueryParamsModel):
    last_name: str
    common_name: str | None = None
    first_names: list[str]
    birth_date: datetime.date
    gender: users_models.GenderEnum
    birth_country_cog_code: str
    birth_city_cog_code: str | None = None
