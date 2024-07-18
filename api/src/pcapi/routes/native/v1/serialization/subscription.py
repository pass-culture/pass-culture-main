import datetime

from pydantic.v1 import fields
from pydantic.v1 import validator

import pcapi.core.fraud.utils as fraud_utils
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import profile_options
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date
from pydantic import field_validator, ConfigDict


class CallToActionMessage(BaseModel):
    title: str | None = fields.Field(None, alias="callToActionTitle")
    link: str | None = fields.Field(None, alias="callToActionLink")
    icon: subscription_models.CallToActionIcon | None = fields.Field(None, alias="callToActionIcon")
    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True, use_enum_values=True)


class SubscriptionMessage(BaseModel):
    user_message: str
    call_to_action: CallToActionMessage | None
    pop_over_icon: subscription_models.PopOverIcon | None
    updated_at: datetime.datetime | None
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True, json_encoders={datetime.datetime: format_into_utc_date}, use_enum_values=True)


class SubscriptionMessageV2(BaseModel):
    user_message: str
    message_summary: str | None = None
    call_to_action: CallToActionMessage | None
    pop_over_icon: subscription_models.PopOverIcon | None
    updated_at: datetime.datetime | None
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True, json_encoders={datetime.datetime: format_into_utc_date}, use_enum_values=True)


class NextSubscriptionStepResponse(BaseModel):
    next_subscription_step: subscription_models.SubscriptionStep | None
    maintenance_page_type: subscription_models.MaintenancePageType | None
    allowed_identity_check_methods: list[subscription_models.IdentityCheckMethod]
    has_identity_check_pending: bool
    subscription_message: SubscriptionMessage | None
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class SubscriptionStepDetailsResponse(BaseModel):
    name: subscription_models.SubscriptionStep
    title: subscription_models.SubscriptionStepTitle
    subtitle: str | None
    completion_state: subscription_models.SubscriptionStepCompletionState
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, use_enum_values=True)


class SubscriptionStepperResponse(BaseModel):
    subscription_steps_to_display: list[SubscriptionStepDetailsResponse]
    allowed_identity_check_methods: list[subscription_models.IdentityCheckMethod]
    maintenance_page_type: subscription_models.MaintenancePageType | None
    title: str
    subtitle: str | None
    error_message: str | None
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class SubscriptionStepperResponseV2(BaseModel):
    subscription_steps_to_display: list[SubscriptionStepDetailsResponse]
    allowed_identity_check_methods: list[subscription_models.IdentityCheckMethod]
    has_identity_check_pending: bool
    maintenance_page_type: subscription_models.MaintenancePageType | None
    next_subscription_step: subscription_models.SubscriptionStep | None
    title: str
    subtitle: str | None
    subscription_message: SubscriptionMessageV2 | None
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class ProfileContent(BaseModel):
    activity: profile_options.ACTIVITY_VALUE_ENUM
    address: str | None  # Address is nullable for backward compatibility
    city: str
    first_name: str
    last_name: str
    postal_code: str
    school_type: profile_options.SCHOOL_TYPE_VALUE_ENUM | None
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, use_enum_values=True)


class ProfileResponse(BaseModel):
    profile: ProfileContent | None = fields.Field(None)


class ProfileUpdateRequest(BaseModel):
    activity_id: profile_options.ACTIVITY_ID_ENUM
    address: str
    city: str
    first_name: str
    last_name: str
    postal_code: str
    school_type_id: profile_options.SCHOOL_TYPE_ID_ENUM | None
    model_config = ConfigDict(alias_generator=to_camel)

    @field_validator("first_name", "last_name", "address", "city", "postal_code")
    @classmethod
    def mandatory_string_fields_cannot_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("This field cannot be empty")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def string_must_contain_latin_characters(cls, v: str) -> str:
        fraud_utils.validate_name(v)
        return v

    @field_validator("city")
    @classmethod
    def city_must_be_valid(cls, v: str) -> str:
        fraud_utils.validate_city(v)
        return v

    @field_validator("address")
    @classmethod
    def address_must_be_valid(cls, v: str) -> str:
        fraud_utils.validate_address(v)
        return v


class ActivityResponseModel(BaseModel):
    id: profile_options.ACTIVITY_ID_ENUM
    label: str
    description: str | None
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class ActivityTypesResponse(BaseModel):
    activities: list[ActivityResponseModel]


class IdentificationSessionResponse(BaseModel):
    identificationUrl: str


class IdentificationSessionRequest(BaseModel):
    redirectUrl: str
