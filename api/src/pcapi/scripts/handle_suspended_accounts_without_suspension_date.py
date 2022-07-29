from datetime import datetime

import sqlalchemy as sqla

import pcapi.core.users.constants as users_constants
import pcapi.core.users.models as users_models
from pcapi.models import db
from pcapi.utils.chunks import get_chunks


def get_users_latest_event_row_id_query() -> sqla.orm.Query:
    """
    For each each user, find out which its most recent row.
    This could be used to find out whether a user's latest event is a
    suspension upon his request.

    Note: the ids are a sequence of integer. This means that a row with
    a greater id represents a more recent event in time. eventDate is
    not a great choice since it can contain null values wich lead to an
    unexpected result.
    """
    return users_models.UserSuspension.query.group_by(users_models.UserSuspension.userId).with_entities(
        users_models.UserSuspension.userId, sqla.func.max(users_models.UserSuspension.id)
    )


def get_suspended_users_without_a_suspension_date_query() -> sqla.orm.Query:
    """
    Find users for which the last suspension event is a suspension upon
    their request and which has no event date.
    """
    users_with_latest_row_id = get_users_latest_event_row_id_query().subquery()

    return (
        users_models.UserSuspension.query.join(
            users_with_latest_row_id, users_with_latest_row_id.c.userId == users_models.UserSuspension.userId
        )
        .filter(
            users_models.UserSuspension.eventType == users_constants.SuspensionEventType.SUSPENDED,
            users_models.UserSuspension.reasonCode == users_constants.SuspensionReason.UPON_USER_REQUEST,
            users_models.UserSuspension.eventDate == None,
            # the user's most recent event
            users_with_latest_row_id.c.max == users_models.UserSuspension.id,
        )
        .with_entities(users_models.UserSuspension.userId)
        .distinct(users_models.UserSuspension.userId)
    )


def mark_accounts_as_deleted(event_date: datetime, actor_user_id: int) -> None:
    query = get_suspended_users_without_a_suspension_date_query().yield_per(3_000)
    user_ids = [row[0] for row in query]

    for chunk in get_chunks(user_ids, 1_000):  # type: ignore
        for user_id in chunk:
            db.session.add(
                users_models.UserSuspension(
                    userId=user_id,
                    eventType=users_constants.SuspensionEventType.SUSPENDED,
                    eventDate=event_date,
                    actorUserId=actor_user_id,
                    reasonCode=users_constants.SuspensionReason.DELETED,
                )
            )

        db.session.commit()
