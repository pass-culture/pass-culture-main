from dataclasses import asdict
import datetime
from decimal import Decimal
import enum
import logging
import re
import typing

from dateutil.relativedelta import relativedelta
from flask import current_app as app
from flask import request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.orm import Query

from pcapi import settings
from pcapi.connectors import api_adresse
from pcapi.connectors.beamer import BeamerException
from pcapi.connectors.beamer import delete_beamer_user
from pcapi.core import mails as mails_api
from pcapi.core import token as token_utils
import pcapi.core.bookings.models as bookings_models
import pcapi.core.bookings.repository as bookings_repository
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.external.sendinblue import update_contact_attributes
from pcapi.core.finance import models as finance_models
import pcapi.core.finance.api as finance_api
import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.common.models as common_fraud_models
from pcapi.core.geography.repository import get_iris_from_address
import pcapi.core.history.api as history_api
import pcapi.core.history.models as history_models
import pcapi.core.mails.transactional as transactional_mails
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.subscription.dms import api as dms_subscription_api
import pcapi.core.subscription.phone_validation.exceptions as phone_validation_exceptions
import pcapi.core.users.constants as users_constants
import pcapi.core.users.models as users_models
import pcapi.core.users.repository as users_repository
import pcapi.core.users.utils as users_utils
from pcapi.domain.password import check_password_strength
from pcapi.domain.password import random_password
from pcapi.models import db
from pcapi.models import feature
from pcapi.models.api_errors import ApiErrors
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.notifications import push as push_api
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.routes.serialization.users import ProUserCreationBodyV2Model
from pcapi.utils.clean_accents import clean_accents
import pcapi.utils.date as date_utils
import pcapi.utils.email as email_utils
import pcapi.utils.phone_number as phone_number_utils
import pcapi.utils.postal_code as postal_code_utils
from pcapi.utils.requests import ExternalAPIException

from . import constants
from . import exceptions
from . import models


if typing.TYPE_CHECKING:
    from pcapi.connectors import google_oauth
    from pcapi.routes.native.v1.serialization import account as account_serialization


class T_UNCHANGED(enum.Enum):
    TOKEN = 0


UNCHANGED = T_UNCHANGED.TOKEN


logger = logging.getLogger(__name__)


def create_reset_password_token(user: models.User, expiration: datetime.datetime | None = None) -> token_utils.Token:
    return token_utils.Token.create(
        token_utils.TokenType.RESET_PASSWORD,
        datetime.datetime.utcnow() - expiration if expiration else constants.RESET_PASSWORD_TOKEN_LIFE_TIME,
        user.id,
    )


def create_recently_reset_password_token(user: models.User) -> token_utils.Token:
    """Used to display a specific step during email change, in the mobile app"""
    return token_utils.Token.create(
        token_utils.TokenType.RECENTLY_RESET_PASSWORD,
        constants.RESET_PASSWORD_TOKEN_LIFE_TIME,
        user.id,
    )


def create_phone_validation_token(
    user: models.User,
    phone_number: str,
) -> token_utils.SixDigitsToken:
    return token_utils.SixDigitsToken.create(
        type_=token_utils.TokenType.PHONE_VALIDATION,
        user_id=user.id,
        ttl=constants.PHONE_VALIDATION_TOKEN_LIFE_TIME,
        data={"phone_number": phone_number},
    )


def delete_all_users_phone_validation_tokens(user: models.User) -> None:
    token_utils.Token.delete(token_utils.TokenType.PHONE_VALIDATION, user.id)


def create_account(
    email: str,
    password: str | None,
    birthdate: datetime.date,
    marketing_email_subscription: bool = False,
    is_email_validated: bool = False,
    send_activation_mail: bool = True,
    remote_updates: bool = True,
    phone_number: str | None = None,
    apps_flyer_user_id: str | None = None,
    apps_flyer_platform: str | None = None,
    firebase_pseudo_id: str | None = None,
    sso_provider: str | None = None,
    sso_user_id: str | None = None,
) -> models.User:
    email = email_utils.sanitize_email(email)
    if users_repository.find_user_by_email(email):
        raise exceptions.UserAlreadyExistsException()

    user = models.User(
        email=email,
        dateOfBirth=datetime.datetime.combine(birthdate, datetime.datetime.min.time()),
        isEmailValidated=is_email_validated,
        notificationSubscriptions=asdict(
            models.NotificationSubscriptions(marketing_email=marketing_email_subscription)
        ),
        phoneNumber=phone_number,
        lastConnectionDate=datetime.datetime.utcnow(),
    )

    if not user.age or user.age < constants.ACCOUNT_CREATION_MINIMUM_AGE:
        raise exceptions.UnderAgeUserException()

    setup_login(user, password, sso_provider, sso_user_id)

    if user.externalIds is None:
        user.externalIds = {}

    if apps_flyer_user_id and apps_flyer_platform:
        user.externalIds["apps_flyer"] = {"user": apps_flyer_user_id, "platform": apps_flyer_platform.upper()}

    if firebase_pseudo_id:
        user.externalIds["firebase_pseudo_id"] = firebase_pseudo_id

    repository.save(user)
    logger.info("Created user account", extra={"user": user.id})

    if remote_updates:
        external_attributes_api.update_external_user(user)

    if not user.isEmailValidated and send_activation_mail:
        request_email_confirmation(user)

    return user


def setup_login(
    user: models.User, password: str | None, sso_provider: str | None = None, sso_user_id: str | None = None
) -> None:
    if password:
        user.setPassword(password)
        return

    if not sso_provider or not sso_user_id:
        raise exceptions.MissingLoginMethod()

    single_sign_on = users_repository.create_single_sign_on(user, sso_provider, sso_user_id)
    db.session.add(single_sign_on)


def update_user_information(
    user: models.User,
    first_name: str | None = None,
    last_name: str | None = None,
    validated_birth_date: datetime.date | None = None,
    activity: str | None = None,
    address: str | None = None,
    city: str | None = None,
    civility: str | None = None,
    id_piece_number: str | None = None,
    ine_hash: str | None = None,
    married_name: str | None = None,
    postal_code: str | None = None,
    commit: bool = False,
) -> models.User:
    if first_name is not None:
        user.firstName = first_name
    if last_name is not None:
        user.lastName = last_name
    if validated_birth_date is not None:
        user.validatedBirthDate = validated_birth_date
    if activity is not None:
        user.activity = activity
    if address is not None:
        user.address = address
    if city is not None:
        user.city = city
    if civility is not None:
        user.civility = civility
    if id_piece_number is not None:
        if id_piece_number.strip() == "":
            user.idPieceNumber = None
        else:
            user.idPieceNumber = fraud_api.format_id_piece_number(id_piece_number)
    if ine_hash is not None:
        user.ineHash = ine_hash
    if married_name is not None:
        user.married_name = married_name
    if postal_code is not None:
        user.postalCode = postal_code
        user.departementCode = postal_code_utils.PostalCode(postal_code).get_departement_code() if postal_code else None

    user.remove_admin_role()

    db.session.add(user)
    db.session.flush()
    if commit:
        db.session.commit()
    return user


def update_user_information_from_external_source(
    user: models.User,
    data: common_fraud_models.IdentityCheckContent,
    commit: bool = False,
) -> models.User:
    first_name = data.get_first_name()
    last_name = data.get_last_name()
    birth_date = user.validatedBirthDate or data.get_birth_date()

    if not first_name or not last_name or not birth_date:
        raise exceptions.IncompleteDataException()

    return update_user_information(
        user=user,
        first_name=first_name,
        last_name=last_name,
        validated_birth_date=birth_date,
        activity=data.get_activity(),
        address=data.get_address(),
        city=data.get_city(),
        civility=data.get_civility(),
        id_piece_number=data.get_id_piece_number(),
        ine_hash=data.get_ine_hash(),
        married_name=data.get_married_name(),
        postal_code=data.get_postal_code(),
        commit=commit,
    )


def request_email_confirmation(user: models.User) -> None:
    token = token_utils.Token.create(
        token_utils.TokenType.EMAIL_VALIDATION,
        constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME,
        user.id,
    )
    transactional_mails.send_email_confirmation_email(user, token=token)


def _email_validation_resends_key(user: models.User) -> str:
    return f"email_validation_resends_user_{user.id}"


def get_remaining_email_validation_resends(user: models.User) -> int:
    email_validation_resends_count = app.redis_client.get(_email_validation_resends_key(user))

    if email_validation_resends_count:
        return max(settings.MAX_EMAIL_VALIDATION_RESENDS - int(email_validation_resends_count), 0)

    return settings.MAX_EMAIL_VALIDATION_RESENDS


def get_email_validation_resends_limitation_expiration_time(user: models.User) -> datetime.datetime | None:
    ttl = app.redis_client.ttl(_email_validation_resends_key(user))

    if ttl > 0:
        return datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl)

    return None


def check_email_validation_resends_count(user: models.User) -> None:
    """
    Check if the user has reached the maximum number of email validation resends.
    If yes, raise an exception.
    """
    email_validation_resends = app.redis_client.get(_email_validation_resends_key(user))

    if email_validation_resends and int(email_validation_resends) >= settings.MAX_EMAIL_VALIDATION_RESENDS:
        raise exceptions.EmailValidationLimitReached()


def increment_email_validation_resends_count(user: models.User) -> None:
    """
    Increment or initiate the number of resends of the email validation email
    """
    email_validation_resends_key = _email_validation_resends_key(user)
    email_validation_resends = app.redis_client.incr(email_validation_resends_key)

    if email_validation_resends == 1:
        # If the key did not exist, set the expiration time
        app.redis_client.expire(email_validation_resends_key, settings.EMAIL_VALIDATION_RESENDS_TTL)


def request_password_reset(user: models.User | None, reason: constants.SuspensionReason | None = None) -> None:
    if not user:
        return

    token = create_reset_password_token(user)
    transactional_mails.send_reset_password_email_to_user(token, reason)


def reset_password_with_token(new_password: str, encoded_reset_password_token: str) -> models.User:
    check_password_strength("newPassword", new_password)
    token = None
    try:
        token = token_utils.Token.load_and_check(encoded_reset_password_token, token_utils.TokenType.RESET_PASSWORD)
        user = models.User.query.get(token.user_id)
    except exceptions.InvalidToken:
        raise ApiErrors({"token": ["Le token de changement de mot de passe est invalide."]})

    user.setPassword(new_password)

    if not user.isEmailValidated:
        user.isEmailValidated = True
        try:
            dms_subscription_api.try_dms_orphan_adoption(user)
        except Exception:  # pylint: disable=broad-except
            logger.exception(
                "An unexpected error occurred while trying to link dms orphan to user", extra={"user_id": user.id}
            )
    if token:
        token.expire()
    return user


def handle_create_account_with_existing_email(user: models.User) -> None:
    if not user:
        return

    token = create_reset_password_token(user)
    transactional_mails.send_email_already_exists_email(token)


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
    user: models.User,
    reason: constants.SuspensionReason,
    actor: models.User | None,
    comment: str | None = None,
    is_backoffice_action: bool = False,
) -> dict[str, int]:
    """
    Suspend a user's account:
        * mark as inactive;
        * mark as suspended (suspension history);
        * remove its admin role if any;
        * cancel its bookings if needed;

    Notes:
        * `actor` can be None if and only if this function is called
        from an automated task (eg cron).
        * a user who suspends his account should be able to connect to
        the application in order to access to some restricted actions.
    """

    with transaction():
        user.isActive = False
        user.remove_admin_role()
        db.session.add(user)

        history_api.add_action(
            history_models.ActionType.USER_SUSPENDED, author=actor, user=user, reason=reason.value, comment=comment
        )

        for session in models.UserSession.query.filter_by(userId=user.id):
            db.session.delete(session)

        if user.backoffice_profile:
            user.backoffice_profile.roles = []

    if reason == constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER:
        update_user_password(user, random_password())

    n_bookings = _cancel_bookings_from_user_on_requested_account_suspension(user, reason)
    n_bookings += _cancel_bookings_of_user_on_requested_account_suspension(user, reason, is_backoffice_action)

    logger.info(
        "Account has been suspended",
        extra={
            "actor": actor.id if actor else None,
            "user": user.id,
            "reason": str(reason),
        },
    )

    _remove_external_user(user)

    return {"cancelled_bookings": n_bookings}


_USER_REQUESTED_REASONS = {
    constants.SuspensionReason.UPON_USER_REQUEST,
    constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER,
}

_AUTO_REQUESTED_REASONS = {
    constants.SuspensionReason.FRAUD_SUSPICION,
    constants.SuspensionReason.BLACKLISTED_DOMAIN_NAME,
}

_NON_BO_REASONS_WHICH_CANCEL_ALL_BOOKINGS = _USER_REQUESTED_REASONS | _AUTO_REQUESTED_REASONS

_BACKOFFICE_REASONS_WHICH_CANCEL_ALL_BOOKINGS = {
    constants.SuspensionReason.FRAUD_RESELL_PRODUCT,
    constants.SuspensionReason.FRAUD_RESELL_PASS,
}

_BACKOFFICE_REASONS_WHICH_CANCEL_NON_EVENTS = {
    constants.SuspensionReason.FRAUD_HACK,
    constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER,
    constants.SuspensionReason.UPON_USER_REQUEST,
}


def _cancel_bookings_of_user_on_requested_account_suspension(
    user: users_models.User,
    reason: constants.SuspensionReason,
    is_backoffice_action: bool,
) -> int:
    import pcapi.core.bookings.api as bookings_api

    bookings_query = bookings_models.Booking.query.filter(
        bookings_models.Booking.userId == user.id,
        bookings_models.Booking.status == bookings_models.BookingStatus.CONFIRMED,
    )

    if (is_backoffice_action and reason in _BACKOFFICE_REASONS_WHICH_CANCEL_ALL_BOOKINGS) or (
        not is_backoffice_action and reason in _NON_BO_REASONS_WHICH_CANCEL_ALL_BOOKINGS
    ):
        bookings_query = bookings_query.filter(
            sa.or_(
                datetime.datetime.utcnow() < bookings_models.Booking.cancellationLimitDate,
                bookings_models.Booking.cancellationLimitDate.is_(None),
            ),
        )
    elif is_backoffice_action and reason in _BACKOFFICE_REASONS_WHICH_CANCEL_NON_EVENTS:
        bookings_query = (
            bookings_query.join(bookings_models.Booking.stock)
            .join(offers_models.Stock.offer)
            .filter(sa.func.not_(offers_models.Offer.isEvent))
        )
    else:
        return 0

    cancelled_bookings_count = 0

    for booking in bookings_query.all():
        if not is_backoffice_action and reason in _USER_REQUESTED_REASONS:
            bookings_api.cancel_booking_on_user_requested_account_suspension(booking)
        else:
            bookings_api.cancel_booking_for_fraud(booking)
        cancelled_bookings_count += 1

    return cancelled_bookings_count


def _cancel_bookings_from_user_on_requested_account_suspension(
    user: users_models.User,
    reason: constants.SuspensionReason,
) -> int:
    import pcapi.core.bookings.api as bookings_api

    # Cancel all bookings of the related offerer if the suspended
    # account was the last active offerer's account.
    cancelled_bookings_count = 0
    if reason in (constants.SuspensionReason.FRAUD_SUSPICION, constants.SuspensionReason.BLACKLISTED_DOMAIN_NAME):
        for user_offerer in user.UserOfferers:
            offerer = user_offerer.offerer
            if any(user_of.user.isActive and user_of.user != user for user_of in offerer.UserOfferers):
                continue
            bookings = bookings_repository.find_cancellable_bookings_by_offerer(offerer.id)
            for booking in bookings:
                bookings_api.cancel_booking_for_fraud(booking)
                cancelled_bookings_count += 1

    return cancelled_bookings_count


def unsuspend_account(
    user: models.User, actor: models.User, comment: str | None = None, send_email: bool = False
) -> None:
    suspension_reason = user.suspension_reason
    user.isActive = True
    db.session.add(user)

    history_api.add_action(history_models.ActionType.USER_UNSUSPENDED, author=actor, user=user, comment=comment)

    db.session.commit()

    logger.info(
        "Account has been unsuspended",
        extra={
            "actor": actor.id,
            "user": user.id,
            "send_email": send_email,
        },
    )

    # external user was deleted when suspended, re-create it
    external_attributes_api.update_external_user(user)

    if send_email:
        transactional_mails.send_unsuspension_email(user)

    if suspension_reason == constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER:
        request_password_reset(user, constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER)


def change_email(
    current_user: models.User,
    new_email: str,
) -> None:
    email_history = models.UserEmailHistory.build_validation(user=current_user, new_email=new_email, by_admin=False)

    try:
        current_user.email = new_email
        repository.save(current_user, email_history)
    except ApiErrors as error:
        # The caller might not want to inform the end client that the
        # email address exists. To do so, raise a specific error and
        # let the caller handle this specific case as needed.
        # Note: email addresses are unique (db constraint)
        if "email" in error.errors:
            raise exceptions.EmailExistsError() from error
        raise

    models.UserSession.query.filter_by(userId=current_user.id).delete(synchronize_session=False)
    models.SingleSignOn.query.filter_by(userId=current_user.id).delete(synchronize_session=False)
    db.session.commit()

    logger.info("User has changed their email", extra={"user": current_user.id})


def change_pro_user_email(
    current_email: str,
    new_email: str,
    user_id: int,
) -> None:
    current_user = users_repository.find_user_by_email(current_email)
    if not current_user or current_user.id != user_id:
        raise exceptions.UserDoesNotExist()
    change_email(current_user, new_email)


def update_user_password(user: models.User, new_password: str) -> None:
    user.setPassword(new_password)
    repository.save(user)


def update_password_and_external_user(user: users_models.User, new_password: str) -> None:
    user.setPassword(new_password)
    if not user.isEmailValidated:
        user.isEmailValidated = True
        external_attributes_api.update_external_user(user)
    repository.save(user)


def update_user_info(
    user: users_models.User,
    author: users_models.User,
    cultural_survey_filled_date: datetime.datetime | T_UNCHANGED = UNCHANGED,
    email: str | T_UNCHANGED = UNCHANGED,
    first_name: str | T_UNCHANGED = UNCHANGED,
    last_name: str | T_UNCHANGED = UNCHANGED,
    needs_to_fill_cultural_survey: bool | T_UNCHANGED = UNCHANGED,
    phone_number: str | T_UNCHANGED = UNCHANGED,
    address: str | T_UNCHANGED = UNCHANGED,
    postal_code: str | T_UNCHANGED = UNCHANGED,
    city: str | T_UNCHANGED = UNCHANGED,
    validated_birth_date: datetime.date | T_UNCHANGED = UNCHANGED,
    id_piece_number: str | T_UNCHANGED = UNCHANGED,
    marketing_email_subscription: bool | T_UNCHANGED = UNCHANGED,
    new_nav_pro_date: datetime.datetime | None | T_UNCHANGED = UNCHANGED,
    new_nav_pro_eligibility_date: datetime.datetime | None | T_UNCHANGED = UNCHANGED,
    commit: bool = True,
) -> history_api.ObjectUpdateSnapshot:
    old_email = None
    snapshot = history_api.ObjectUpdateSnapshot(user, author)

    if cultural_survey_filled_date is not UNCHANGED:
        user.culturalSurveyFilledDate = cultural_survey_filled_date
    if email is not UNCHANGED:
        old_email = user.email
        user.email = email_utils.sanitize_email(email)
    if first_name is not UNCHANGED:
        if user.firstName != first_name:
            snapshot.set("firstName", old=user.firstName, new=first_name)
        user.firstName = first_name
    if last_name is not UNCHANGED:
        if user.lastName != last_name:
            snapshot.set("lastName", old=user.lastName, new=last_name)
        user.lastName = last_name
    if needs_to_fill_cultural_survey is not UNCHANGED:
        user.needsToFillCulturalSurvey = needs_to_fill_cultural_survey
    if phone_number is not UNCHANGED:
        user_phone_number = typing.cast(str, user.phoneNumber)
        if user_phone_number != phone_number:
            snapshot.set("phoneNumber", old=user_phone_number, new=phone_number)
        user.phoneNumber = phone_number  # type: ignore[method-assign]
    if address is not UNCHANGED:
        if address != user.address:
            snapshot.set("address", old=user.address, new=address)
        user.address = address
    if postal_code is not UNCHANGED:
        if user.postalCode != postal_code:
            snapshot.set("postalCode", old=user.postalCode, new=postal_code)
        user.postalCode = postal_code
        user.departementCode = postal_code_utils.PostalCode(postal_code).get_departement_code() if postal_code else None
    if city is not UNCHANGED:
        if city != user.city:
            snapshot.set("city", old=user.city, new=city)
        user.city = city
    if validated_birth_date is not UNCHANGED:
        if validated_birth_date != user.validatedBirthDate:
            snapshot.set("validatedBirthDate", old=user.validatedBirthDate, new=validated_birth_date)
            user.validatedBirthDate = validated_birth_date
            if _has_underage_deposit(user):
                _update_underage_beneficiary_deposit_expiration_date(user)
    if id_piece_number is not UNCHANGED:
        if id_piece_number != user.idPieceNumber:
            snapshot.set("idPieceNumber", old=user.idPieceNumber, new=id_piece_number)
        user.idPieceNumber = id_piece_number
    if marketing_email_subscription is not UNCHANGED:
        snapshot.trace_update(
            {"marketing_email": marketing_email_subscription},
            target=user.get_notification_subscriptions(),
            field_name_template="notificationSubscriptions.{}",
        )
        user.set_marketing_email_subscription(marketing_email_subscription)
    if (
        new_nav_pro_date is not UNCHANGED or new_nav_pro_eligibility_date is not UNCHANGED
    ) and feature.FeatureToggle.ENABLE_PRO_NEW_NAV_MODIFICATION.is_active():
        pro_new_nav_state = user.pro_new_nav_state
        if not pro_new_nav_state:
            pro_new_nav_state = models.UserProNewNavState(userId=user.id)
            user.pro_new_nav_state = pro_new_nav_state
        if new_nav_pro_date is not UNCHANGED:
            snapshot.set("pro_new_nav_state.newNavDate", old=pro_new_nav_state.newNavDate, new=new_nav_pro_date)
            pro_new_nav_state.newNavDate = new_nav_pro_date
        if new_nav_pro_eligibility_date is not UNCHANGED:
            snapshot.set(
                "pro_new_nav_state.eligibilityDate",
                old=pro_new_nav_state.eligibilityDate,
                new=new_nav_pro_eligibility_date,
            )
            pro_new_nav_state.eligibilityDate = new_nav_pro_eligibility_date
        db.session.add(pro_new_nav_state)

    # keep using repository as long as user is validated in pcapi.validation.models.user
    if commit:
        snapshot.add_action()
        repository.save(user)
    else:
        repository.add_to_session(user)

    # TODO(prouzet) even for young users, we should probably remove contact with former email from sendinblue lists
    if old_email and user.has_pro_role:
        external_attributes_api.update_external_pro(old_email)
    external_attributes_api.update_external_user(user)

    return snapshot


def _has_underage_deposit(user: users_models.User) -> bool:
    return user.deposit is not None and user.deposit.type == finance_models.DepositType.GRANT_15_17


def _update_underage_beneficiary_deposit_expiration_date(user: users_models.User) -> None:
    if user.birth_date is None:
        raise ValueError("User has no birth_date")
    if not (user.deposit and user.deposit.expirationDate):
        raise ValueError("Trying to update underage beneficiary deposit expiration date but user has no deposit")

    current_deposit_expiration_datetime = user.deposit.expirationDate
    new_deposit_expiration_datetime = finance_api.compute_underage_deposit_expiration_datetime(user.birth_date)

    if current_deposit_expiration_datetime == new_deposit_expiration_datetime:
        return

    logger.info(
        "Updating deposit expiration date for underage beneficiary %s",
        user.id,
        extra={
            "user": user.id,
            "deposit": user.deposit.id,
            "current_expiration_date": current_deposit_expiration_datetime,
            "new_expiration_date": new_deposit_expiration_datetime,
        },
    )

    if new_deposit_expiration_datetime > datetime.datetime.utcnow():
        user.deposit.expirationDate = new_deposit_expiration_datetime
    else:
        if current_deposit_expiration_datetime < datetime.datetime.utcnow():
            # no need to update the deposit expirationDate because it is already passed
            return
        # Else, reduce to now and not to the theoretical new date in case there are bookings made between these dates
        user.deposit.expirationDate = datetime.datetime.utcnow()

    repository.save(user.deposit)


def add_comment_to_user(user: models.User, author_user: models.User, comment: str) -> None:
    history_api.add_action(history_models.ActionType.COMMENT, author_user, user=user, comment=comment)
    db.session.commit()


def get_domains_credit(
    user: models.User, user_bookings: list[bookings_models.Booking] | None = None
) -> models.DomainsCredit | None:
    if not user.deposit:
        return None

    if user_bookings is None:
        deposit_bookings = bookings_repository.get_bookings_from_deposit(user.deposit.id)
    else:
        deposit_bookings = [
            booking
            for booking in user_bookings
            if booking.depositId == user.deposit.id and booking.status != bookings_models.BookingStatus.CANCELLED
        ]

    domains_credit = models.DomainsCredit(
        all=models.Credit(
            initial=user.deposit.amount,
            remaining=(
                max(user.deposit.amount - sum(booking.total_amount for booking in deposit_bookings), Decimal("0"))
                if user.has_active_deposit
                else Decimal("0")
            ),
        ),
    )
    specific_caps = user.deposit.specific_caps

    if specific_caps.DIGITAL_CAP:
        digital_bookings_total = sum(
            booking.total_amount
            for booking in deposit_bookings
            if specific_caps.digital_cap_applies(booking.stock.offer)
        )
        domains_credit.digital = models.Credit(
            initial=specific_caps.DIGITAL_CAP,
            remaining=(
                min(
                    max(specific_caps.DIGITAL_CAP - digital_bookings_total, Decimal("0")),
                    domains_credit.all.remaining,
                )
            ),
        )

    if specific_caps.PHYSICAL_CAP:
        physical_bookings_total = sum(
            booking.total_amount
            for booking in deposit_bookings
            if specific_caps.physical_cap_applies(booking.stock.offer)
        )
        domains_credit.physical = models.Credit(
            initial=specific_caps.PHYSICAL_CAP,
            remaining=(
                min(
                    max(specific_caps.PHYSICAL_CAP - physical_bookings_total, Decimal("0")),
                    domains_credit.all.remaining,
                )
            ),
        )

    return domains_credit


def create_pro_user_V2(pro_user: ProUserCreationBodyV2Model) -> models.User:
    new_pro_user = create_pro_user(pro_user)
    repository.add_to_session(new_pro_user)  # valide user with pcapi.validation.models.user
    history_api.add_action(history_models.ActionType.USER_CREATED, author=new_pro_user, user=new_pro_user)
    repository.save()  # keep commit with repository.save() to catch IntegrityError when email is duplicated

    token = token_utils.Token.create(
        token_utils.TokenType.EMAIL_VALIDATION,
        ttl=constants.EMAIL_VALIDATION_TOKEN_FOR_PRO_LIFE_TIME,
        user_id=new_pro_user.id,
    )

    transactional_mails.send_email_validation_to_pro_email(new_pro_user, token)

    external_attributes_api.update_external_pro(new_pro_user.email)
    return new_pro_user


def create_pro_user(pro_user: ProUserCreationBodyV2Model) -> models.User:
    user_kwargs = {
        k: v for k, v in pro_user.dict(by_alias=True).items() if k not in ("contactOk", "token", "_sa_instance_state")
    }
    password_arg = user_kwargs.pop("password")
    new_pro_user = models.User(**user_kwargs)
    new_pro_user.setPassword(password_arg)
    new_pro_user.email = email_utils.sanitize_email(new_pro_user.email)
    user_by_email = users_repository.find_user_by_email(new_pro_user.email)

    if user_by_email:
        raise exceptions.UserAlreadyExistsException()

    new_pro_user.notificationSubscriptions = asdict(
        models.NotificationSubscriptions(marketing_email=pro_user.contact_ok)
    )
    new_pro_user.add_non_attached_pro_role()
    new_pro_user.remove_admin_role()
    new_pro_user.remove_beneficiary_role()
    new_pro_user.needsToFillCulturalSurvey = False

    if hasattr(pro_user, "postal_code") and pro_user.postal_code:
        new_pro_user.departementCode = postal_code_utils.PostalCode(pro_user.postal_code).get_departement_code()

    if settings.MAKE_PROS_BENEFICIARIES_IN_APP:
        new_pro_user.add_beneficiary_role()
        eighteen_years_ago = datetime.datetime.utcnow() - datetime.timedelta(days=366 * 18)
        new_pro_user.dateOfBirth = eighteen_years_ago
        new_pro_user.validatedBirthDate = new_pro_user.dateOfBirth.date()
        deposit = finance_api.create_deposit(new_pro_user, "integration_signup", models.EligibilityType.AGE18)
        new_pro_user.deposits = [deposit]

    db.session.add(new_pro_user)
    db.session.flush()
    invitation = offerers_models.OffererInvitation.query.filter_by(email=new_pro_user.email).first()
    if invitation:
        inviter_pro_new_nav_state = users_models.UserProNewNavState.query.filter_by(
            userId=invitation.userId
        ).one_or_none()
        if inviter_pro_new_nav_state and inviter_pro_new_nav_state.newNavDate is not None:
            new_nav_pro = users_models.UserProNewNavState(
                userId=new_pro_user.id,
                newNavDate=datetime.datetime.utcnow(),
            )
            db.session.add(new_nav_pro)
    else:
        new_nav_pro = users_models.UserProNewNavState(
            userId=new_pro_user.id,
            newNavDate=datetime.datetime.utcnow(),
        )
        db.session.add(new_nav_pro)

    return new_pro_user


def set_pro_tuto_as_seen(user: models.User) -> None:
    user.hasSeenProTutorials = True
    repository.save(user)


def set_pro_rgs_as_seen(user: models.User) -> None:
    user.hasSeenProRgs = True
    repository.save(user)


def update_last_connection_date(user: models.User) -> None:
    previous_connection_date = user.lastConnectionDate
    last_connection_date = datetime.datetime.utcnow()

    should_save_last_connection_date = (
        not previous_connection_date or last_connection_date - previous_connection_date > datetime.timedelta(minutes=15)
    )
    should_update_sendinblue_last_connection_date = should_save_last_connection_date and (
        not previous_connection_date
        or last_connection_date.date() - previous_connection_date.date() >= datetime.timedelta(days=1)
    )

    if should_save_last_connection_date:
        user.lastConnectionDate = last_connection_date
        repository.save(user)

    if should_update_sendinblue_last_connection_date:
        external_attributes_api.update_external_user(user, skip_batch=True)


def create_user_access_token(user: models.User) -> str:
    return create_access_token(identity=user.email, additional_claims={"user_claims": {"user_id": user.id}})


def create_user_refresh_token(user: models.User, device_info: "account_serialization.TrustedDevice | None") -> str:
    should_extend_lifetime = (
        feature.FeatureToggle.WIP_ENABLE_TRUSTED_DEVICE.is_active()
        and feature.FeatureToggle.WIP_ENABLE_SUSPICIOUS_EMAIL_SEND.is_active()
        and is_login_device_a_trusted_device(device_info, user)
    )

    if should_extend_lifetime:
        duration = datetime.timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXTENDED_EXPIRES)
    else:
        duration = datetime.timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXPIRES)

    return create_refresh_token(identity=user.email, expires_delta=duration)


def create_oauth_state_token() -> str:
    token = token_utils.UUIDToken.create(
        token_utils.TokenType.OAUTH_STATE,
        users_constants.OAUTH_STATE_TOKEN_LIFE_TIME,
    )
    return token.encoded_token


def create_account_creation_token(google_user: "google_oauth.GoogleUser") -> str:
    token = token_utils.UUIDToken.create(
        token_utils.TokenType.ACCOUNT_CREATION,
        users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME,
        data=google_user.model_dump(),
    )
    return token.encoded_token


def update_notification_subscription(
    user: models.User, subscriptions: "account_serialization.NotificationSubscriptions | None"
) -> None:
    if subscriptions is None:
        return

    old_subscriptions = user.get_notification_subscriptions()
    history_api.ObjectUpdateSnapshot(user, user).trace_update(
        {"marketing_email": subscriptions.marketing_email, "marketing_push": subscriptions.marketing_push},
        target=old_subscriptions,
        field_name_template="notificationSubscriptions.{}",
    ).add_action()
    user.notificationSubscriptions = {
        "marketing_push": subscriptions.marketing_push,
        "marketing_email": subscriptions.marketing_email,
        "subscribed_themes": subscriptions.subscribed_themes,
    }

    logger.info(
        "Notification subscription update",
        extra={
            "analyticsSource": "app-native",
            "newlySubscribedTo": {
                "email": subscriptions.marketing_email and not old_subscriptions.marketing_email,
                "push": subscriptions.marketing_push and not old_subscriptions.marketing_push,
                "themes": set(subscriptions.subscribed_themes) - set(old_subscriptions.subscribed_themes),
            },
            "newlyUnsubscribedFrom": {
                "email": not subscriptions.marketing_email and old_subscriptions.marketing_email,
                "push": not subscriptions.marketing_push and old_subscriptions.marketing_push,
                "themes": set(old_subscriptions.subscribed_themes) - set(subscriptions.subscribed_themes),
            },
            "subscriptions": user.notificationSubscriptions,
        },
        technical_message_id="subscription_update",
    )

    repository.save(user)


def reset_recredit_amount_to_show(user: models.User) -> None:
    user.recreditAmountToShow = None
    repository.save(user)


def get_eligibility_end_datetime(
    date_of_birth: datetime.date | datetime.datetime | None,
) -> datetime.datetime | None:
    if not date_of_birth:
        return None

    return datetime.datetime.combine(date_of_birth, datetime.time(0, 0)) + relativedelta(
        years=constants.ELIGIBILITY_AGE_18 + 1, hour=11
    )


def get_eligibility_start_datetime(
    date_of_birth: datetime.date | datetime.datetime | None,
) -> datetime.datetime | None:
    if not date_of_birth:
        return None

    date_of_birth = datetime.datetime.combine(date_of_birth, datetime.time(0, 0))
    fifteenth_birthday = date_of_birth + relativedelta(years=constants.ELIGIBILITY_UNDERAGE_RANGE[0])

    return fifteenth_birthday


def get_eligibility_at_date(
    date_of_birth: datetime.date | None,
    specified_datetime: datetime.datetime,
) -> models.EligibilityType | None:
    eligibility_start = get_eligibility_start_datetime(date_of_birth)
    eligibility_end = get_eligibility_end_datetime(date_of_birth)

    if not date_of_birth or not (eligibility_start <= specified_datetime < eligibility_end):  # type: ignore[operator]
        return None

    age = users_utils.get_age_at_date(date_of_birth, specified_datetime)
    if not age:
        return None

    if age in constants.ELIGIBILITY_UNDERAGE_RANGE:
        return models.EligibilityType.UNDERAGE
    # If the user is older than 18 in UTC timezone, we consider them eligible until they reach eligibility_end
    if constants.ELIGIBILITY_AGE_18 <= age and specified_datetime < eligibility_end:  # type: ignore[operator]
        return models.EligibilityType.AGE18

    return None


def is_eligible_for_beneficiary_upgrade(user: models.User, eligibility: models.EligibilityType | None) -> bool:
    return (eligibility == models.EligibilityType.UNDERAGE and not user.is_beneficiary) or (
        eligibility == models.EligibilityType.AGE18 and not user.has_beneficiary_role
    )


def is_user_age_compatible_with_eligibility(user_age: int | None, eligibility: models.EligibilityType | None) -> bool:
    if eligibility == models.EligibilityType.UNDERAGE:
        return user_age in constants.ELIGIBILITY_UNDERAGE_RANGE
    if eligibility == models.EligibilityType.AGE18:
        return user_age is not None and user_age >= constants.ELIGIBILITY_AGE_18
    return False


def _filter_user_accounts(accounts: BaseQuery, search_term: str) -> BaseQuery:
    filters = []
    name_term = None

    if not search_term:
        return accounts.filter(False)

    term_filters: list[sa.sql.ColumnElement] = []

    # phone number
    try:
        parsed_phone_number = phone_number_utils.parse_phone_number(search_term)
        term_as_phone_number = phone_number_utils.get_formatted_phone_number(parsed_phone_number)
    except phone_validation_exceptions.InvalidPhoneNumber:
        pass  # term can't be a phone number
    else:
        term_filters.append(models.User.phoneNumber == term_as_phone_number)  # type: ignore[arg-type]

    # numeric (single id or multiple ids)
    split_terms = re.split(r"[,;\s]+", search_term)
    if all(term.isnumeric() for term in split_terms):
        term_filters.append(models.User.id.in_([int(term) for term in split_terms]))

    # email
    sanitized_term = email_utils.sanitize_email(search_term)

    if email_utils.is_valid_email(sanitized_term):
        term_filters.append(models.User.email == sanitized_term)
    elif email_utils.is_valid_email_domain(sanitized_term):
        # search for all emails @domain.ext
        term_filters.append(models.User.email.like(f"%{sanitized_term}"))

    if not term_filters:
        name_term = search_term
        for name in name_term.split():
            term_filters.append(
                sa.func.immutable_unaccent(models.User.firstName + " " + models.User.lastName).ilike(
                    f"%{clean_accents(name)}%"
                )
            )
        filters.append(sa.and_(*term_filters) if len(term_filters) > 1 else term_filters[0])

    else:
        filters.append(sa.or_(*term_filters) if len(term_filters) > 1 else term_filters[0])

    # each result must match all terms in any column
    accounts = accounts.filter(*filters)

    if name_term:
        name_term = name_term.lower()
        accounts = accounts.order_by(
            sa.func.levenshtein(sa.func.lower(models.User.firstName + " " + models.User.lastName), name_term)
        )

    accounts = accounts.order_by(models.User.id)

    return accounts


def search_public_account(search_query: str) -> BaseQuery:
    public_accounts = get_public_account_base_query()

    return _filter_user_accounts(public_accounts, search_query)


def search_public_account_in_history_email(search_query: str) -> BaseQuery:
    sanitized_term = email_utils.sanitize_email(search_query)
    if not email_utils.is_valid_email(sanitized_term):
        raise ValueError(f"Unsupported email search on invalid email: {search_query}")

    accounts = get_public_account_base_query()

    if not search_query:
        return accounts.filter(False)

    # including old emails: look for validated email updates inside user_email_history
    return (
        accounts.join(models.UserEmailHistory)
        .filter(
            models.UserEmailHistory.oldEmail == sanitized_term,
            models.UserEmailHistory.eventType.in_(
                {
                    models.EmailHistoryEventTypeEnum.VALIDATION,
                    models.EmailHistoryEventTypeEnum.ADMIN_VALIDATION,
                    models.EmailHistoryEventTypeEnum.ADMIN_UPDATE,
                }
            ),
        )
        .order_by(models.User.id)
    )


def get_public_account_base_query() -> BaseQuery:
    # There is no fully reliable condition to be sure that a user account is used as a public account (vs only pro).
    # In Flask-Admin backoffice, the difference was made from user_offerer table, which turns the user into a "pro"
    # account ; the same filter is kept here.
    # However, some young users, including beneficiaries, work for organizations and are associated with offerers
    # using the same email as their personal account. So let's include "pro" users who are beneficiaries (doesn't
    # include those who are only in the subscription process).
    public_accounts = models.User.query.outerjoin(users_models.User.backoffice_profile).filter(
        sa.or_(  # type: ignore[type-var]
            sa.and_(
                sa.not_(models.User.has_pro_role),
                sa.not_(models.User.has_non_attached_pro_role),
                perm_models.BackOfficeUserProfile.id.is_(None),
            ),
            models.User.is_beneficiary,
        ),
    )
    return public_accounts


# TODO (prouzet, 2023-11-02) This function should be moved in backoffice and use common _join_suspension_history()
def search_pro_account(search_query: str, *_: typing.Any) -> BaseQuery:
    pro_accounts = models.User.query.filter(
        sa.or_(  # type: ignore[type-var]
            models.User.has_non_attached_pro_role,
            models.User.has_pro_role,
        )
    )

    return _filter_user_accounts(pro_accounts, search_query).options(
        sa.orm.with_expression(users_models.User.suspension_reason_expression, users_models.User.suspension_reason.expression),  # type: ignore[attr-defined]
        sa.orm.with_expression(users_models.User.suspension_date_expression, users_models.User.suspension_date.expression),  # type: ignore[attr-defined]
        sa.orm.joinedload(users_models.User.UserOfferers).load_only(offerers_models.UserOfferer.validationStatus),
    )


def get_pro_account_base_query(pro_id: int) -> BaseQuery:
    return models.User.query.filter(
        models.User.id == pro_id,
        sa.or_(  # type: ignore[type-var]
            models.User.has_non_attached_pro_role,
            models.User.has_pro_role,
        ),
    )


def search_backoffice_accounts(search_query: str) -> BaseQuery:
    bo_accounts = models.User.query.join(users_models.User.backoffice_profile).options(
        sa.orm.with_expression(users_models.User.suspension_reason_expression, users_models.User.suspension_reason.expression),  # type: ignore[attr-defined]
        sa.orm.with_expression(users_models.User.suspension_date_expression, users_models.User.suspension_date.expression),  # type: ignore[attr-defined]
    )

    if not search_query:
        return bo_accounts

    return _filter_user_accounts(bo_accounts, search_query)


def validate_pro_user_email(user: users_models.User, author_user: users_models.User | None = None) -> None:
    user.isEmailValidated = True

    if author_user:
        history_api.add_action(history_models.ActionType.USER_EMAIL_VALIDATED, author=author_user, user=user)

    repository.save(user)

    # FIXME: accept_offerer_invitation_if_exists also add() and commit()... in a loop!
    offerers_api.accept_offerer_invitation_if_exists(user)


def save_firebase_flags(user: models.User, firebase_value: dict) -> None:
    user_pro_flags = users_models.UserProFlags.query.filter(users_models.UserProFlags.user == user).one_or_none()
    if user_pro_flags:
        if user.pro_flags.firebase and user.pro_flags.firebase != firebase_value:
            logger.warning("%s now has different Firebase flags than before", user)
        user.pro_flags.firebase = firebase_value
    else:
        user_pro_flags = users_models.UserProFlags(user=user, firebase=firebase_value)
    repository.save(user_pro_flags)


def save_flags(user: models.User, flags: dict) -> None:
    for flag, value in flags.items():
        match flag:
            case "firebase":
                save_firebase_flags(user, value)
            case _:
                raise ValueError()


def save_trusted_device(device_info: "account_serialization.TrustedDevice", user: models.User) -> None:
    if not device_info.device_id:
        logger.info(
            "Invalid deviceId was provided for trusted device",
            extra={
                "deviceId": device_info.device_id,
                "os": device_info.os,
                "source": device_info.source,
            },
        )
        return

    trusted_device = users_models.TrustedDevice(
        deviceId=device_info.device_id,
        os=device_info.os,
        source=device_info.source,
        user=user,
    )
    repository.save(trusted_device)


def update_login_device_history(
    device_info: "account_serialization.TrustedDevice", user: models.User
) -> users_models.LoginDeviceHistory | None:
    if not device_info.device_id:
        logger.info(
            "Invalid deviceId was provided for login device",
            extra={
                "deviceId": device_info.device_id,
                "os": device_info.os,
                "source": device_info.source,
            },
        )
        return None

    location = users_utils.format_login_location(request.headers.get("X-Country"), request.headers.get("X-City"))

    login_device = users_models.LoginDeviceHistory(
        deviceId=device_info.device_id,
        os=device_info.os,
        source=device_info.source,
        user=user,
        location=location,
    )
    repository.save(login_device)

    return login_device


def should_save_login_device_as_trusted_device(
    device_info: "account_serialization.TrustedDevice", user: models.User
) -> bool:
    if not device_info.device_id:
        return False

    if any(device.deviceId == device_info.device_id for device in user.trusted_devices):
        return False

    return db.session.query(
        users_models.LoginDeviceHistory.query.with_entities(users_models.LoginDeviceHistory.deviceId)
        .filter(users_models.LoginDeviceHistory.userId == user.id)
        .filter(users_models.LoginDeviceHistory.deviceId == device_info.device_id)
        .exists()
    ).scalar()


def is_login_device_a_trusted_device(
    device_info: "account_serialization.TrustedDevice | None", user: models.User
) -> bool:
    if device_info is None or not device_info.device_id:
        return False

    if any(device.deviceId == device_info.device_id for device in user.trusted_devices):
        return True

    return False


def get_recent_suspicious_logins(user: users_models.User) -> list[users_models.LoginDeviceHistory]:
    yesterday = datetime.datetime.utcnow() - relativedelta(hours=24)
    recent_logins = users_models.LoginDeviceHistory.query.filter(
        users_models.LoginDeviceHistory.user == user,
        users_models.LoginDeviceHistory.dateCreated >= yesterday,
    ).all()
    recent_trusted_devices = users_models.TrustedDevice.query.filter(
        users_models.TrustedDevice.dateCreated >= yesterday,
    ).all()
    user_trusted_device_ids = [device.deviceId for device in user.trusted_devices]

    recent_suspicious_logins = []
    for recent_login in recent_logins:
        if recent_login.deviceId not in user_trusted_device_ids:
            recent_suspicious_logins.append(recent_login)
            continue

        was_device_trusted_after_suspicious_login = any(
            trusted_device.deviceId == recent_login.deviceId and trusted_device.dateCreated > recent_login.dateCreated
            for trusted_device in recent_trusted_devices
        )
        if was_device_trusted_after_suspicious_login:
            recent_suspicious_logins.append(recent_login)

    return recent_suspicious_logins


def create_suspicious_login_email_token(
    login_info: users_models.LoginDeviceHistory | None, user_id: int
) -> token_utils.Token:
    if login_info is None:
        return token_utils.Token.create(
            token_utils.TokenType.SUSPENSION_SUSPICIOUS_LOGIN,
            users_constants.SUSPICIOUS_LOGIN_EMAIL_TOKEN_LIFE_TIME,
            user_id,
            {"dateCreated": datetime.datetime.utcnow().strftime(date_utils.DATE_ISO_FORMAT)},
        )

    passed_ttl = datetime.datetime.utcnow() - login_info.dateCreated
    remaining_ttl = users_constants.SUSPICIOUS_LOGIN_EMAIL_TOKEN_LIFE_TIME - passed_ttl

    return token_utils.Token.create(
        token_utils.TokenType.SUSPENSION_SUSPICIOUS_LOGIN,
        remaining_ttl,
        user_id,
        {
            "dateCreated": login_info.dateCreated.strftime(date_utils.DATE_ISO_FORMAT),
            "location": login_info.location,
            "os": login_info.os,
            "source": login_info.source,
        },
    )


def save_device_info_and_notify_user(
    user: models.User, device_info: "account_serialization.TrustedDevice | None"
) -> None:
    login_history = None
    if device_info is not None:
        if should_save_login_device_as_trusted_device(device_info, user):
            save_trusted_device(device_info, user)

        login_history = update_login_device_history(device_info, user)

    should_send_suspicious_login_email = (
        (user.is_active or user.is_account_suspended_upon_user_request)
        and not is_login_device_a_trusted_device(device_info, user)
        and feature.FeatureToggle.WIP_ENABLE_SUSPICIOUS_EMAIL_SEND.is_active()
        and len(get_recent_suspicious_logins(user)) <= constants.MAX_SUSPICIOUS_LOGIN_EMAILS
    )

    if should_send_suspicious_login_email:
        account_suspension_token = create_suspicious_login_email_token(login_history, user.id)
        reset_password_token = create_reset_password_token(user)
        transactional_mails.send_suspicious_login_email(
            user, login_history, account_suspension_token, reset_password_token
        )


def delete_old_trusted_devices() -> None:
    five_years_ago = datetime.datetime.utcnow() - relativedelta(years=5)

    users_models.TrustedDevice.query.filter(users_models.TrustedDevice.dateCreated <= five_years_ago).delete()
    db.session.commit()


def delete_old_login_device_history() -> None:
    thirteen_months_ago = datetime.datetime.utcnow() - relativedelta(months=13)

    users_models.LoginDeviceHistory.query.filter(
        users_models.LoginDeviceHistory.dateCreated <= thirteen_months_ago
    ).delete()
    db.session.commit()


def _get_users_with_suspended_account() -> Query:
    # distinct keeps the first row if duplicates are found. Since rows
    # are ordered by userId and eventDate, this query will fetch the
    # latest event for each userId.
    return (
        users_models.User.query.distinct(history_models.ActionHistory.userId)
        .join(users_models.User.action_history)
        .filter(
            history_models.ActionHistory.actionType == history_models.ActionType.USER_SUSPENDED,
            users_models.User.isActive.is_(False),
        )
        .order_by(history_models.ActionHistory.userId, history_models.ActionHistory.actionDate.desc())
    )


def _get_users_with_suspended_account_to_notify(expiration_delta_in_days: int) -> Query:
    start = datetime.date.today() - datetime.timedelta(days=expiration_delta_in_days)
    user_ids_and_latest_action = (
        _get_users_with_suspended_account()
        .with_entities(
            users_models.User.id,
            history_models.ActionHistory.actionDate,
            history_models.ActionHistory.extraData["reason"].astext.label("reason"),
        )
        .subquery()
    )
    return (
        users_models.User.query.join(
            user_ids_and_latest_action, user_ids_and_latest_action.c.id == users_models.User.id
        )
        .filter(
            user_ids_and_latest_action.c.actionDate - start >= datetime.timedelta(days=0),
            user_ids_and_latest_action.c.actionDate - start < datetime.timedelta(days=1),
            user_ids_and_latest_action.c.reason == constants.SuspensionReason.UPON_USER_REQUEST.value,
        )
        .with_entities(users_models.User)
    )


def get_suspended_upon_user_request_accounts_since(expiration_delta_in_days: int) -> Query:
    start = datetime.date.today() - datetime.timedelta(days=expiration_delta_in_days)
    user_ids_and_latest_action = (
        _get_users_with_suspended_account()
        .with_entities(
            users_models.User.id,
            history_models.ActionHistory.actionDate,
            history_models.ActionHistory.extraData["reason"].astext.label("reason"),
        )
        .subquery()
    )
    return (
        users_models.User.query.join(
            user_ids_and_latest_action, user_ids_and_latest_action.c.id == users_models.User.id
        )
        .filter(
            user_ids_and_latest_action.c.actionDate <= start,
            user_ids_and_latest_action.c.reason == constants.SuspensionReason.UPON_USER_REQUEST.value,
        )
        .with_entities(users_models.User)
    )


def notify_users_before_deletion_of_suspended_account() -> None:
    expiration_delta_in_days = settings.DELETE_SUSPENDED_ACCOUNTS_SINCE - settings.NOTIFY_X_DAYS_BEFORE_DELETION
    accounts_to_notify = _get_users_with_suspended_account_to_notify(expiration_delta_in_days)
    for account in accounts_to_notify:
        transactional_mails.send_email_before_deletion_of_suspended_account(account)


def anonymize_user(user: users_models.User, *, author: users_models.User | None = None, force: bool = False) -> bool:
    """
    Anonymize the given User. If force is True, the function will anonymize the user even if they have an address and
    we cannot find an iris for it.
    """
    iris = None
    if user.address:
        try:
            iris = get_iris_from_address(address=user.address, postcode=user.postalCode)
        except (api_adresse.AdresseApiException, api_adresse.InvalidFormatException) as exc:
            logger.exception("Could not anonymize user", extra={"user_id": user.id, "exc": str(exc)})
            return False

        if not iris and not force:
            return False

    try:
        push_api.delete_user_attributes(user_id=user.id, can_be_asynchronously_retried=True)
    except ExternalAPIException as exc:
        # If is_retryable it is a real error. If this flag is False then it means the email is unknown for brevo.
        if exc.is_retryable:
            logger.exception("Could not anonymize user", extra={"user_id": user.id, "exc": str(exc)})
            return False
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.exception("Could not anonymize user", extra={"user_id": user.id, "exc": str(exc)})
        return False

    for beneficiary_fraud_check in user.beneficiaryFraudChecks:
        beneficiary_fraud_check.resultContent = None
        beneficiary_fraud_check.reason = "Anonymized"
        beneficiary_fraud_check.dateCreated = beneficiary_fraud_check.dateCreated.replace(day=1, month=1)

    for beneficiary_fraud_review in user.beneficiaryFraudReviews:
        beneficiary_fraud_review.reason = "Anonymized"
        beneficiary_fraud_review.dateReviewed = beneficiary_fraud_review.dateReviewed.replace(day=1, month=1)

    for deposit in user.deposits:
        deposit.source = "Anonymized"

    user.password = b"Anonymized"
    user.firstName = f"Anonymous_{user.id}"
    user.lastName = f"Anonymous_{user.id}"
    user.married_name = None
    user.postalCode = None
    user.phoneNumber = None  # type: ignore[method-assign]
    user.dateOfBirth = user.dateOfBirth.replace(day=1, month=1) if user.dateOfBirth else None
    user.address = None
    user.city = None
    user.externalIds = []
    user.idPieceNumber = None
    user.user_email_history = []
    user.irisFrance = iris
    user.validatedBirthDate = user.validatedBirthDate.replace(day=1, month=1) if user.validatedBirthDate else None

    external_email_anonymized = _remove_external_user(user)

    users_models.TrustedDevice.query.filter(users_models.TrustedDevice.userId == user.id).delete()
    users_models.LoginDeviceHistory.query.filter(users_models.LoginDeviceHistory.userId == user.id).delete()
    history_models.ActionHistory.query.filter(
        history_models.ActionHistory.userId == user.id,
        history_models.ActionHistory.offererId.is_(None),
    ).delete()

    if external_email_anonymized:
        user.replace_roles_by_anonymized_role()
        user.email = f"anonymous_{user.id}@anonymized.passculture"
        db.session.add(
            history_models.ActionHistory(
                actionType=history_models.ActionType.USER_ANONYMIZED,
                authorUser=author,
                userId=user.id,
            )
        )
    return True


def _remove_external_user(user: users_models.User) -> bool:
    # check if this email is used in booking_email (it should not be)
    is_email_used = (
        db.session.query(offerers_models.Venue.id)
        .filter(offerers_models.Venue.bookingEmail == user.email)
        .limit(1)
        .count()
    )

    # clean personal data on email partner's side
    try:
        if is_email_used:
            attributes = external_attributes_api.get_anonymized_attributes(user)
            update_contact_attributes(user.email, attributes, asynchronous=False)
        else:
            mails_api.delete_contact(user.email)
    except ExternalAPIException as exc:
        # If is_retryable it is a real error. If this flag is False then it means the email is unknown for brevo.
        if exc.is_retryable:
            logger.exception("Could not delete external user", extra={"user_id": user.id, "exc": str(exc)})
            return False
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.exception("Could not delete external user", extra={"user_id": user.id, "exc": str(exc)})
        return False

    return True


def anonymize_non_pro_non_beneficiary_users(*, force: bool = False) -> None:
    """
    Anonymize user accounts that have never been beneficiary (no deposits), are not pro (no pro role) and which have
    not connected for at least 3 years.
    """
    users = (
        users_models.User.query.outerjoin(
            finance_models.Deposit,
            users_models.User.deposits,
        )
        .filter(
            ~users_models.User.email.like("%@passculture.app"),  # people who work or worked in the company
            func.array_length(users_models.User.roles, 1).is_(None),  # no role, not already anonymized
            finance_models.Deposit.userId.is_(None),  # no deposit
            users_models.User.lastConnectionDate < datetime.datetime.utcnow() - relativedelta(years=3),
        )
        .all()
    )
    for user in users:
        anonymize_user(user, force=force)
    db.session.commit()


def anonymize_beneficiary_users(*, force: bool = False) -> None:
    """
    Anonymize user accounts that have been beneficiaries which have not connected for at least 3 years, and
    whose deposit has been expired for at least 5 years.
    """
    users = (
        users_models.User.query.outerjoin(
            finance_models.Deposit,
            users_models.User.deposits,
        )
        .filter(
            users_models.User.is_beneficiary,
            users_models.User.lastConnectionDate < datetime.datetime.utcnow() - relativedelta(years=3),
            finance_models.Deposit.expirationDate < datetime.datetime.utcnow() - relativedelta(years=5),
        )
        .all()
    )
    for user in users:
        anonymize_user(user, force=force)
    db.session.commit()


def anonymize_pro_users() -> None:
    """
    Anonymize pro accounts which have not connected for at least 3 years and are either:
    - not validated on an offerer
    - validated on an offerer but at least one user would remain on this offerer
    """
    three_years_ago = datetime.datetime.utcnow() - datetime.timedelta(days=365 * 3)

    exclude_non_pro_filters = [
        ~users_models.User.roles.contains([users_models.UserRole.ADMIN]),
        ~users_models.User.roles.contains([users_models.UserRole.ANONYMIZED]),
        ~users_models.User.roles.contains([users_models.UserRole.BENEFICIARY]),
        ~users_models.User.roles.contains([users_models.UserRole.UNDERAGE_BENEFICIARY]),
    ]

    aliased_offerer = sa.orm.aliased(offerers_models.Offerer)
    aliased_user_offerer = sa.orm.aliased(offerers_models.UserOfferer)
    aliased_user = sa.orm.aliased(users_models.User)

    offerers = (
        db.session.query(aliased_offerer.id)
        .join(aliased_user_offerer, aliased_offerer.UserOfferers)
        .join(aliased_user, aliased_user_offerer.user)
        .filter(
            aliased_user.lastConnectionDate >= three_years_ago,
            aliased_user_offerer.validationStatus == ValidationStatus.VALIDATED,
            aliased_offerer.id == offerers_models.Offerer.id,
        )
    )
    validated_users = (
        db.session.query(users_models.User.id)
        .join(offerers_models.UserOfferer, users_models.User.UserOfferers)
        .join(offerers_models.Offerer, offerers_models.UserOfferer.offerer)
        .filter(
            offerers_models.UserOfferer.validationStatus == ValidationStatus.VALIDATED,
            offerers_models.Offerer.isActive,
            users_models.User.lastConnectionDate < three_years_ago,
            *exclude_non_pro_filters,
            offerers.exists(),
        )
    )

    non_validated_users = (
        db.session.query(users_models.User.id)
        .join(offerers_models.UserOfferer, users_models.User.UserOfferers)
        .filter(
            offerers_models.UserOfferer.validationStatus != ValidationStatus.VALIDATED,
            users_models.User.lastConnectionDate < three_years_ago,
            users_models.User.roles.contains([users_models.UserRole.PRO]),
            *exclude_non_pro_filters,
        )
    )
    non_attached_users = db.session.query(users_models.User.id).filter(
        users_models.User.lastConnectionDate < three_years_ago,
        users_models.User.roles.contains([users_models.UserRole.NON_ATTACHED_PRO]),
        *exclude_non_pro_filters,
    )
    never_connected_users = db.session.query(users_models.User.id).filter(
        users_models.User.lastConnectionDate.is_(None),
        users_models.User.dateCreated < three_years_ago,
        sa.or_(
            users_models.User.roles.contains([users_models.UserRole.PRO]),
            users_models.User.roles.contains([users_models.UserRole.NON_ATTACHED_PRO]),
        ),
        *exclude_non_pro_filters,
    )

    users = users_models.User.query.filter(
        users_models.User.id.in_(
            sa.union(validated_users, non_validated_users, non_attached_users, never_connected_users).subquery(),
        ),
    )
    for user in users:
        gdpr_delete_pro_user(user)

    db.session.commit()


def gdpr_delete_pro_user(user: users_models.User) -> None:
    try:
        delete_beamer_user(user.id)
    except BeamerException:
        pass
    _remove_external_user(user)

    history_models.ActionHistory.query.filter(
        history_models.ActionHistory.userId != user.id,
        history_models.ActionHistory.authorUserId == user.id,
    ).update(
        {
            "authorUserId": None,
        },
        synchronize_session=False,
    )
    offerers_models.UserOfferer.query.filter(offerers_models.UserOfferer.userId == user.id).delete(
        synchronize_session=False,
    )
    users_models.User.query.filter(users_models.User.id == user.id).delete(synchronize_session=False)


def anonymize_user_deposits() -> None:
    """
    Anonymize deposits that have been expired for at least 10 years.
    """
    deposits_query = finance_models.Deposit.query.filter(
        finance_models.Deposit.expirationDate < datetime.datetime.utcnow() - relativedelta(years=10),
        ~sa.and_(  # ignore already anonymized deposits
            sa.func.extract("month", finance_models.Deposit.expirationDate) == 1,
            sa.func.extract("day", finance_models.Deposit.expirationDate) == 1,
            sa.func.extract("month", finance_models.Deposit.dateCreated) == 1,
            sa.func.extract("day", finance_models.Deposit.dateCreated) == 1,
        ),
    )
    deposits_query.update(
        {
            "expirationDate": sa.func.date_trunc("year", finance_models.Deposit.expirationDate),
            "dateCreated": sa.func.date_trunc("year", finance_models.Deposit.dateCreated),
        },
        synchronize_session=False,
    )

    db.session.commit()


def enable_new_pro_nav(user: models.User) -> None:
    pro_new_nav_state = models.UserProNewNavState.query.filter(
        models.UserProNewNavState.userId == user.id
    ).one_or_none()

    if not pro_new_nav_state or not pro_new_nav_state.eligibilityDate:
        raise exceptions.ProUserNotEligibleForNewNav()

    if pro_new_nav_state.eligibilityDate > datetime.datetime.utcnow():
        raise exceptions.ProUserNotYetEligibleForNewNav()

    if pro_new_nav_state.newNavDate:
        return

    pro_new_nav_state.newNavDate = datetime.datetime.utcnow()
    db.session.add(pro_new_nav_state)
    db.session.commit()
