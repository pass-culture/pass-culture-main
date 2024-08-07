import datetime

from pydantic.v1 import fields
from pydantic.v1 import validator

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


class SubscriptionMessageV2(BaseModel):
    user_message: str
    message_summary: str | None = None
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
    allowed_identity_check_methods: list[subscription_models.IdentityCheckMethod]
    maintenance_page_type: subscription_models.MaintenancePageType | None
    title: str
    subtitle: str | None
    error_message: str | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class SubscriptionStepperResponseV2(BaseModel):
    subscription_steps_to_display: list[SubscriptionStepDetailsResponse]
    allowed_identity_check_methods: list[subscription_models.IdentityCheckMethod]
    has_identity_check_pending: bool
    maintenance_page_type: subscription_models.MaintenancePageType | None
    next_subscription_step: subscription_models.SubscriptionStep | None
    title: str
    subtitle: str | None
    subscription_message: SubscriptionMessageV2 | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class ProfileContent(BaseModel):
    activity: profile_options.ActivityValueEnum
    address: str | None  # Address is nullable for backward compatibility
    city: str
    first_name: str
    last_name: str
    postal_code: str
    school_type: profile_options.SchoolTypeValueEnum | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        use_enum_values = True


class ProfileResponse(BaseModel):
    profile: ProfileContent | None = fields.Field(None)


class ProfileUpdateRequest(BaseModel):
    activity_id: profile_options.ActivityIdEnum
    address: str
    city: str
    first_name: str
    last_name: str
    postal_code: str
    school_type_id: profile_options.SchoolTypeIdEnum | None

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


class ActivityResponseModel(BaseModel):
    id: profile_options.ActivityIdEnum
    label: str
    description: str | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class ActivityTypesResponse(BaseModel):
    activities: list[ActivityResponseModel]


class IdentificationSessionResponse(BaseModel):
    identificationUrl: str


class IdentificationSessionRequest(BaseModel):
    redirectUrl: str
