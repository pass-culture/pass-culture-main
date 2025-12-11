import logging

from flask_login import current_user
from werkzeug.exceptions import NotFound

import pcapi.core.offers.models as offers_models
import pcapi.core.reminders.api as reminders_api
import pcapi.core.reminders.models as reminders_models
import pcapi.routes.native.v1.serialization.reminder as serialization
from pcapi.models import db
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from .. import blueprint


logger = logging.getLogger(__name__)


@blueprint.native_route("/me/reminders", methods=["GET"])
@spectree_serialize(response_model=serialization.GetRemindersResponse, api=blueprint.api, on_success_status=200)
@authenticated_and_active_user_required
@atomic()
def get_reminders() -> serialization.GetRemindersResponse:
    reminders = reminders_api.get_reminders(current_user)
    reminders_response = [
        serialization.ReminderResponse(id=reminder.id, offer=reminder.offer) for reminder in reminders
    ]

    return serialization.GetRemindersResponse(reminders=reminders_response)


@blueprint.native_route("/me/reminders", methods=["POST"])
@spectree_serialize(response_model=serialization.ReminderResponse, api=blueprint.api, on_success_status=201)
@authenticated_and_active_user_required
@atomic()
def post_reminder(body: serialization.PostReminderRequest) -> serialization.ReminderResponse:
    offer: offers_models.Offer | None = db.session.query(offers_models.Offer).filter_by(id=body.offer_id).one_or_none()

    if not offer:
        raise NotFound()

    reminder = reminders_api.get_offer_reminder(current_user.id, offer.id)

    if not reminder:
        reminder = reminders_api.create_offer_reminder(current_user, offer)

    return serialization.ReminderResponse(id=reminder.id, offer=reminder.offer)


@blueprint.native_route("/me/reminders/<int:reminder_id>", methods=["DELETE"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@authenticated_and_active_user_required
@atomic()
def delete_reminder(reminder_id: int) -> None:
    reminder: reminders_models.OfferReminder | None = (
        db.session.query(reminders_models.OfferReminder).filter_by(id=reminder_id, user=current_user).one_or_none()
    )

    if not reminder:
        raise NotFound()

    db.session.delete(reminder)
