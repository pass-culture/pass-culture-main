from pydantic import validator

from pcapi.core.fraud.utils import has_latin_or_numeric_chars
from pcapi.core.fraud.utils import is_latin
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import profile_options
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class NextSubscriptionStepResponse(BaseModel):
    next_subscription_step: subscription_models.SubscriptionStep | None
    stepper_includes_phone_validation: bool
    maintenance_page_type: subscription_models.MaintenancePageType | None
    allowed_identity_check_methods: list[subscription_models.IdentityCheckMethod]
    has_identity_check_pending: bool

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class ProfileUpdateRequest(BaseModel):
    activity_id: profile_options.ACTIVITY_ID_ENUM
    address: str
    city: str
    first_name: str
    last_name: str
    postal_code: str
    school_type_id: profile_options.SCHOOL_TYPE_ID_ENUM | None

    class Config:
        alias_generator = to_camel

    @validator("first_name", "last_name", "address", "city", "postal_code")
    def mandatory_string_fields_cannot_be_empty(cls, v):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        v = v.strip()
        if not v:
            raise ValueError("This field cannot be empty")
        return v

    @validator("first_name", "last_name", "city")
    def string_must_contain_latin_characters(cls, v):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        if not is_latin(v):
            raise ValueError("Les champs textuels doivent contenir des caractères latins")
        return v

    @validator("address")
    def address_must_be_valid(cls, v):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        if not has_latin_or_numeric_chars(v):
            raise ValueError("L'adresse doit contenir des caractères alphanumériques")

        return v


class SchoolTypeResponseModel(BaseModel):
    id: profile_options.SCHOOL_TYPE_ID_ENUM
    description: str | None
    label: str

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class ActivityResponseModel(BaseModel):
    id: profile_options.ACTIVITY_ID_ENUM
    label: str
    description: str | None
    associated_school_types_ids: list[profile_options.SCHOOL_TYPE_ID_ENUM] | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class ProfileOptionsResponse(BaseModel):
    activities: list[ActivityResponseModel]
    school_types: list[SchoolTypeResponseModel]


class IdentificationSessionResponse(BaseModel):
    identificationUrl: str


class IdentificationSessionRequest(BaseModel):
    redirectUrl: str
