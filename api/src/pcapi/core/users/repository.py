from datetime import date
from datetime import datetime
import logging
import typing

from dateutil.relativedelta import relativedelta
from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlalchemy.orm as sa_orm
from sqlalchemy.sql.functions import func

import pcapi.core.offerers.models as offerers_models
from pcapi.models import db
from pcapi.utils import crypto
import pcapi.utils.email as email_utils

from . import exceptions
from . import models


logger = logging.getLogger(__name__)


HASHED_PLACEHOLDER = crypto.hash_password("placeholder")


def check_user_and_credentials(user: models.User | None, password: str, allow_inactive: bool = False) -> None:
    # Order is important to prevent end-user to guess user emails
    # We need to check email and password before checking email validation
    if not user or not user.password:
        # Hash the given password, just like we would do if the user
        # or the password existed. This avoids user enumeration by comparing
        # server response time.
        crypto.check_password(password, HASHED_PLACEHOLDER)
        raise exceptions.InvalidIdentifier()
    if not (user.checkPassword(password) and (user.isActive or allow_inactive)):
        logger.info(
            "Failed authentication attempt",
            extra={"identifier": user.email, "user": user.id, "avoid_current_user": True, "success": False},
            technical_message_id="users.login",
        )
        raise exceptions.InvalidIdentifier()
    if not user.isEmailValidated:
        raise exceptions.UnvalidatedAccount()


def get_user_with_credentials(identifier: str, password: str, allow_inactive: bool = False) -> models.User:
    user = find_user_by_email(identifier)
    if not user:
        logger.info(
            "Failed authentication attempt",
            extra={"identifier": identifier, "user": None, "avoid_current_user": True, "success": False},
            technical_message_id="users.login",
        )
    check_user_and_credentials(user, password, allow_inactive)
    if user:
        logger.info(
            "Successful authentication attempt",
            extra={"identifier": identifier, "user": user.id, "avoid_current_user": True, "success": True},
            technical_message_id="users.login",
        )
    return typing.cast(models.User, user)


def _find_user_by_email_query(email: str) -> BaseQuery:
    return db.session.query(models.User).filter(func.lower(models.User.email) == email_utils.sanitize_email(email))


def find_user_by_email(email: str) -> models.User | None:
    return _find_user_by_email_query(email).one_or_none()


def find_pro_or_non_attached_pro_user_by_email_query(email: str) -> BaseQuery:
    return _find_user_by_email_query(email).filter(sa.or_(models.User.has_pro_role, models.User.has_non_attached_pro_role))  # type: ignore[type-var]


def has_access(user: models.User, offerer_id: int) -> bool:
    """Return whether the user has access to the requested offerer's data."""
    if user.has_admin_role:
        return True
    return (
        db.session.query(offerers_models.UserOfferer)
        .filter(
            offerers_models.UserOfferer.offererId == offerer_id,
            offerers_models.UserOfferer.userId == user.id,
            offerers_models.UserOfferer.isValidated,
        )
        .exists()
        .scalar()
    )


def has_access_to_venues(user: models.User, venue_ids: list[int]) -> bool:
    """Return whether the user has access to all the requested venues' data."""
    return db.session.execute(
        sa.select(
            sa.cast(postgresql.array(venue_ids), postgresql.ARRAY(postgresql.BIGINT)).contained_by(
                sa.func.array_agg(offerers_models.Venue.id)
            )
        )
        .select_from(offerers_models.Venue)
        .join(offerers_models.Offerer)
        .join(offerers_models.UserOfferer)
        .where(offerers_models.UserOfferer.userId == user.id, offerers_models.UserOfferer.isValidated)
        .group_by(offerers_models.UserOfferer.userId)
    ).scalar()


def get_users_that_had_birthday_since(since: date, age: int) -> list[models.User]:
    """
    Get users that are eligible between `since` (excluded) and now (included) and that have
    created their account before `today`
    If `since` is "yesterday", on 29th of February:
        `today - relativedelta(years=18) = YYYY-02-28`
        `since - relativedelta(years=18) = YYYY-02-28`
        So the function will return an empty list.
        And the day after:
        `today - relativedelta(years=18) = YYYY-03-01`
        `since - relativedelta(years=18) = YYYY-02-28`
        So users born on the 29th of February will be notified.
    """
    today = datetime.combine(datetime.today(), datetime.min.time())
    since = datetime.combine(since, datetime.min.time())
    eligible_users = (
        db.session.query(models.User)
        .outerjoin(offerers_models.UserOfferer)
        .filter(
            sa.not_(models.User.has_admin_role),  # not an admin
            offerers_models.UserOfferer.userId.is_(None),  # not a pro
            (models.User.birth_date <= today - relativedelta(years=age)),  # type: ignore[operator]
            (models.User.birth_date > since - relativedelta(years=age)),  # type: ignore[operator]
            models.User.dateCreated < today,
        )
        .all()
    )
    return eligible_users


def get_users_with_validated_attachment_by_offerer(offerer: offerers_models.Offerer) -> list[models.User]:
    return (
        db.session.query(models.User)
        .join(offerers_models.UserOfferer)
        .filter(
            offerers_models.UserOfferer.isValidated,
            offerers_models.UserOfferer.offererId == offerer.id,
        )
        .all()
    )


def get_users_with_validated_attachment(offerer: offerers_models.Offerer) -> list[models.User]:
    return (
        db.session.query(models.User)
        .join(offerers_models.UserOfferer)
        .filter_by(offererId=offerer.id, isValidated=True)
        .order_by(offerers_models.UserOfferer.id)
        .all()
    )


def get_and_lock_user(userId: int) -> models.User:
    user = (
        db.session.query(models.User)
        .filter(models.User.id == userId)
        .populate_existing()
        .with_for_update()
        .one_or_none()
    )
    return user


def get_single_sign_on(sso_provider: str, sso_user_id: str) -> models.SingleSignOn | None:
    return (
        db.session.query(models.SingleSignOn)
        .filter(
            models.SingleSignOn.ssoProvider == sso_provider,
            models.SingleSignOn.ssoUserId == sso_user_id,
        )
        .options(sa_orm.joinedload(models.SingleSignOn.user))
        .one_or_none()
    )


def create_single_sign_on(user: models.User, sso_provider: str, sso_user_id: str) -> models.SingleSignOn:
    return models.SingleSignOn(user=user, ssoProvider=sso_provider, ssoUserId=sso_user_id)


def fill_phone_number_on_all_users_offerer_without_any(offerer_id: int, phone_number: str) -> None:
    users_without_phone_number = (
        sa.select(models.User.id)
        .select_from(models.User)
        .where(sa.or_(models.User.phoneNumber == None, models.User.phoneNumber == ""))
        .join(
            offerers_models.UserOfferer,
            sa.and_(
                models.User.id == offerers_models.UserOfferer.userId,
                offerers_models.UserOfferer.offererId == offerer_id,
            ),
        )
    )
    db.session.query(models.User).where(models.User.id.in_(users_without_phone_number)).update(
        {"phoneNumber": phone_number}, synchronize_session=False
    )
    db.session.flush()
