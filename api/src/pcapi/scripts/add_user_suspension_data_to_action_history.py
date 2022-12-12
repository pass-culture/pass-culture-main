"""Script to add all data of the UserSuspension table to the ActionHistory table.
It does not change anything to ther UserSuspension table.
WARNING: run it once, or you'll have duplicate data in ActionHistory table."""

import pcapi.core.history.models as history_models
import pcapi.core.users.constants as users_constants
import pcapi.core.users.models as users_models
from pcapi.models import db


YIELD_COUNT_PER_DB_QUERY = 2


def _add_user_suspension_to_action_history(user_suspension: users_models.UserSuspension) -> None:
    if user_suspension.eventType == users_constants.SuspensionEventType.SUSPENDED:
        action_type = history_models.ActionType.USER_SUSPENDED
    else:
        action_type = history_models.ActionType.USER_UNSUSPENDED

    # Helps find faulty data if the updating process failed at some point
    extraData = {"origin": "user_suspension"}
    if user_suspension.reasonCode:
        extraData["reason"] = user_suspension.reasonCode.value
        action = history_models.ActionHistory(
            actionDate=user_suspension.eventDate,
            actionType=action_type,
            authorUser=user_suspension.actorUser,
            user=user_suspension.user,
            extraData=extraData,
        )
    else:
        action = history_models.ActionHistory(
            actionDate=user_suspension.eventDate,
            actionType=action_type,
            authorUser=user_suspension.actorUser,
            user=user_suspension.user,
            extraData=extraData,
        )

    db.session.add(action)


def update_user_suspension_chunk(min_user_id: int, max_user_id: int) -> None:

    user_suspension_ids = list(range(min_user_id, max_user_id + 1))

    chunk = users_models.UserSuspension.query.filter(users_models.UserSuspension.id.in_(user_suspension_ids)).all()
    for user_suspension in chunk:
        _add_user_suspension_to_action_history(user_suspension)
    db.session.commit()

    print(f"{len(chunk)} user suspensions updated")


def update_user_suspension_loop(chunk_size: int) -> None:

    max_id = users_models.UserSuspension.query.order_by(users_models.UserSuspension.id.desc()).first().id

    for current_min_id in range(1, max_id + 1, chunk_size):
        update_user_suspension_chunk(current_min_id, current_min_id + chunk_size - 1)


if __name__ == "__main__":

    from pcapi.flask_app import app

    with app.app_context():
        print("Update starting")
        update_user_suspension_loop(chunk_size=YIELD_COUNT_PER_DB_QUERY)
        print("Update complete")
