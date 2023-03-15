import datetime

from pydantic import fields
from pydantic import validator

import pcapi.core.fraud.utils as fraud_utils
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import profile_options
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


class CallToActionMessage(BaseModel):
    title: str | None = fields.Field(None, alias="callToActionTitle")
    link: str | None = fields.Field(None, alias="callToActionLink")
    icon: subscription_models.CallToActionIcon | None = fields.Field(None, alias="callToActionIcon")

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True
        use_enum_values = True


class SubscriptionMessage(BaseModel):
    user_message: str
    call_to_action: CallToActionMessage | None
    pop_over_icon: subscription_models.PopOverIcon | None
    updated_at: datetime.datetime | None

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True
        json_encoders = {datetime.datetime: format_into_utc_date}
        use_enum_values = True


class NextSubscriptionStepResponse(BaseModel):
    next_subscription_step: subscription_models.SubscriptionStep | None
    # TODO: (Lixxday) 23/02/2023: Remove "stepper_includes_phone_validation" when the app does not use it anymore
    # - when this ticket is done: https://passculture.atlassian.net/browse/PC-20003
    # - and after a forced update of the app
    stepper_includes_phone_validation: bool
    maintenance_page_type: subscription_models.MaintenancePageType | None
    allowed_identity_check_methods: list[subscription_models.IdentityCheckMethod]
    has_identity_check_pending: bool
    subscription_message: SubscriptionMessage | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class SubscriptionStepDetailsResponse(BaseModel):
    name: subscription_models.SubscriptionStep
    title: subscription_models.SubscriptionStepTitle
    subtitle: str | None
    completion_state: subscription_models.SubscriptionStepCompletionState

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        use_enum_values = True


class SubscriptionStepperResponse(BaseModel):
    subscription_steps_to_display: list[SubscriptionStepDetailsResponse]
    title: str
    subtitle: str | None
    error_message: str | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class ProfileResponse(BaseModel):
    activity: profile_options.ACTIVITY_ID_ENUM
    address: str
    city: str
    first_name: str
    last_name: str
    postal_code: str
    school_type: profile_options.SCHOOL_TYPE_ID_ENUM | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        use_enum_values = True


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
    def mandatory_string_fields_cannot_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("This field cannot be empty")
        return v

    @validator("first_name", "last_name")
    def string_must_contain_latin_characters(cls, v: str) -> str:
        fraud_utils.validate_name(v)
        return v

    @validator("city")
    def city_must_be_valid(cls, v: str) -> str:
        fraud_utils.validate_city(v)
        return v

    @validator("address")
    def address_must_be_valid(cls, v: str) -> str:
        fraud_utils.validate_address(v)
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
