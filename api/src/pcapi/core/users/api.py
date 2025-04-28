from dataclasses import asdict
import datetime
from decimal import Decimal
import enum
from io import BytesIO
import itertools
import logging
from pathlib import Path
import random
import re
import typing
import zipfile

from dateutil.relativedelta import relativedelta
from flask import current_app as app
from flask import render_template
from flask import request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
from sqlalchemy import func
import sqlalchemy.orm as sa_orm

from pcapi import settings
from pcapi.connectors import api_adresse
from pcapi.connectors.beamer import BeamerException
from pcapi.connectors.beamer import delete_beamer_user
from pcapi.connectors.dms import exceptions as dms_exceptions
from pcapi.core import mails as mails_api
from pcapi.core import object_storage
from pcapi.core import token as token_utils
import pcapi.core.bookings.models as bookings_models
import pcapi.core.bookings.repository as bookings_repository
from pcapi.core.chronicles import constants as chronicles_constants
from pcapi.core.chronicles import models as chronicles_models
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.external.sendinblue import update_contact_attributes
from pcapi.core.finance import models as finance_models
import pcapi.core.finance.api as finance_api
from pcapi.core.fraud import models as fraud_models
import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.common.models as common_fraud_models
from pcapi.core.geography.repository import get_iris_from_address
import pcapi.core.history.api as history_api
from pcapi.core.history.api import add_action
import pcapi.core.history.models as history_models
from pcapi.core.mails import get_raw_contact_data
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.object_storage import store_public_object
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.subscription.dms import api as dms_subscription_api
import pcapi.core.subscription.phone_validation.exceptions as phone_validation_exceptions
import pcapi.core.users.constants as users_constants
import pcapi.core.users.ds as users_ds
import pcapi.core.users.repository as users_repository
import pcapi.core.users.utils as users_utils
from pcapi.domain.password import check_password_strength
from pcapi.domain.password import random_password
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.notifications import push as push_api
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.repository.session_management import is_managed_transaction
from pcapi.routes.serialization import users as users_serialization
from pcapi.utils import phone_number as phone_number_utils
from pcapi.utils.clean_accents import clean_accents
import pcapi.utils.date as date_utils
import pcapi.utils.email as email_utils
from pcapi.utils.pdf import generate_pdf_from_html
import pcapi.utils.postal_code as postal_code_utils
from pcapi.utils.requests import ExternalAPIException

from . import constants
from . import exceptions
from . import models


if typing.TYPE_CHECKING:
    from pcapi.connectors import google_oauth
    from pcapi.routes.native.v1.serialization import account as account_serialization


class ExtractBeneficiaryDataCounter:
    """
    Counter to coordinate the limitation of extraction performed every day.
    If reset is called it will reset the counter between 0:00 and 0:10
    """

    def __init__(self, key: str, max_value: int):
        self.key = key
        self.max_value = max_value

    def reset(self) -> None:
        now = datetime.datetime.utcnow()
        if now.hour == 0 and now.minute < 10:
            app.redis_client.delete(self.key)

    def get(self) -> int:
        raw_counter = app.redis_client.get(self.key)
        counter = int(raw_counter) if raw_counter else 0
        return counter

    def is_full(self) -> bool:
        return self.get() >= self.max_value

    def __iadd__(self, other: int) -> None:
        app.redis_client.incrby(self.key, other)


class T_UNCHANGED(enum.Enum):
    TOKEN = 0


UNCHANGED = T_UNCHANGED.TOKEN

EMAIL_CONFIRMATION_TEST_EMAIL_PATTERN = "+e2e@"


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
    *,
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
    db.session.add(user)

    if not user.age or user.age < constants.ACCOUNT_CREATION_MINIMUM_AGE:
        raise exceptions.UnderAgeUserException()

    setup_login(user, password, sso_provider, sso_user_id)

    if user.externalIds is None:
        user.externalIds = {}

    if apps_flyer_user_id and apps_flyer_platform:
        user.externalIds["apps_flyer"] = {"user": apps_flyer_user_id, "platform": apps_flyer_platform.upper()}

    if firebase_pseudo_id:
        user.externalIds["firebase_pseudo_id"] = firebase_pseudo_id

    db.session.flush()
    if remote_updates:
        external_attributes_api.update_external_user(user)

    if send_activation_mail and not user.isEmailValidated:
        if _bypass_email_confirmation(user.email):
            user.isEmailValidated = True
        else:
            request_email_confirmation(user)

    logger.info("Created user account", extra={"user": user.id})

    return user


def _bypass_email_confirmation(email: str) -> bool:
    return settings.ENABLE_EMAIL_CONFIRMATION_BYPASS and EMAIL_CONFIRMATION_TEST_EMAIL_PATTERN in email


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


def _update_user_information(
    user: models.User,
    *,
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

    return user


def update_user_information_from_external_source(
    user: models.User,
    data: common_fraud_models.IdentityCheckContent,
) -> models.User:
    first_name = data.get_first_name()
    last_name = data.get_last_name()
    birth_date = user.validatedBirthDate or data.get_birth_date()

    if not first_name or not last_name or not birth_date:
        raise exceptions.IncompleteDataException()

    return _update_user_information(
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
    )


def request_email_confirmation(user: models.User) -> None:
    token = token_utils.Token.create(
        token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION,
        constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME,
        user.id,
    )
    transactional_mails.send_email_confirmation_email(user.email, token=token)


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
        user = db.session.query(models.User).get(token.user_id)
    except exceptions.InvalidToken:
        raise ApiErrors({"token": ["Le token de changement de mot de passe est invalide."]})

    user.setPassword(new_password)

    if not user.isEmailValidated:
        user.isEmailValidated = True
        try:
            dms_subscription_api.try_dms_orphan_adoption(user)
        except Exception:
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
    *,
    reason: constants.SuspensionReason,
    actor: models.User | None,
    comment: str | None = None,
    action_extra_data: dict | None = None,
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
            history_models.ActionType.USER_SUSPENDED,
            author=actor,
            user=user,
            reason=reason.value,
            comment=comment,
            **(action_extra_data or {}),
        )

        for session in db.session.query(models.UserSession).filter_by(userId=user.id):
            db.session.delete(session)

        if user.backoffice_profile:
            user.backoffice_profile.roles = []

    if reason == constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER:
        update_user_password(user, random_password())

    n_bookings = _cancel_bookings_of_user_on_requested_account_suspension(user, reason, is_backoffice_action)

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
    constants.SuspensionReason.WAITING_FOR_ANONYMIZATION,
}

_AUTO_REQUESTED_REASONS = {
    constants.SuspensionReason.BLACKLISTED_DOMAIN_NAME,
}

_NON_BO_REASONS_WHICH_CANCEL_ALL_BOOKINGS = _USER_REQUESTED_REASONS | _AUTO_REQUESTED_REASONS

_BACKOFFICE_REASONS_WHICH_CANCEL_ALL_BOOKINGS = {
    constants.SuspensionReason.FRAUD_RESELL_PRODUCT,
    constants.SuspensionReason.FRAUD_RESELL_PASS,
}

_BACKOFFICE_REASONS_WHICH_CANCEL_NON_EVENTS = {
    constants.SuspensionReason.FRAUD_SUSPICION,
    constants.SuspensionReason.FRAUD_USURPATION,
    constants.SuspensionReason.FRAUD_HACK,
    constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER,
    constants.SuspensionReason.UPON_USER_REQUEST,
    constants.SuspensionReason.WAITING_FOR_ANONYMIZATION,
}


def _cancel_bookings_of_user_on_requested_account_suspension(
    user: models.User,
    reason: constants.SuspensionReason,
    is_backoffice_action: bool,
) -> int:
    import pcapi.core.bookings.api as bookings_api

    bookings_query = db.session.query(bookings_models.Booking).filter(
        bookings_models.Booking.userId == user.id,
        bookings_models.Booking.status == bookings_models.BookingStatus.CONFIRMED,
    )

    if reason in _BACKOFFICE_REASONS_WHICH_CANCEL_ALL_BOOKINGS | _NON_BO_REASONS_WHICH_CANCEL_ALL_BOOKINGS:
        bookings_query = bookings_query.filter(
            sa.or_(
                datetime.datetime.utcnow() < bookings_models.Booking.cancellationLimitDate,
                bookings_models.Booking.cancellationLimitDate.is_(None),
            ),
        )
    elif reason in _BACKOFFICE_REASONS_WHICH_CANCEL_NON_EVENTS:
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
            bookings_api.cancel_booking_for_fraud(booking, reason)
        cancelled_bookings_count += 1

    return cancelled_bookings_count


def unsuspend_account(
    user: models.User, actor: models.User, comment: str | None = None, send_email: bool = False
) -> None:
    suspension_reason = user.suspension_reason
    user.isActive = True
    db.session.add(user)
    db.session.query(models.GdprUserAnonymization).filter(models.GdprUserAnonymization.userId == user.id).delete()

    history_api.add_action(history_models.ActionType.USER_UNSUSPENDED, author=actor, user=user, comment=comment)

    db.session.flush()
    if not is_managed_transaction():
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

    db.session.query(models.UserSession).filter_by(userId=current_user.id).delete(synchronize_session=False)
    db.session.query(models.SingleSignOn).filter_by(userId=current_user.id).delete(synchronize_session=False)
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


def update_password_and_external_user(user: models.User, new_password: str) -> None:
    user.setPassword(new_password)
    if not user.isEmailValidated:
        user.isEmailValidated = True
        external_attributes_api.update_external_user(user)
    repository.save(user)


def update_user_info(
    user: models.User,
    *,
    author: models.User,
    cultural_survey_filled_date: datetime.datetime | T_UNCHANGED = UNCHANGED,
    email: str | T_UNCHANGED = UNCHANGED,
    first_name: str | T_UNCHANGED = UNCHANGED,
    last_name: str | T_UNCHANGED = UNCHANGED,
    needs_to_fill_cultural_survey: bool | T_UNCHANGED = UNCHANGED,
    phone_number: str | None | T_UNCHANGED = UNCHANGED,
    phone_validation_status: models.PhoneValidationStatusType | None | T_UNCHANGED = UNCHANGED,
    address: str | T_UNCHANGED = UNCHANGED,
    postal_code: str | T_UNCHANGED = UNCHANGED,
    city: str | T_UNCHANGED = UNCHANGED,
    validated_birth_date: datetime.date | T_UNCHANGED = UNCHANGED,
    id_piece_number: str | T_UNCHANGED = UNCHANGED,
    marketing_email_subscription: bool | T_UNCHANGED = UNCHANGED,
    activity: models.ActivityEnum | T_UNCHANGED = UNCHANGED,
    commit: bool = True,
) -> history_api.ObjectUpdateSnapshot:
    old_email = None
    snapshot = history_api.ObjectUpdateSnapshot(user, author)
    batch_extra_data = {}

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
    if phone_validation_status is not UNCHANGED:
        if user.phoneValidationStatus != phone_validation_status:
            snapshot.set("phoneValidationStatus", old=user.phoneValidationStatus, new=phone_validation_status)
        user.phoneValidationStatus = phone_validation_status
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
            if _has_underage_deposit(user) and not FeatureToggle.WIP_ENABLE_CREDIT_V3.is_active():
                _update_underage_beneficiary_deposit_expiration_date(user)
            if (
                FeatureToggle.WIP_ENABLE_CREDIT_V3.is_active()
                and user.deposit
                and user.has_active_deposit
                and validated_birth_date is not None
            ):
                twenty_first_birthday = validated_birth_date + relativedelta(years=21)
                user.deposit.expirationDate = datetime.datetime.combine(twenty_first_birthday, datetime.time.min)

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
    if activity is not UNCHANGED:
        if user.activity != activity.value:
            snapshot.set("activity", old=user.activity, new=activity.value)
            batch_extra_data["last_status_update_date"] = datetime.datetime.utcnow()
        user.activity = activity.value

    # keep using repository as long as user is validated in pcapi.validation.models.user
    if commit:
        snapshot.add_action()
        repository.save(user)
    else:
        repository.add_to_session(user)

    # TODO(prouzet) even for young users, we should probably remove contact with former email from sendinblue lists
    if old_email and user.has_pro_role:
        external_attributes_api.update_external_pro(old_email)
    external_attributes_api.update_external_user(user, batch_extra_data=batch_extra_data)

    return snapshot


def _has_underage_deposit(user: models.User) -> bool:
    return user.deposit is not None and user.deposit.type == finance_models.DepositType.GRANT_15_17


def _update_underage_beneficiary_deposit_expiration_date(user: models.User) -> None:
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
    history_api.add_action(
        action_type=history_models.ActionType.COMMENT,
        author=author_user,
        user=user,
        comment=comment,
    )
    db.session.flush()


def _get_booking_credit(booking: bookings_models.Booking) -> Decimal:
    # Get only partial incidents
    for booking_finance_incident in booking.incidents:
        if booking_finance_incident.is_partial:
            if booking_finance_incident.incident.status == finance_models.IncidentStatus.VALIDATED:
                return Decimal(booking_finance_incident.newTotalAmount) / Decimal("100")
    return booking.total_amount


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
                max(
                    user.deposit.amount - sum(_get_booking_credit(booking) for booking in deposit_bookings),
                    Decimal("0"),
                )
                if user.has_active_deposit
                else Decimal("0")
            ),
        ),
    )
    specific_caps = user.deposit.specific_caps

    if specific_caps.DIGITAL_CAP:
        digital_bookings_total = sum(
            _get_booking_credit(booking)
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
            _get_booking_credit(booking)
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


def create_and_send_signup_email_confirmation(new_pro_user: models.User) -> None:
    if FeatureToggle.WIP_2025_SIGN_UP.is_active():
        token = token_utils.create_passwordless_login_token(
            user_id=new_pro_user.id, ttl=constants.PASSWORDLESS_TOKEN_LIFE_TIME
        )
        logger.info("Login Token: %s/inscription/validation/%s", settings.PRO_URL, token)
    else:
        token = token_utils.Token.create(
            token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION,
            ttl=constants.EMAIL_VALIDATION_TOKEN_FOR_PRO_LIFE_TIME,
            user_id=new_pro_user.id,
        ).encoded_token

    transactional_mails.send_signup_email_confirmation_to_pro(new_pro_user, token)

    external_attributes_api.update_external_pro(new_pro_user.email)


def create_pro_user(pro_user: users_serialization.ProUserCreationBodyV2Model) -> models.User:
    if not FeatureToggle.WIP_2025_SIGN_UP.is_active() and pro_user.phone_number is None:
        raise phone_validation_exceptions.RequiredPhoneNumber()

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

    history_api.add_action(history_models.ActionType.USER_CREATED, author=new_pro_user, user=new_pro_user)

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
    if is_login_device_a_trusted_device(device_info, user):
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
    user: models.User, subscriptions: "account_serialization.NotificationSubscriptions | None", origin: str | None
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
    db.session.flush()

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
            "origin": origin,
        },
        technical_message_id="subscription_update",
    )


def reset_recredit_amount_to_show(user: models.User) -> None:
    user.recreditAmountToShow = None
    repository.save(user)


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

    split_terms = [email_utils.sanitize_email(term) for term in re.split(r"[,;\s]+", search_term) if term]

    # numeric (single id or multiple ids)
    if all(term.isnumeric() for term in split_terms):
        term_filters.append(models.User.id.in_([int(term) for term in split_terms]))

    # email
    if all(email_utils.is_valid_email(term) for term in split_terms):
        term_filters.append(models.User.email.in_(split_terms))
    elif len(split_terms) == 1 and email_utils.is_valid_email_domain(split_terms[0]):
        # search for all emails @domain.ext
        term_filters.append(sa.func.email_domain(models.User.email) == split_terms[0][1:])

    if not term_filters:
        split_term = search_term.split()
        if len(split_term) > 1 and all(len(item) <= 3 for item in split_term):
            # When terms only contain 3 letters or less, search for the exact full name to avoid timeout.
            # This enables to find users with very short names (e.g. "Lou Na") using the trigram index on full name.
            filters.append(
                sa.func.immutable_unaccent(models.User.firstName + " " + models.User.lastName).ilike(
                    f"{clean_accents(search_term)}"
                )
            )
        else:
            name_term = search_term
            for name in split_term:
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
                    models.EmailHistoryEventTypeEnum.NEW_EMAIL_SELECTION,
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
    public_accounts = (
        db.session.query(models.User)
        .outerjoin(models.User.backoffice_profile)
        .filter(
            sa.or_(  # type: ignore[type-var]
                sa.and_(
                    sa.not_(models.User.has_pro_role),
                    sa.not_(models.User.has_non_attached_pro_role),
                    perm_models.BackOfficeUserProfile.id.is_(None),
                ),
                models.User.is_beneficiary,
            ),
        )
    )
    return public_accounts


# TODO (prouzet, 2023-11-02) This function should be moved in backoffice and use common _join_suspension_history()
def search_pro_account(search_query: str, *_: typing.Any) -> BaseQuery:
    pro_accounts = (
        db.session.query(models.User)
        .filter(
            sa.or_(  # type: ignore[type-var]
                models.User.has_non_attached_pro_role,
                models.User.has_pro_role,
            )
        )
        .outerjoin(
            finance_models.Deposit,
            # load only the last deposit to avoid breaking line count
            sa.and_(
                models.User.id == finance_models.Deposit.userId,
                finance_models.Deposit.expirationDate > datetime.datetime.utcnow(),
            ),
        )
    )

    return _filter_user_accounts(pro_accounts, search_query).options(
        sa_orm.with_expression(models.User.suspension_reason_expression, models.User.suspension_reason.expression),  # type: ignore[attr-defined]
        sa_orm.with_expression(models.User.suspension_date_expression, models.User.suspension_date.expression),  # type: ignore[attr-defined]
        sa_orm.joinedload(models.User.UserOfferers).load_only(offerers_models.UserOfferer.validationStatus),
        sa_orm.contains_eager(models.User.deposits),
    )


def get_pro_account_base_query(pro_id: int) -> BaseQuery:
    return db.session.query(models.User).filter(
        models.User.id == pro_id,
        sa.or_(  # type: ignore[type-var]
            models.User.has_non_attached_pro_role,
            models.User.has_pro_role,
        ),
    )


def search_backoffice_accounts(search_query: str) -> BaseQuery:
    bo_accounts = (
        db.session.query(models.User)
        .join(models.User.backoffice_profile)
        .options(
            sa_orm.with_expression(models.User.suspension_reason_expression, models.User.suspension_reason.expression),  # type: ignore[attr-defined]
            sa_orm.with_expression(models.User.suspension_date_expression, models.User.suspension_date.expression),  # type: ignore[attr-defined]
        )
    )

    if not search_query:
        return bo_accounts

    return _filter_user_accounts(bo_accounts, search_query)


def validate_pro_user_email(user: models.User, author_user: models.User | None = None) -> None:
    user.isEmailValidated = True

    if author_user:
        history_api.add_action(history_models.ActionType.USER_EMAIL_VALIDATED, author=author_user, user=user)

    repository.save(user)

    # FIXME: accept_offerer_invitation_if_exists also add() and commit()... in a loop!
    offerers_api.accept_offerer_invitation_if_exists(user)


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

    trusted_device = models.TrustedDevice(
        deviceId=device_info.device_id,
        os=device_info.os,
        source=device_info.source,
        user=user,
    )
    repository.save(trusted_device)


def update_login_device_history(
    device_info: "account_serialization.TrustedDevice", user: models.User
) -> models.LoginDeviceHistory | None:
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

    login_device = models.LoginDeviceHistory(
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
        db.session.query(models.LoginDeviceHistory)
        .with_entities(models.LoginDeviceHistory.deviceId)
        .filter(models.LoginDeviceHistory.userId == user.id)
        .filter(models.LoginDeviceHistory.deviceId == device_info.device_id)
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


def get_recent_suspicious_logins(user: models.User) -> list[models.LoginDeviceHistory]:
    yesterday = datetime.datetime.utcnow() - relativedelta(hours=24)
    recent_logins = (
        db.session.query(models.LoginDeviceHistory)
        .filter(
            models.LoginDeviceHistory.user == user,
            models.LoginDeviceHistory.dateCreated >= yesterday,
        )
        .all()
    )
    recent_trusted_devices = (
        db.session.query(models.TrustedDevice)
        .filter(
            models.TrustedDevice.dateCreated >= yesterday,
        )
        .all()
    )
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
    login_info: models.LoginDeviceHistory | None, user_id: int
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

    db.session.query(models.TrustedDevice).filter(models.TrustedDevice.dateCreated <= five_years_ago).delete()
    db.session.commit()


def delete_old_login_device_history() -> None:
    thirteen_months_ago = datetime.datetime.utcnow() - relativedelta(months=13)

    db.session.query(models.LoginDeviceHistory).filter(
        models.LoginDeviceHistory.dateCreated <= thirteen_months_ago
    ).delete()
    db.session.commit()


def _get_users_with_suspended_account() -> sa_orm.Query:
    # distinct keeps the first row if duplicates are found. Since rows
    # are ordered by userId and eventDate, this query will fetch the
    # latest event for each userId.
    return (
        db.session.query(models.User)
        .distinct(history_models.ActionHistory.userId)
        .join(models.User.action_history)
        .filter(
            history_models.ActionHistory.actionType == history_models.ActionType.USER_SUSPENDED,
            models.User.isActive.is_(False),
        )
        .order_by(history_models.ActionHistory.userId, history_models.ActionHistory.actionDate.desc())
    )


def _get_users_with_suspended_account_to_notify(expiration_delta_in_days: int) -> sa_orm.Query:
    start = datetime.date.today() - datetime.timedelta(days=expiration_delta_in_days)
    user_ids_and_latest_action = (
        _get_users_with_suspended_account()
        .with_entities(
            models.User.id,
            history_models.ActionHistory.actionDate,
            history_models.ActionHistory.extraData["reason"].astext.label("reason"),
        )
        .subquery()
    )
    return (
        db.session.query(models.User)
        .join(user_ids_and_latest_action, user_ids_and_latest_action.c.id == models.User.id)
        .filter(
            user_ids_and_latest_action.c.actionDate - start >= datetime.timedelta(days=0),
            user_ids_and_latest_action.c.actionDate - start < datetime.timedelta(days=1),
            user_ids_and_latest_action.c.reason == constants.SuspensionReason.UPON_USER_REQUEST.value,
        )
        .with_entities(models.User)
    )


def get_suspended_upon_user_request_accounts_since(expiration_delta_in_days: int) -> sa_orm.Query:
    start = datetime.date.today() - datetime.timedelta(days=expiration_delta_in_days)
    user_ids_and_latest_action = (
        _get_users_with_suspended_account()
        .with_entities(
            models.User.id,
            history_models.ActionHistory.actionDate,
            history_models.ActionHistory.extraData["reason"].astext.label("reason"),
        )
        .subquery()
    )
    return (
        db.session.query(models.User)
        .join(user_ids_and_latest_action, user_ids_and_latest_action.c.id == models.User.id)
        .filter(
            user_ids_and_latest_action.c.actionDate <= start,
            user_ids_and_latest_action.c.reason == constants.SuspensionReason.UPON_USER_REQUEST.value,
        )
        .with_entities(models.User)
    )


def notify_users_before_deletion_of_suspended_account() -> None:
    expiration_delta_in_days = settings.DELETE_SUSPENDED_ACCOUNTS_SINCE - settings.NOTIFY_X_DAYS_BEFORE_DELETION
    accounts_to_notify = _get_users_with_suspended_account_to_notify(expiration_delta_in_days)
    for account in accounts_to_notify:
        transactional_mails.send_email_before_deletion_of_suspended_account(account)


def has_unprocessed_extract(user: models.User) -> bool:
    for extract in user.gdprUserDataExtract:
        if not extract.is_expired and not extract.dateProcessed:
            return True
    return False


def is_suspended_for_less_than_five_years(user: models.User) -> bool:
    if user.suspension_reason in constants.FRAUD_SUSPENSION_REASONS:
        return user.suspension_date > datetime.datetime.utcnow() - relativedelta(years=5)
    return False


def anonymize_user(user: models.User, *, author: models.User | None = None, force: bool = False) -> bool:
    """
    Anonymize the given User. If force is True, the function will anonymize the user even if they have an address and
    we cannot find an iris for it.
    """
    if has_unprocessed_extract(user):
        return False

    iris = None
    if user.address:
        try:
            iris = get_iris_from_address(address=user.address, postcode=user.postalCode)
        except (api_adresse.AdresseApiException, api_adresse.InvalidFormatException) as exc:
            logger.error("Could not anonymize user", extra={"user_id": user.id, "exc": str(exc)})
            return False

        if not iris and not force:
            return False

    try:
        push_api.delete_user_attributes(user_id=user.id, can_be_asynchronously_retried=True)
    except ExternalAPIException as exc:
        # If is_retryable it is a real error. If this flag is False then it means the email is unknown for brevo.
        if exc.is_retryable:
            logger.error("Could not anonymize user", extra={"user_id": user.id, "exc": str(exc)})
            return False
    except Exception as exc:
        logger.error("Could not anonymize user", extra={"user_id": user.id, "exc": str(exc)})
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

    for extract in user.gdprUserDataExtract:
        delete_gdpr_extract(extract.id)

    db.session.query(models.GdprUserAnonymization).filter(models.GdprUserAnonymization.userId == user.id).delete()
    db.session.query(chronicles_models.Chronicle).filter(chronicles_models.Chronicle.userId == user.id).update(
        {
            "userId": None,
            "email": chronicles_constants.ANONYMIZED_EMAIL,
        },
        synchronize_session=False,
    )

    for update_request in (
        db.session.query(models.UserAccountUpdateRequest)
        .filter(models.UserAccountUpdateRequest.userId == user.id)
        .all()
    ):
        # UserAccountUpdateRequest objects are deleted after being archived in DS
        try:
            users_ds.archive(update_request, motivation="Anonymisation du compte")
        except dms_exceptions.DmsGraphQLApiError as dms_api_error:
            # Ignore not found: the application is already deleted or on staging after dump/restore with fake id
            if not dms_api_error.is_not_found:
                raise

    user.password = b"Anonymized"  # ggignore
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

    db.session.query(models.TrustedDevice).filter(models.TrustedDevice.userId == user.id).delete()
    db.session.query(models.LoginDeviceHistory).filter(models.LoginDeviceHistory.userId == user.id).delete()
    db.session.query(history_models.ActionHistory).filter(
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


def _remove_external_user(user: models.User) -> bool:
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
            mails_api.delete_contact(user.email, user.has_any_pro_role)
    except ExternalAPIException as exc:
        # If is_retryable it is a real error. If this flag is False then it means the email is unknown for brevo.
        if exc.is_retryable:
            logger.exception("Could not delete external user", extra={"user_id": user.id, "exc": str(exc)})
            return False
    except Exception as exc:
        logger.exception("Could not delete external user", extra={"user_id": user.id, "exc": str(exc)})
        return False

    return True


def anonymize_non_pro_non_beneficiary_users(*, force: bool = False) -> None:
    """
    Anonymize user accounts that have never been beneficiary (no deposits), are not pro (no pro
    role) and which have not connected for at least 3 years and if they have been suspended it was
    at least 5 years ago.
    """
    users = (
        db.session.query(models.User)
        .outerjoin(
            finance_models.Deposit,
            models.User.deposits,
        )
        .filter(
            sa.func.email_domain(models.User.email) != "passculture.app",  # people who work or worked in the company
            func.array_length(models.User.roles, 1).is_(None),  # no role, not already anonymized
            finance_models.Deposit.userId.is_(None),  # no deposit
            models.User.lastConnectionDate < datetime.datetime.utcnow() - relativedelta(years=3),
            sa.or_(
                models.User.suspension_reason.is_(None),  # type: ignore [attr-defined]
                ~models.User.suspension_reason.in_(constants.FRAUD_SUSPENSION_REASONS),  # type: ignore [attr-defined]
                sa.and_(
                    models.User.suspension_reason.in_(constants.FRAUD_SUSPENSION_REASONS),  # type: ignore [attr-defined]
                    models.User.suspension_date < datetime.datetime.utcnow() - relativedelta(years=5),  # type: ignore [operator]
                ),
            ),
        )
    )
    for user in users:
        anonymize_user(user, force=force)
    db.session.commit()


def is_beneficiary_anonymizable(user: models.User) -> bool:
    if not is_only_beneficiary(user):
        return False

    # Check if the user never had credits.
    if len(user.deposits) == 0:
        return True

    # Check if the user is over 21.
    if (
        user.validatedBirthDate
        and users_utils.get_age_at_date(user.validatedBirthDate, datetime.datetime.utcnow()) >= 21
    ):
        return True
    return False


def is_only_beneficiary(user: models.User) -> bool:
    # Check if the user is admin, pro or anonymised
    beneficiary_roles = {models.UserRole.BENEFICIARY, models.UserRole.UNDERAGE_BENEFICIARY}
    return beneficiary_roles.issuperset(user.roles)


def pre_anonymize_user(user: models.User, author: models.User, is_backoffice_action: bool = False) -> None:
    if has_user_pending_anonymization(user.id):
        raise exceptions.UserAlreadyHasPendingAnonymization()

    suspend_account(
        user=user,
        reason=constants.SuspensionReason.WAITING_FOR_ANONYMIZATION,
        actor=author,
        comment="L'utilisateur sera anonymisé le jour de ses 21 ans",
        is_backoffice_action=is_backoffice_action,
    )
    db.session.add(models.GdprUserAnonymization(user=user))
    db.session.flush()


def has_user_pending_anonymization(user_id: int) -> bool:
    return db.session.query(
        db.session.query(models.GdprUserAnonymization).filter(models.GdprUserAnonymization.userId == user_id).exists()
    ).scalar()


def anonymize_beneficiary_users(*, force: bool = False) -> None:
    """
    Anonymize user accounts that have been beneficiaries which have not connected for at least 3
    years, and whose deposit has been expired for at least 5 years and if they have been suspended
    it was at least 5 years ago.
    """
    beneficiaries = (
        db.session.query(models.User)
        .outerjoin(
            finance_models.Deposit,
            models.User.deposits,
        )
        .filter(
            models.User.is_beneficiary,
            models.User.lastConnectionDate < datetime.datetime.utcnow() - relativedelta(years=3),
            finance_models.Deposit.expirationDate < datetime.datetime.utcnow() - relativedelta(years=5),
            sa.or_(
                models.User.suspension_reason.is_(None),  # type: ignore [attr-defined]
                ~models.User.suspension_reason.in_(constants.FRAUD_SUSPENSION_REASONS),  # type: ignore [attr-defined]
                sa.and_(
                    models.User.suspension_reason.in_(constants.FRAUD_SUSPENSION_REASONS),  # type: ignore [attr-defined]
                    models.User.suspension_date < datetime.datetime.utcnow() - relativedelta(years=5),  # type: ignore [operator]
                ),
            ),
        )
    )

    beneficiaries_tagged_to_anonymize = (
        db.session.query(models.User)
        .join(models.GdprUserAnonymization)
        .filter(
            models.User.validatedBirthDate < datetime.datetime.utcnow() - relativedelta(years=21),
            sa.or_(
                models.User.suspension_reason.is_(None),  # type: ignore [attr-defined]
                ~models.User.suspension_reason.in_(constants.FRAUD_SUSPENSION_REASONS),  # type: ignore [attr-defined]
                sa.and_(
                    models.User.suspension_reason.in_(constants.FRAUD_SUSPENSION_REASONS),  # type: ignore [attr-defined]
                    models.User.suspension_date < datetime.datetime.utcnow() - relativedelta(years=5),  # type: ignore [operator]
                ),
            ),
        )
    )
    for user in itertools.chain(beneficiaries, beneficiaries_tagged_to_anonymize):
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
        ~models.User.roles.contains([models.UserRole.ADMIN]),
        ~models.User.roles.contains([models.UserRole.ANONYMIZED]),
        ~models.User.roles.contains([models.UserRole.BENEFICIARY]),
        ~models.User.roles.contains([models.UserRole.UNDERAGE_BENEFICIARY]),
    ]

    aliased_offerer = sa_orm.aliased(offerers_models.Offerer)
    aliased_user_offerer = sa_orm.aliased(offerers_models.UserOfferer)
    aliased_user = sa_orm.aliased(models.User)

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
        db.session.query(models.User.id)
        .join(offerers_models.UserOfferer, models.User.UserOfferers)
        .join(offerers_models.Offerer, offerers_models.UserOfferer.offerer)
        .filter(
            offerers_models.UserOfferer.validationStatus == ValidationStatus.VALIDATED,
            offerers_models.Offerer.isActive,
            models.User.lastConnectionDate < three_years_ago,
            *exclude_non_pro_filters,
            offerers.exists(),
        )
    )

    non_validated_users = (
        db.session.query(models.User.id)
        .join(offerers_models.UserOfferer, models.User.UserOfferers)
        .filter(
            offerers_models.UserOfferer.validationStatus != ValidationStatus.VALIDATED,
            models.User.lastConnectionDate < three_years_ago,
            models.User.roles.contains([models.UserRole.PRO]),
            *exclude_non_pro_filters,
        )
    )
    non_attached_users = db.session.query(models.User.id).filter(
        models.User.lastConnectionDate < three_years_ago,
        models.User.roles.contains([models.UserRole.NON_ATTACHED_PRO]),
        *exclude_non_pro_filters,
    )
    never_connected_users = db.session.query(models.User.id).filter(
        models.User.lastConnectionDate.is_(None),
        models.User.dateCreated < three_years_ago,
        sa.or_(
            models.User.roles.contains([models.UserRole.PRO]),
            models.User.roles.contains([models.UserRole.NON_ATTACHED_PRO]),
        ),
        *exclude_non_pro_filters,
    )

    users = db.session.query(models.User).filter(
        models.User.id.in_(
            sa.union(validated_users, non_validated_users, non_attached_users, never_connected_users).subquery(),
        ),
    )
    for user in users:
        gdpr_delete_pro_user(user)

    db.session.commit()


def gdpr_delete_pro_user(user: models.User) -> None:
    try:
        delete_beamer_user(user.id)
    except BeamerException:
        pass
    _remove_external_user(user)

    db.session.query(history_models.ActionHistory).filter(
        history_models.ActionHistory.userId != user.id,
        history_models.ActionHistory.authorUserId == user.id,
    ).update(
        {
            "authorUserId": None,
        },
        synchronize_session=False,
    )
    db.session.query(offerers_models.UserOfferer).filter(offerers_models.UserOfferer.userId == user.id).delete(
        synchronize_session=False,
    )
    db.session.query(models.User).filter(models.User.id == user.id).delete(synchronize_session=False)


def anonymize_user_deposits() -> None:
    """
    Anonymize deposits that have been expired for at least 10 years.
    """
    deposits_query = db.session.query(finance_models.Deposit).filter(
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


def clean_gdpr_extracts() -> None:
    files = object_storage.list_files(
        folder=settings.GCP_GDPR_EXTRACT_FOLDER,
        bucket=settings.GCP_GDPR_EXTRACT_BUCKET,
    )
    files_ids = set()
    for file_path in files:
        try:
            extract_id = int(Path(file_path).stem)
            files_ids.add(extract_id)
        except ValueError:
            continue

    ids_in_db_query = (
        db.session.query(models.GdprUserDataExtract)
        .filter(models.GdprUserDataExtract.id.in_(files_ids))
        .with_entities(models.GdprUserDataExtract.id)
    )
    ids_in_db = {r.id for r in ids_in_db_query}

    # files in bucket and not in db
    for extract_id in files_ids - ids_in_db:
        delete_gdpr_extract(extract_id)

    extracts_to_delete = (
        db.session.query(models.GdprUserDataExtract)
        .filter(models.GdprUserDataExtract.expirationDate < datetime.datetime.utcnow())  # type: ignore [operator]
        .with_entities(models.GdprUserDataExtract.id)
    )
    for extract in extracts_to_delete:
        # expired extract
        delete_gdpr_extract(extract.id)


def delete_gdpr_extract(extract_id: int) -> None:
    object_storage.delete_public_object(
        folder=settings.GCP_GDPR_EXTRACT_FOLDER,
        object_id=f"{extract_id}.zip",
        bucket=settings.GCP_GDPR_EXTRACT_BUCKET,
    )
    db.session.query(models.GdprUserDataExtract).filter(models.GdprUserDataExtract.id == extract_id).delete()


def _extract_gdpr_chronicles(user: models.User) -> list[users_serialization.GdprChronicleData]:
    chronicles_data = (
        db.session.query(chronicles_models.Chronicle)
        .filter(
            chronicles_models.Chronicle.userId == user.id,
        )
        .options(
            sa_orm.joinedload(chronicles_models.Chronicle.products).load_only(
                offers_models.Product.ean,
                offers_models.Product.name,
            )
        )
    )

    chronicles = []
    for chronicle in chronicles_data:
        product_name = None
        for product in chronicle.products:
            if chronicle.ean and product.ean == chronicle.ean:
                product_name = product.name
                break
        chronicles.append(
            users_serialization.GdprChronicleData(
                age=chronicle.age,
                city=chronicle.city,
                content=chronicle.content,
                dateCreated=chronicle.dateCreated,
                ean=chronicle.ean,
                email=chronicle.email,
                firstName=chronicle.firstName,
                isIdentityDiffusible=chronicle.isIdentityDiffusible,
                isSocialMediaDiffusible=chronicle.isSocialMediaDiffusible,
                productName=product_name,
            )
        )
    return chronicles


def _extract_gdpr_account_update_requests(user: models.User) -> list[users_serialization.GdprAccountUpdateRequests]:
    fr_update_types = {
        models.UserAccountUpdateType.FIRST_NAME: "Prénom",
        models.UserAccountUpdateType.LAST_NAME: "Nom",
        models.UserAccountUpdateType.EMAIL: "Email",
        models.UserAccountUpdateType.PHONE_NUMBER: "Numéro de téléphone",
    }
    update_requests_data = db.session.query(models.UserAccountUpdateRequest).filter(
        models.UserAccountUpdateRequest.userId == user.id,
    )
    update_requests = []
    for update_request in update_requests_data:
        update_requests.append(
            users_serialization.GdprAccountUpdateRequests(
                allConditionsChecked=update_request.allConditionsChecked,
                birthDate=update_request.birthDate,
                dateCreated=update_request.dateCreated,
                dateLastInstructorMessage=update_request.dateLastInstructorMessage,
                dateLastStatusUpdate=update_request.dateLastStatusUpdate,
                dateLastUserMessage=update_request.dateLastUserMessage,
                email=update_request.email,
                firstName=update_request.firstName,
                lastName=update_request.lastName,
                newEmail=update_request.newEmail,
                newFirstName=update_request.newFirstName,
                newLastName=update_request.newLastName,
                newPhoneNumber=update_request.newPhoneNumber,
                oldEmail=update_request.oldEmail,
                status=update_request.status,
                updateTypes=[fr_update_types.get(updateType, "") for updateType in update_request.updateTypes],
            )
        )
    return update_requests


def _extract_gdpr_marketing_data(user: models.User) -> users_serialization.GdprMarketing:
    notification_subscriptions = user.notificationSubscriptions or {}
    return users_serialization.GdprMarketing(
        marketingEmails=notification_subscriptions.get("marketing_email") or False,
        marketingNotifications=notification_subscriptions.get("marketing_push") or False,
    )


def _extract_gdpr_devices_history(
    user: models.User,
) -> list[users_serialization.GdprLoginDeviceHistorySerializer]:
    login_devices_data = (
        db.session.query(models.LoginDeviceHistory)
        .filter(models.LoginDeviceHistory.user == user)
        .order_by(models.LoginDeviceHistory.id)
        .all()
    )
    return [users_serialization.GdprLoginDeviceHistorySerializer.from_orm(data) for data in login_devices_data]


def _extract_gdpr_deposits(user: models.User) -> list[users_serialization.GdprDepositSerializer]:
    deposit_types = {
        finance_models.DepositType.GRANT_15_17.name: "Pass 15-17",
        finance_models.DepositType.GRANT_18.name: "Pass 18",
    }
    deposits_data = (
        db.session.query(finance_models.Deposit)
        .filter(finance_models.Deposit.user == user)
        .order_by(finance_models.Deposit.id)
        .all()
    )
    return [
        users_serialization.GdprDepositSerializer(
            dateCreated=deposit.dateCreated,
            dateUpdated=deposit.dateUpdated,
            expirationDate=deposit.expirationDate,
            amount=deposit.amount,
            source=deposit.source,
            type=deposit_types.get(deposit.type.name, deposit.type.name),
        )
        for deposit in deposits_data
    ]


def _extract_gdpr_email_history(user: models.User) -> list[users_serialization.GdprEmailHistory]:
    emails = (
        db.session.query(models.UserEmailHistory)
        .filter(
            models.UserEmailHistory.user == user,
            models.UserEmailHistory.eventType.in_(
                [
                    models.EmailHistoryEventTypeEnum.CONFIRMATION,
                    models.EmailHistoryEventTypeEnum.ADMIN_UPDATE,
                ]
            ),
        )
        .order_by(models.UserEmailHistory.id)
        .all()
    )
    emails_history = []
    for history in emails:
        new_email = None
        if history.newUserEmail:
            new_email = f"{history.newUserEmail}@{history.newDomainEmail}"
        emails_history.append(
            users_serialization.GdprEmailHistory(
                oldEmail=f"{history.oldUserEmail}@{history.oldDomainEmail}",
                newEmail=new_email,
                dateCreated=history.creationDate,
            )
        )
    return emails_history


def _extract_gdpr_action_history(user: models.User) -> list[users_serialization.GdprActionHistorySerializer]:
    actions_history = (
        db.session.query(history_models.ActionHistory)
        .filter(
            history_models.ActionHistory.user == user,
            history_models.ActionHistory.actionType.in_(
                [
                    history_models.ActionType.USER_SUSPENDED,
                    history_models.ActionType.USER_UNSUSPENDED,
                    history_models.ActionType.USER_PHONE_VALIDATED,
                    history_models.ActionType.USER_EMAIL_VALIDATED,
                ],
            ),
        )
        .order_by(history_models.ActionHistory.id)
        .all()
    )
    return [users_serialization.GdprActionHistorySerializer.from_orm(a) for a in actions_history]


def _extract_gdpr_beneficiary_validation(
    user: models.User,
) -> list[users_serialization.GdprBeneficiaryValidation]:
    check_types = {
        fraud_models.FraudCheckType.DMS.name: "Démarches simplifiées",
        fraud_models.FraudCheckType.EDUCONNECT.name: "ÉduConnect",
        fraud_models.FraudCheckType.HONOR_STATEMENT.name: "Attestation sur l'honneur",
        fraud_models.FraudCheckType.INTERNAL_REVIEW.name: "Revue Interne",
        fraud_models.FraudCheckType.JOUVE.name: "Jouve",
        fraud_models.FraudCheckType.PHONE_VALIDATION.name: "Validation par téléphone",
        fraud_models.FraudCheckType.PROFILE_COMPLETION.name: "Complétion du profil",
        fraud_models.FraudCheckType.UBBLE.name: "Ubble",
        fraud_models.FraudCheckType.USER_PROFILING.name: "Profilage d'utilisateur",
    }
    check_status = {
        fraud_models.FraudCheckStatus.CANCELED.name: "Annulé",
        fraud_models.FraudCheckStatus.ERROR.name: "Erreur",
        fraud_models.FraudCheckStatus.KO.name: "Échec",
        fraud_models.FraudCheckStatus.OK.name: "Succès",
        fraud_models.FraudCheckStatus.PENDING.name: "En attente",
        fraud_models.FraudCheckStatus.STARTED.name: "Commencé",
        fraud_models.FraudCheckStatus.SUSPICIOUS.name: "Suspect",
    }
    eligibility_types = {
        models.EligibilityType.AGE18.name: "Pass 18",
        models.EligibilityType.UNDERAGE.name: "Pass 15-17",
    }
    beneficiary_fraud_checks = (
        db.session.query(fraud_models.BeneficiaryFraudCheck)
        .filter(fraud_models.BeneficiaryFraudCheck.user == user)
        .order_by(fraud_models.BeneficiaryFraudCheck.id)
        .all()
    )
    return [
        users_serialization.GdprBeneficiaryValidation(
            dateCreated=fraud_check.dateCreated,
            eligibilityType=(
                eligibility_types.get(fraud_check.eligibilityType.name, fraud_check.eligibilityType.name)
                if fraud_check.eligibilityType
                else None
            ),
            status=check_status.get(fraud_check.status.name, fraud_check.status.name) if fraud_check.status else None,
            type=check_types.get(fraud_check.type.name, fraud_check.type.name),
            updatedAt=fraud_check.updatedAt,
        )
        for fraud_check in beneficiary_fraud_checks
    ]


def _extract_gdpr_booking_data(user: models.User) -> list[users_serialization.GdprBookingSerializer]:
    booking_status = {
        bookings_models.BookingStatus.CONFIRMED.name: "Réservé",
        bookings_models.BookingStatus.USED.name: "Utilisé",
        bookings_models.BookingStatus.CANCELLED.name: "Annulé",
        bookings_models.BookingStatus.REIMBURSED.name: "Utilisé",
    }
    bookings_data = (
        db.session.query(bookings_models.Booking)
        .filter(
            bookings_models.Booking.user == user,
        )
        .options(
            sa_orm.joinedload(bookings_models.Booking.stock).joinedload(offers_models.Stock.offer),
            sa_orm.joinedload(bookings_models.Booking.venue),
            sa_orm.joinedload(bookings_models.Booking.venue).joinedload(offerers_models.Venue.managingOfferer),
        )
        .order_by(bookings_models.Booking.id)
    )
    bookings = []
    for booking_data in bookings_data:
        offerer = booking_data.venue.managingOfferer
        bookings.append(
            users_serialization.GdprBookingSerializer(
                cancellationDate=booking_data.cancellationDate,
                dateCreated=booking_data.dateCreated,
                dateUsed=booking_data.dateUsed,
                quantity=booking_data.quantity,
                amount=booking_data.amount,
                status=booking_status.get(booking_data.status.name, booking_data.status.name),
                name=booking_data.stock.offer.name,
                venue=booking_data.venue.common_name,
                offerer=offerer.name,
            )
        )
    return bookings


def _extract_gdpr_brevo_data(user: models.User) -> dict:
    return get_raw_contact_data(user.email, user.has_any_pro_role)


def _dump_gdpr_data_container_as_json_bytes(
    container: users_serialization.GdprDataContainer,
) -> tuple[zipfile.ZipInfo, bytes]:
    json_bytes = container.json(indent=4).encode("utf-8")
    file_info = zipfile.ZipInfo(
        filename=f"{container.internal.user.email}.json",
        date_time=datetime.datetime.utcnow().timetuple()[:6],
    )
    return file_info, json_bytes


def _dump_gdpr_data_container_as_pdf_bytes(
    container: users_serialization.GdprDataContainer,
) -> tuple[zipfile.ZipInfo, bytes]:
    html_content = render_template("extracts/beneficiary_extract.html", container=container)
    pdf_bytes = generate_pdf_from_html(html_content=html_content)
    file_info = zipfile.ZipInfo(
        filename=f"{container.internal.user.email}.pdf",
        date_time=datetime.datetime.utcnow().timetuple()[:6],
    )
    return file_info, pdf_bytes


def _generate_archive_from_gdpr_data_container(container: users_serialization.GdprDataContainer) -> BytesIO:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", allowZip64=False) as zip_file:
        zip_file.writestr(*_dump_gdpr_data_container_as_json_bytes(container))
        zip_file.writestr(*_dump_gdpr_data_container_as_pdf_bytes(container))
    buffer.seek(0)
    return buffer


def _store_gdpr_archive(name: str, archive: bytes) -> None:
    store_public_object(
        folder=settings.GCP_GDPR_EXTRACT_FOLDER,
        object_id=name,
        blob=archive,
        content_type="application/zip",
        bucket=settings.GCP_GDPR_EXTRACT_BUCKET,
    )


def extract_beneficiary_data(extract: models.GdprUserDataExtract) -> None:
    extract.dateProcessed = datetime.datetime.utcnow()
    user = extract.user
    data = users_serialization.GdprDataContainer(
        generationDate=datetime.datetime.utcnow(),
        internal=users_serialization.GdprInternal(
            user=users_serialization.GdprUserSerializer.from_orm(user),
            marketing=_extract_gdpr_marketing_data(user),
            loginDevices=_extract_gdpr_devices_history(user),
            emailsHistory=_extract_gdpr_email_history(user),
            actionsHistory=_extract_gdpr_action_history(user),
            beneficiaryValidations=_extract_gdpr_beneficiary_validation(user),
            deposits=_extract_gdpr_deposits(user),
            bookings=_extract_gdpr_booking_data(user),
            chronicles=_extract_gdpr_chronicles(user),
            accountUpdateRequests=_extract_gdpr_account_update_requests(user),
        ),
        external=users_serialization.GdprExternal(
            brevo=_extract_gdpr_brevo_data(user),
        ),
    )
    archive = _generate_archive_from_gdpr_data_container(data)
    _store_gdpr_archive(
        name=f"{extract.id}.zip",
        archive=archive.getvalue(),
    )
    add_action(history_models.ActionType.USER_EXTRACT_DATA, author=extract.authorUser, user=extract.user)
    db.session.flush()


def _get_extract_beneficiary_data_lock() -> bool:
    result = app.redis_client.set(
        constants.GDPR_EXTRACT_DATA_LOCK,
        "locked",
        ex=settings.GDPR_LOCK_TIMEOUT,
        nx=True,
    )
    return bool(result)


def _release_extract_beneficiary_data_lock() -> None:
    app.redis_client.delete(constants.GDPR_EXTRACT_DATA_LOCK)


def extract_beneficiary_data_command() -> bool:
    counter = ExtractBeneficiaryDataCounter(
        key=constants.GDPR_EXTRACT_DATA_COUNTER, max_value=settings.GDPR_MAX_EXTRACT_PER_DAY
    )
    counter.reset()

    if not _get_extract_beneficiary_data_lock():
        return False

    if counter.is_full():
        _release_extract_beneficiary_data_lock()
        return False

    candidates = (
        db.session.query(models.GdprUserDataExtract)
        .filter(
            models.GdprUserDataExtract.dateProcessed.is_(None),
            models.GdprUserDataExtract.expirationDate > datetime.datetime.utcnow(),  # type: ignore [operator]
        )
        .options(
            sa_orm.joinedload(models.GdprUserDataExtract.user),
            sa_orm.joinedload(models.GdprUserDataExtract.authorUser),
        )
        .limit(10)
        .all()
    )
    if not candidates:
        _release_extract_beneficiary_data_lock()
        return False

    # choose one at random to avoid being stuck on a buggy extract
    extract = random.choice(candidates)
    try:
        extract_beneficiary_data(extract)
    finally:
        _release_extract_beneficiary_data_lock()
    counter += 1  # type: ignore [misc]
    return True
