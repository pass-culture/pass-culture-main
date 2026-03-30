import datetime

import pydantic as pydantic_v2

from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.routes.serialization import HttpBodyModel


class CallToActionMessageV2(HttpBodyModel):
    title: str | None = pydantic_v2.Field(None, alias="callToActionTitle")
    link: str | None = pydantic_v2.Field(None, alias="callToActionLink")
    icon: subscription_schemas.CallToActionIcon | None = pydantic_v2.Field(None, alias="callToActionIcon")

    model_config = pydantic_v2.ConfigDict(
        use_enum_values=True,
    )


class SubscriptionMessageV2(HttpBodyModel):
    user_message: str
    message_summary: str | None = None
    call_to_action: CallToActionMessageV2 | None = None
    pop_over_icon: subscription_schemas.PopOverIcon | None = None
    updated_at: datetime.datetime | None = None

    model_config = pydantic_v2.ConfigDict(
        use_enum_values=True,
    )


class SubscriptionStepDetailsResponseV2(HttpBodyModel):
    name: subscription_schemas.SubscriptionStep
    title: subscription_schemas.SubscriptionStepTitle
    subtitle: str | None = None
    completion_state: subscription_schemas.SubscriptionStepCompletionState

    model_config = pydantic_v2.ConfigDict(
        use_enum_values=True,
    )


class SubscriptionStepperResponseV2(HttpBodyModel):
    subscription_steps_to_display: list[SubscriptionStepDetailsResponseV2]
    allowed_identity_check_methods: list[subscription_schemas.IdentityCheckMethod]
    has_identity_check_pending: bool
    maintenance_page_type: subscription_schemas.MaintenancePageType | None = None
    next_subscription_step: subscription_schemas.SubscriptionStep | None = None
    title: str
    subtitle: str | None = None
    subscription_message: SubscriptionMessageV2 | None = None
