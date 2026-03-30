import logging

from flask_login import current_user

from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import fraud_check_api as fraud_api
from pcapi.core.subscription import messages as subscription_messages
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint
from .serialization import subscription as serializers


logger = logging.getLogger(__name__)


@blueprint.native_route("/subscription/stepper", version="v2", methods=["GET"])
@spectree_serialize(
    response_model=serializers.SubscriptionStepperResponseV2,
    on_success_status=200,
    api=blueprint.api,
)
@authenticated_and_active_user_required
def get_subscription_stepper() -> serializers.SubscriptionStepperResponseV2:
    user_subscription_state = subscription_api.get_user_subscription_state(
        current_user, phone_validation_state_enabled=True
    )
    subscription_message = user_subscription_state.subscription_message
    stepper_header = subscription_messages.get_stepper_title_and_subtitle(current_user, user_subscription_state)
    subscription_steps_to_display = subscription_messages.get_subscription_steps_to_display(
        current_user, user_subscription_state, phone_validation_step_enabled=True
    )

    return serializers.SubscriptionStepperResponseV2(
        subscription_steps_to_display=[
            serializers.SubscriptionStepDetailsResponseV2(
                title=step.title,
                subtitle=step.subtitle,
                completion_state=step.completion_state,
                name=step.name,
            )
            for step in subscription_steps_to_display
        ],
        allowed_identity_check_methods=subscription_api.get_allowed_identity_check_methods(current_user),
        has_identity_check_pending=fraud_api.has_user_pending_identity_check(current_user),
        maintenance_page_type=subscription_api.get_maintenance_page_type(current_user),
        next_subscription_step=user_subscription_state.next_step,
        title=stepper_header.title,
        subtitle=stepper_header.subtitle,
        subscription_message=serializers.SubscriptionMessageV2.model_validate(subscription_message)
        if subscription_message
        else None,
    )
