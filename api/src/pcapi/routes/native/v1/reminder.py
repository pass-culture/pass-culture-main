import logging

import pcapi.core.reminders.api as reminders_api
import pcapi.core.users.models as users_models
from pcapi.repository import atomic
from pcapi.routes.native.security import authenticated_and_active_user_required
import pcapi.routes.native.v1.serialization.reminder as serialization
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint


logger = logging.getLogger(__name__)


@blueprint.native_route("/me/reminders", methods=["GET"])
@spectree_serialize(response_model=serialization.GetRemindersResponse, api=blueprint.api, on_success_status=200)
@authenticated_and_active_user_required
@atomic()
def get_reminders(user: users_models.User) -> serialization.GetRemindersResponse:
    reminders = reminders_api.get_reminders(user)
    reminders_reponse = [
        serialization.ReminderResponse(id=reminder.id, offer=reminder.futureOffer.offer) for reminder in reminders
    ]

    return serialization.GetRemindersResponse(reminders=reminders_reponse)


@blueprint.native_route("/me/reminders", methods=["POST"])
@spectree_serialize(response_model=serialization.ReminderResponse, api=blueprint.api, on_success_status=201)
@authenticated_and_active_user_required
@atomic()
def post_reminder(user: users_models.User, body: serialization.PostReminderRequest) -> serialization.ReminderResponse:
    reminder = reminders_api.create_reminder(user, body)

    return serialization.ReminderResponse(id=reminder.id, offer=reminder.futureOffer.offer)


@blueprint.native_route("/me/reminders/<int:reminder_id>", methods=["DELETE"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@authenticated_and_active_user_required
@atomic()
def delete_reminder(user: users_models.User, reminder_id: int) -> None:
    reminders_api.delete_reminder(user, reminder_id)
