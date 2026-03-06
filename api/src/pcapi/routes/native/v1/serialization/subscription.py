import datetime

import pydantic

from pcapi.core.subscription import profile_options
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.subscription import utils as subscription_utils
from pcapi.core.users import models as users_models
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


class CallToActionMessageV2(HttpBodyModel):
    title: str | None = pydantic.Field(alias="callToActionTitle")
    link: str | None = pydantic.Field(alias="callToActionLink")
    icon: subscription_schemas.CallToActionIcon | None = pydantic.Field(alias="callToActionIcon")

    model_config = pydantic.ConfigDict(
        use_enum_values=True,
    )


class SubscriptionMessageV2(HttpBodyModel):
    user_message: str
    message_summary: str | None = None
    call_to_action: CallToActionMessageV2 | None = None
    pop_over_icon: subscription_schemas.PopOverIcon | None = None
    updated_at: datetime.datetime | None = None

    model_config = pydantic.ConfigDict(
        use_enum_values=True,
    )


class SubscriptionStepDetailsResponse(HttpBodyModel):
    name: subscription_schemas.SubscriptionStep
    title: subscription_schemas.SubscriptionStepTitle
    subtitle: str | None = None
    completion_state: subscription_schemas.SubscriptionStepCompletionState

    model_config = pydantic.ConfigDict(
        use_enum_values=True,
    )


class SubscriptionStepperResponseV2(HttpBodyModel):
    subscription_steps_to_display: list[SubscriptionStepDetailsResponse]
    allowed_identity_check_methods: list[subscription_schemas.IdentityCheckMethod]
    has_identity_check_pending: bool
    maintenance_page_type: subscription_schemas.MaintenancePageType | None = None
    next_subscription_step: subscription_schemas.SubscriptionStep | None = None
    title: str
    subtitle: str | None = None
    subscription_message: SubscriptionMessageV2 | None = None


class ProfileContent(HttpBodyModel):
    activity: profile_options.ActivityValueEnum
    address: str | None  # Address is nullable for backward compatibility
    city: str
    first_name: str
    last_name: str
    postal_code: str
    school_type: profile_options.SchoolTypeValueEnum | None = None

    model_config = pydantic.ConfigDict(
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

    @pydantic.field_validator("first_name", "last_name", "address", "city", "postal_code", mode="after")
    @classmethod
    def mandatory_string_fields_cannot_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("This field cannot be empty")
        return v

    @pydantic.field_validator("first_name", "last_name", mode="after")
    @classmethod
    def string_must_contain_latin_characters(cls, v: str) -> str:
        subscription_utils.validate_name(v)
        return v

    @pydantic.field_validator("city", mode="after")
    @classmethod
    def city_must_be_valid(cls, v: str) -> str:
        subscription_utils.validate_city(v)
        return v

    @pydantic.field_validator("address", mode="after")
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
