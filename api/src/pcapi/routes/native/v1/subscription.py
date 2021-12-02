import logging
from typing import Optional

from pcapi.core.subscription import api as subscription_api
from pcapi.core.users import models as users_models
from pcapi.routes.native.security import authenticated_user_required
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import subscription as serializers


logger = logging.getLogger(__name__)


@blueprint.native_v1.route("/subscription/next_step", methods=["GET"])
@spectree_serialize(
    response_model=serializers.NextSubscriptionStepResponse,
    on_success_status=200,
    api=blueprint.api,
)  # type: ignore
@authenticated_user_required
def next_subscription_step(
    user: users_models.User,
) -> Optional[serializers.NextSubscriptionStepResponse]:
    return serializers.NextSubscriptionStepResponse(
        next_subscription_step=subscription_api.get_next_subscription_step(user),
        allowed_identity_check_methods=subscription_api.get_allowed_identity_check_methods(user),
        maintenance_page_type=subscription_api.get_maintenance_page_type(user),
    )


@blueprint.native_v1.route("/subscription/profile", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_user_required
def update_profile(user: users_models.User, body: serializers.ProfileUpdateRequest) -> None:
    subscription_api.update_user_profile(
        user,
        first_name=body.first_name,
        last_name=body.last_name,
        address=body.address,
        city=body.city,
        postal_code=body.postal_code,
        activity=body.activity.value,
        school_type=body.school_type,
    )
