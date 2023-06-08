from datetime import date
from datetime import datetime
import logging
import typing

from dateutil.relativedelta import relativedelta
from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
from sqlalchemy.sql.functions import func

import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.repository import repository
from pcapi.utils import crypto
import pcapi.utils.email as email_utils

from . import constants
from . import exceptions
from . import models


logger = logging.getLogger(__name__)


HASHED_PLACEHOLDER = crypto.hash_password("placeholder")


def check_user_and_credentials(user: models.User | None, password: str, allow_inactive: bool = False) -> None:
    # Order is important to prevent end-user to guess user emails
    # We need to check email and password before checking email validation
    if not user:
        # Hash the given password, just like we would do if the user
        # existed. This avoids user enumeration by comparing server
        # response time.
        crypto.check_password(password, HASHED_PLACEHOLDER)
        raise exceptions.InvalidIdentifier()
    if not (user.checkPassword(password) and (user.isActive or allow_inactive)):
        logger.info(
            "Failed authentication attempt",
            extra={"identifier": user.email, "user": user.id, "avoid_current_user": True, "success": False},
            technical_message_id="users.login",
        )
        raise exceptions.InvalidIdentifier()
    if not user.isValidated or not user.isEmailValidated:
        raise exceptions.UnvalidatedAccount()


def get_user_with_credentials(identifier: str, password: str, allow_inactive: bool = False) -> models.User:
    user = find_user_by_email(identifier)
    if not user:
        logger.info(
            "Failed authentication attempt",
            extra={"identifier": identifier, "user": "not found", "avoid_current_user": True, "success": False},
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
    # FIXME (dbaty, 2021-05-02): remove call to `func.lower()` once
    # all emails have been sanitized in the database.
    return models.User.query.filter(func.lower(models.User.email) == email_utils.sanitize_email(email))


def find_user_by_email(email: str) -> models.User | None:
    return _find_user_by_email_query(email).one_or_none()


def find_pro_user_by_email_query(email: str) -> BaseQuery:
    return _find_user_by_email_query(email).filter(models.User.has_pro_role.is_(True))  # type: ignore [attr-defined]


def get_user_with_valid_token(
    token_value: str, token_types: list[models.TokenType], use_token: bool = True
) -> models.User:
    token = models.Token.query.filter(
        models.Token.value == token_value,
        models.Token.type.in_(token_types),
        sa.not_(models.Token.isUsed),
    ).one_or_none()

    if not token:
        raise exceptions.InvalidToken()

    if token.expirationDate and token.expirationDate < datetime.utcnow():
        raise exceptions.ExpiredToken(user=token.user)

    if use_token:
        token.isUsed = True
        repository.save(token)

    return token.user


def get_newly_eligible_age_18_users(since: date) -> list[models.User]:
    """get users that are eligible between `since` (excluded) and now (included) and that have
    created their account before `since`"""
    today = datetime.combine(datetime.today(), datetime.min.time())
    since = datetime.combine(since, datetime.min.time())
    eligible_users = (
        models.User.query.outerjoin(offerers_models.UserOfferer)
        .filter(
            sa.not_(models.User.has_beneficiary_role),  # not already beneficiary
            sa.not_(models.User.has_admin_role),  # not an admin
            offerers_models.UserOfferer.userId.is_(None),  # not a pro
            # less than 19yo
            models.User.birth_date > today - relativedelta(years=(constants.ELIGIBILITY_AGE_18 + 1)),  # type: ignore [operator]
            # more than or 18yo
            models.User.birth_date <= today - relativedelta(years=constants.ELIGIBILITY_AGE_18),  # type: ignore [operator]
            # less than 18yo at since
            models.User.birth_date > since - relativedelta(years=constants.ELIGIBILITY_AGE_18),  # type: ignore [operator]
            models.User.dateCreated < today,
        )
        .all()
    )
    return eligible_users


def get_users_with_validated_attachment_by_offerer(offerer: offerers_models.Offerer) -> list[models.User]:
    return (
        models.User.query.join(offerers_models.UserOfferer)
        .filter(
            offerers_models.UserOfferer.isValidated,
            offerers_models.UserOfferer.offererId == offerer.id,
        )
        .all()
    )


def get_users_with_validated_attachment(offerer: offerers_models.Offerer) -> list[models.User]:
    return (
        models.User.query.join(offerers_models.UserOfferer)
        .filter_by(offererId=offerer.id, isValidated=True)
        .order_by(offerers_models.UserOfferer.id)
        .all()
    )


def get_and_lock_user(userId: int) -> models.User:
    user = models.User.query.filter(models.User.id == userId).populate_existing().with_for_update().one_or_none()
    return user


def get_emails_without_active_offers(since_date: date) -> list[tuple[str, bool, bool]]:
    """
    Returns emails whose last active offer expired since_date.
    The additional tuple fields are the properties of the last active offer needed for pro reminder mails.
    """
    offer_id_query = repository.db.session.query(offers_models.Stock.offerId.distinct()).filter(
        sa.cast(offers_models.Stock.dateModified, sa.Date) == since_date
    )
    offer_ids = [offer_id for offer_id, in offer_id_query]

    offer_with_stock_ranked_stmt_alias = (
        sa.select(
            offers_models.Offer.venueId,
            offers_models.Offer.canExpire,
            offers_models.Offer.isEvent,
            offers_models.Stock.dateModified,
            sa.func.row_number()
            .over(partition_by=offers_models.Offer.venueId, order_by=offers_models.Stock.dateModified.desc())
            .label("date_modification_rank"),
        )
        .join(offers_models.Offer.stocks.and_(offers_models.Stock.isSoftDeleted.is_(False)))
        .filter(offers_models.Offer.id.in_(offer_ids))
        .alias()
    )
    venues_with_stock_last_modified_at_date_stmt_alias = (
        sa.select(
            offer_with_stock_ranked_stmt_alias.c.venueId,
            offer_with_stock_ranked_stmt_alias.c.canExpire,
            offer_with_stock_ranked_stmt_alias.c.isEvent,
        )
        .filter(
            sa.cast(offer_with_stock_ranked_stmt_alias.c.dateModified, sa.Date) == since_date,
            offer_with_stock_ranked_stmt_alias.c.date_modification_rank == 1,
        )
        .alias()
    )

    has_active_offer_criterion = (
        offers_models.Offer.query.filter(
            offers_models.Offer.venueId == offerers_models.Venue.id,
            offers_models.Offer.isSoldOut.is_(False),  # type: ignore [attr-defined]
            offers_models.Offer.hasBookingLimitDatetimesPassed.is_(False),  # type: ignore [attr-defined]
        )
        .limit(1)
        .exists()
    )
    emails_without_active_offers_since_date_query = (
        repository.db.session.query(
            models.User.email,
            venues_with_stock_last_modified_at_date_stmt_alias.c.canExpire,
            venues_with_stock_last_modified_at_date_stmt_alias.c.isEvent,
        )
        .select_from(venues_with_stock_last_modified_at_date_stmt_alias)
        .join(
            offerers_models.Venue,
            venues_with_stock_last_modified_at_date_stmt_alias.c.venueId == offerers_models.Venue.id,
        )
        .join(offerers_models.Venue.managingOfferer)
        .join(offerers_models.Offerer.UserOfferers)
        .join(offerers_models.UserOfferer.user)
        .filter(has_active_offer_criterion.is_(False))
    )

    return emails_without_active_offers_since_date_query.all()
