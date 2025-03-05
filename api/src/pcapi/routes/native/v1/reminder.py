import logging

import pcapi.core.reminders.api as reminders_api
import pcapi.core.users.models as users_models
from pcapi.repository import atomic
from pcapi.routes.native.security import authenticated_and_active_user_required
import pcapi.routes.native.v1.serialization.reminder as serialization
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint


logger = logging.getLogger(__name__)


@blueprint.native_route("/reminder", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@authenticated_and_active_user_required
@atomic()
def post_reminder(user: users_models.User, body: serialization.PostReminderRequest) -> None:
    reminders_api.create_reminder(user, body)
