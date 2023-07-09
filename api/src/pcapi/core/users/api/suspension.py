import datetime
import logging
import typing

import sqlalchemy as sa

import pcapi.core.bookings.models as bookings_models
import pcapi.core.bookings.repository as bookings_repository
import pcapi.core.history.api as history_api
import pcapi.core.history.models as history_models
import pcapi.core.mails.transactional as transactional_mails
import pcapi.core.users.models as users_models
from pcapi.models import db
from pcapi.repository import repository

from .. import constants
from .. import exceptions
from .. import models


if typing.TYPE_CHECKING:
    from pcapi.routes.native.v1.serialization import account as account_serialization

logger = logging.getLogger(__name__)


def check_can_unsuspend(user: models.User) -> None:
    """
    A user can ask for unsuspension if it has been suspended upon his
    own request and if the unsuspension time limit has not been exceeded
    """
    reason = user.suspension_reason
    if not reason:
        raise exceptions.NotSuspended()

    if reason != constants.SuspensionReason.UPON_USER_REQUEST:
        raise exceptions.CantAskForUnsuspension()

    suspension_date = typing.cast(datetime.datetime, user.suspension_date)
    days_delta = datetime.timedelta(days=constants.ACCOUNT_UNSUSPENSION_DELAY)
    if suspension_date.date() + days_delta < datetime.date.today():
        raise exceptions.UnsuspensionTimeLimitExceeded()


def suspend_account(
    user: models.User, reason: constants.SuspensionReason, actor: models.User | None, comment: str | None = None
) -> dict[str, int]:
    """
    Suspend a user's account:
        * mark as inactive;
        * mark as suspended (suspension history);
        * remove its admin role if any;
        * cancel its bookings;

    Notes:
        * `actor` can be None if and only if this function is called
        from an automated task (eg cron).
        * a user who suspends his account should be able to connect to
        the application in order to access to some restricted actions.
    """
    import pcapi.core.bookings.api as bookings_api  # avoid import loop

    user.isActive = False
    user.remove_admin_role()
    action = history_api.log_action(
        history_models.ActionType.USER_SUSPENDED,
        author=actor,
        user=user,
        reason=reason.value,
        comment=comment,
        save=False,
    )

    repository.save(user, action)

    sessions = models.UserSession.query.filter_by(userId=user.id)
    repository.delete(*sessions)

    n_bookings = 0

    # Cancel all bookings of the related offerer if the suspended
    # account was the last active offerer's account.
    if reason in (constants.SuspensionReason.FRAUD_SUSPICION, constants.SuspensionReason.BLACKLISTED_DOMAIN_NAME):
        for user_offerer in user.UserOfferers:
            offerer = user_offerer.offerer
            if any(user_of.user.isActive and user_of.user != user for user_of in offerer.UserOfferers):
                continue
            bookings = bookings_repository.find_cancellable_bookings_by_offerer(offerer.id)
            for booking in bookings:
                bookings_api.cancel_booking_for_fraud(booking)
                n_bookings += 1

    n_bookings += _cancel_bookings_of_user_on_requested_account_suspension(user, reason)

    logger.info(
        "Account has been suspended",
        extra={
            "actor": actor.id if actor else None,
            "user": user.id,
            "reason": str(reason),
        },
    )

    return {"cancelled_bookings": n_bookings}


def _cancel_bookings_of_user_on_requested_account_suspension(
    user: users_models.User, reason: constants.SuspensionReason
) -> int:
    import pcapi.core.bookings.api as bookings_api

    bookings_to_cancel = bookings_models.Booking.query.filter(
        bookings_models.Booking.userId == user.id,
        bookings_models.Booking.status == bookings_models.BookingStatus.CONFIRMED,
        sa.or_(
            datetime.datetime.utcnow() < bookings_models.Booking.cancellationLimitDate,
            bookings_models.Booking.cancellationLimitDate.is_(None),
        ),
    ).all()

    cancelled_bookings_count = 0

    for booking in bookings_to_cancel:
        match reason:
            case constants.SuspensionReason.FRAUD_SUSPICION | constants.SuspensionReason.BLACKLISTED_DOMAIN_NAME:
                bookings_api.cancel_booking_for_fraud(booking)
                cancelled_bookings_count += 1

            case constants.SuspensionReason.UPON_USER_REQUEST | constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER:
                bookings_api.cancel_booking_on_user_requested_account_suspension(booking)
                cancelled_bookings_count += 1

    return cancelled_bookings_count


def unsuspend_account(
    user: models.User, actor: models.User, comment: str | None = None, send_email: bool = False
) -> None:
    user.isActive = True
    action = history_api.log_action(
        history_models.ActionType.USER_UNSUSPENDED, author=actor, user=user, comment=comment, save=False
    )

    repository.save(user, action)

    logger.info(
        "Account has been unsuspended",
        extra={
            "actor": actor.id,
            "user": user.id,
            "send_email": send_email,
        },
    )

    if send_email:
        transactional_mails.send_unsuspension_email(user)


def bulk_unsuspend_account(user_ids: list[int], actor: models.User) -> None:
    models.User.query.filter(models.User.id.in_(user_ids)).update(
        values={"isActive": True},
        synchronize_session=False,
    )
    users = models.User.query.filter(models.User.id.in_(user_ids)).all()
    for user in users:
        history_api.log_action(history_models.ActionType.USER_UNSUSPENDED, author=actor, user=user)

    db.session.commit()

    logger.info(
        "Some accounts have been reactivated",
        extra={
            "actor": actor.id,
            "users": user_ids,
        },
    )
