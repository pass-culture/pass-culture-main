import logging
from typing import Optional

from pcapi.core.subscription.api import get_next_subscription_step
from pcapi.core.users import models as users_models
from pcapi.routes.native.security import authenticated_user_required
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import subscription as serializers


logger = logging.getLogger(__name__)


@blueprint.native_v1.route("/subscription/next_step", methods=["GET"])
@spectree_serialize(
    response_model=serializers.NextSubscriptionStepRequest,
    on_success_status=200,
    api=blueprint.api,
)  # type: ignore
@authenticated_user_required
def next_subscription_step(
    user: users_models.User,
) -> Optional[serializers.NextSubscriptionStepRequest]:
    return serializers.NextSubscriptionStepRequest(next_subscription_step=get_next_subscription_step(user))
