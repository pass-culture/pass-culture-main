import logging

from werkzeug.exceptions import NotFound

import pcapi.core.offers.models as offers_models
import pcapi.core.reminders.api as reminders_api
import pcapi.core.reminders.models as reminders_models
import pcapi.core.users.models as users_models
import pcapi.routes.native.v1.serialization.reminder as serialization
from pcapi.models import db
from pcapi.repository.session_management import atomic
from pcapi.routes.native.security import authenticated_and_active_user_required
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
    future_offer: offers_models.FutureOffer = (
        db.session.query(offers_models.FutureOffer)
        .filter(offers_models.FutureOffer.offerId == body.offer_id)
        .one_or_none()
    )
    if not future_offer:
        raise NotFound()

    reminder = reminders_api.get_future_offer_reminder(user.id, future_offer.id)

    if not reminder:
        reminder = reminders_api.create_future_offer_reminder(user, future_offer)
        # NOTE: (tcoudray-pass, 04/06/2025)
        # On effectue une double écriture avant de remplacer
        # `FutureOfferReminder` par `OfferReminder`
        reminders_api.create_offer_reminder(user, future_offer.offer)

    return serialization.ReminderResponse(id=reminder.id, offer=reminder.futureOffer.offer)


@blueprint.native_route("/me/reminders/<int:reminder_id>", methods=["DELETE"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@authenticated_and_active_user_required
@atomic()
def delete_reminder(user: users_models.User, reminder_id: int) -> None:
    # NOTE: (tcoudray-pass, 04/06/2025)
    # On effectue une double écriture avant de remplacer
    # `FutureOfferReminder` par `OfferReminder`
    reminder: reminders_models.FutureOfferReminder = (
        db.session.query(reminders_models.FutureOfferReminder).filter_by(id=reminder_id, user=user).first_or_404()
    )
    reminders_api.delete_offer_reminder(user, reminder.futureOffer.offer.id)

    reminders_api.delete_future_offer_reminder(user, reminder_id)
