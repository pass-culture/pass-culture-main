from typing import Optional

from pydantic import validator

from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import profile_options
from pcapi.core.users import models as users_models
from pcapi.serialization.utils import is_latin
from pcapi.serialization.utils import to_camel

from . import BaseModel


class NextSubscriptionStepResponse(BaseModel):
    next_subscription_step: Optional[subscription_models.SubscriptionStep]
    maintenance_page_type: Optional[subscription_models.MaintenancePageType]
    allowed_identity_check_methods: list[subscription_models.IdentityCheckMethod]
    has_identity_check_pending: bool

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class ProfileUpdateRequest(BaseModel):
    activity_id: Optional[profile_options.ACTIVITY_ID_ENUM]
    activity: Optional[users_models.ActivityEnum]  # TODO: CorentinN: remove this field when frontend sends activity_id
    address: Optional[str]
    city: str
    first_name: str
    last_name: str
    postal_code: str
    school_type_id: Optional[profile_options.SCHOOL_TYPE_ID_ENUM]

    class Config:
        alias_generator = to_camel

    @validator("first_name", "last_name", "address", "city")
    def string_must_contain_latin_characters(cls, v):  # pylint: disable=no-self-argument
        if not is_latin(v):
            raise ValueError("Les champs textuels doivent contenir des caractères latins")
        return v


class SchoolTypeResponseModel(BaseModel):
    id: profile_options.SCHOOL_TYPE_ID_ENUM
    description: Optional[str]
    label: str

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class ActivityResponseModel(BaseModel):
    id: profile_options.ACTIVITY_ID_ENUM
    label: str
    description: Optional[str]
    associated_school_types_ids: Optional[list[profile_options.SCHOOL_TYPE_ID_ENUM]]

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class ProfileOptionsResponse(BaseModel):
    activities: list[ActivityResponseModel]
    school_types: list[SchoolTypeResponseModel]
