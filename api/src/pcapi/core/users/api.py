import datetime
import enum
import logging
import re
import typing
from dataclasses import asdict
from decimal import Decimal

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from dateutil.relativedelta import relativedelta
from flask import current_app as app
from flask import request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token

import pcapi.core.bookings.exceptions as bookings_exceptions
import pcapi.core.bookings.models as bookings_models
import pcapi.core.bookings.repository as bookings_repository
import pcapi.core.history.api as history_api
import pcapi.core.history.models as history_models
import pcapi.core.mails.transactional as transactional_mails
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.subscription.fraud_check_api as fraud_api
import pcapi.core.subscription.phone_validation.exceptions as phone_validation_exceptions
import pcapi.core.subscription.repository as subscription_repository
import pcapi.core.subscription.schemas as subscription_schemas
import pcapi.core.users.repository as users_repository
import pcapi.core.users.utils as users_utils
import pcapi.utils.date as date_utils
import pcapi.utils.email as email_utils
import pcapi.utils.postal_code as postal_code_utils
from pcapi import settings
from pcapi.core import mails as mails_api
from pcapi.core import token as token_utils
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.external.sendinblue import update_contact_attributes
from pcapi.core.finance import deposit_api
from pcapi.core.finance import models as finance_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus import constants as bonus_constants
from pcapi.core.subscription.dms import api as dms_subscription_api
from pcapi.core.users import constants
from pcapi.core.users import exceptions
from pcapi.core.users import models
from pcapi.core.users.email.update import check_email_address_does_not_exist
from pcapi.core.users.password_utils import check_password_strength
from pcapi.core.users.password_utils import random_password
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.serialization import users as users_serialization
from pcapi.utils import phone_number as phone_number_utils
from pcapi.utils import transaction_manager
from pcapi.utils.clean_accents import clean_accents
from pcapi.utils.repository import atomic
from pcapi.utils.requests import ExternalAPIException


if typing.TYPE_CHECKING:
    from pcapi.connectors import google_oauth
    from pcapi.routes.native.v1.serialization import account as account_serialization


class T_UNCHANGED(enum.Enum):
    TOKEN = 0


UNCHANGED = T_UNCHANGED.TOKEN

EMAIL_CONFIRMATION_TEST_EMAIL_PATTERN = "+e2e@"


logger = logging.getLogger(__name__)


def create_reset_password_token(user: models.User, expiration: datetime.datetime | None = None) -> token_utils.Token:
    return token_utils.Token.create(
        token_utils.TokenType.RESET_PASSWORD,
        date_utils.get_naive_utc_now() - expiration if expiration else constants.RESET_PASSWORD_TOKEN_LIFE_TIME,
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
        lastConnectionDate=date_utils.get_naive_utc_now(),
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
    birth_place: str | None = None,
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
    if birth_place is not None:
        user.birthPlace = birth_place
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

    return user


def update_user_information_from_external_source(
    user: models.User, data: subscription_schemas.IdentityCheckContent, *, id_piece_number: str | None = None
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
        birth_place=data.get_birth_place(),
        activity=data.get_activity(),
        address=data.get_address(),
        city=data.get_city(),
        civility=data.get_civility(),
        id_piece_number=id_piece_number or data.get_id_piece_number(),
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


def _email_resends_key(email: str) -> str:
    return f"email_resends:{email}"


def get_remaining_email_resends(email: str) -> int:
    email_validation_resends_count = app.redis_client.get(_email_resends_key(email))

    if email_validation_resends_count:
        return max(settings.MAX_EMAIL_RESENDS - int(email_validation_resends_count), 0)

    return settings.MAX_EMAIL_RESENDS


def get_email_validation_resends_limitation_expiration_time(email: str) -> datetime.datetime | None:
    ttl = app.redis_client.ttl(_email_resends_key(email))

    if ttl > 0:
        return date_utils.get_naive_utc_now() + datetime.timedelta(seconds=ttl)

    return None


def check_email_validation_resends_count(email: str) -> None:
    """
    Check if the user has reached the maximum number of email validation resends.
    If yes, raise an exception.
    """
    email_validation_resends = app.redis_client.get(_email_resends_key(email))

    if email_validation_resends and int(email_validation_resends) >= settings.MAX_EMAIL_RESENDS:
        raise exceptions.EmailValidationLimitReached()


def increment_email_resends_count(email: str) -> None:
    """
    Increment or initiate the number of resends of the email validation email
    """
    email_validation_resends_key = _email_resends_key(email)
    email_validation_resends = app.redis_client.incr(email_validation_resends_key)

    if email_validation_resends == 1:
        # If the key did not exist, set the expiration time
        app.redis_client.expire(email_validation_resends_key, settings.EMAIL_RESENDS_TTL)


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
        user = db.session.get(models.User, token.user_id)
    except exceptions.InvalidToken:
        raise ApiErrors({"token": ["Le token de changement de mot de passe est invalide."]})

    assert user  # helps mypy
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

    with atomic():
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

    remove_external_user(user)

    return {"cancelled_bookings": n_bookings}


def remove_external_user(user: models.User) -> bool:
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
                date_utils.get_naive_utc_now() < bookings_models.Booking.cancellationLimitDate,
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
        try:
            if not is_backoffice_action and reason in _USER_REQUESTED_REASONS:
                bookings_api.cancel_booking_on_user_requested_account_suspension(booking)
            else:
                bookings_api.cancel_booking_for_fraud(booking, reason)
        except bookings_exceptions.BookingIsAlreadyCancelled:
            # race conditions can occur when we receive two simultaneous calls in our exposed webhooks
            # do nothing in such cases
            continue

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
    if not transaction_manager.is_managed_transaction():
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

    current_user.email = new_email
    db.session.add(current_user)
    db.session.add(email_history)
    db.session.commit()

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
    check_email_address_does_not_exist(new_email)
    change_email(current_user, new_email)


def update_user_password(user: models.User, new_password: str) -> None:
    user.setPassword(new_password)
    db.session.add(user)
    if transaction_manager.is_managed_transaction():
        db.session.flush()
    else:
        db.session.commit()


def update_password_and_external_user(user: models.User, new_password: str) -> None:
    user.setPassword(new_password)
    if not user.isEmailValidated:
        user.isEmailValidated = True
        external_attributes_api.update_external_user(user)
    db.session.add(user)
    db.session.commit()


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
        user_phone_number = user.phoneNumber
        if user_phone_number != phone_number:
            snapshot.set("phoneNumber", old=user_phone_number, new=phone_number)
        user.phoneNumber = phone_number
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
            if user.deposit and user.has_active_deposit and validated_birth_date is not None:
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
            batch_extra_data["last_status_update_date"] = date_utils.get_naive_utc_now()
        user.activity = activity.value

    if commit:
        snapshot.add_action()
        db.session.add(user)
        db.session.commit
    else:
        db.session.add(user)

    # TODO(prouzet) even for young users, we should probably remove contact with former email from sendinblue lists
    if old_email and user.has_pro_role:
        external_attributes_api.update_external_pro(old_email)
    external_attributes_api.update_external_user(user, batch_extra_data=batch_extra_data)

    return snapshot


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
            if booking_finance_incident.incident.status in (
                finance_models.IncidentStatus.VALIDATED,
                finance_models.IncidentStatus.INVOICED,
            ):
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
    token = token_utils.create_passwordless_login_token(
        user_id=new_pro_user.id, ttl=constants.PASSWORDLESS_TOKEN_LIFE_TIME
    )
    if settings.IS_DEV or settings.IS_TESTING:
        logger.info("Link for signup confirmation: %s/inscription/compte/confirmation/%s", settings.PRO_URL, token)
    transactional_mails.send_signup_email_confirmation_to_pro(new_pro_user, token)

    external_attributes_api.update_external_pro(new_pro_user.email)


def create_pro_user(pro_user: users_serialization.ProUserCreationBodyV2Model) -> models.User:
    new_pro_user = models.User(
        email=pro_user.email,
        firstName=pro_user.first_name,
        lastName=pro_user.last_name,
        phoneNumber=pro_user.phone_number,
    )
    new_pro_user.setPassword(pro_user.password)
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
        eighteen_years_ago = date_utils.get_naive_utc_now() - datetime.timedelta(days=366 * 18)
        new_pro_user.dateOfBirth = eighteen_years_ago
        new_pro_user.validatedBirthDate = new_pro_user.dateOfBirth.date()
        deposit = deposit_api.upsert_deposit(new_pro_user, "integration_signup", models.EligibilityType.AGE18)
        new_pro_user.deposits = [deposit]

    db.session.add(new_pro_user)
    db.session.flush()

    history_api.add_action(history_models.ActionType.USER_CREATED, author=new_pro_user, user=new_pro_user)

    return new_pro_user


def set_pro_tuto_as_seen(user: models.User) -> None:
    user.hasSeenProTutorials = True
    db.session.add(user)
    db.session.commit()


def set_pro_rgs_as_seen(user: models.User) -> None:
    user.hasSeenProRgs = True
    db.session.add(user)
    db.session.commit()


def update_last_connection_date(user: models.User) -> None:
    previous_connection_date = user.lastConnectionDate
    last_connection_date = date_utils.get_naive_utc_now()

    should_save_last_connection_date = (
        not previous_connection_date or last_connection_date - previous_connection_date > datetime.timedelta(minutes=15)
    )
    should_update_sendinblue_last_connection_date = should_save_last_connection_date and (
        not previous_connection_date
        or last_connection_date.date() - previous_connection_date.date() >= datetime.timedelta(days=1)
    )

    if should_save_last_connection_date:
        user.lastConnectionDate = last_connection_date
        db.session.add(user)
        db.session.commit()

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
        constants.OAUTH_STATE_TOKEN_LIFE_TIME,
    )
    return token.encoded_token


def create_account_creation_token(google_user: "google_oauth.GoogleUser") -> str:
    token = token_utils.UUIDToken.create(
        token_utils.TokenType.ACCOUNT_CREATION,
        constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME,
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
    db.session.add(user)
    db.session.commit()


def _filter_user_accounts(accounts: sa_orm.Query, search_term: str) -> sa_orm.Query:
    filters: list[sa.ColumnElement | sa.BinaryExpression] = []
    name_term = None

    if not search_term:
        return accounts

    term_filters: list[sa.ColumnElement] = []

    # phone number
    try:
        parsed_phone_number = phone_number_utils.parse_phone_number(search_term)
        term_as_phone_number = phone_number_utils.get_formatted_phone_number(parsed_phone_number)
    except phone_validation_exceptions.InvalidPhoneNumber:
        pass  # term can't be a phone number
    else:
        term_filters.append(models.User.phoneNumber == term_as_phone_number)

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


def search_public_account(search_query: str) -> sa_orm.Query:
    public_accounts = get_public_account_base_query()
    public_accounts = public_accounts.options(
        sa_orm.joinedload(models.User.tags).load_only(models.UserTag.id, models.UserTag.name, models.UserTag.label),
    )

    return _filter_user_accounts(public_accounts, search_query)


def search_public_account_in_history_email(search_query: str) -> sa_orm.Query:
    sanitized_term = email_utils.sanitize_email(search_query)
    if not email_utils.is_valid_email(sanitized_term):
        raise ValueError(f"Unsupported email search on invalid email: {search_query}")

    accounts = get_public_account_base_query()

    if not search_query:
        return accounts.filter(sa.false())

    # including old emails: look for validated email updates inside user_email_history
    return (
        accounts.join(models.UserEmailHistory)
        .filter(
            typing.cast(sa_orm.Mapped[str], models.UserEmailHistory.oldEmail) == sanitized_term,
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


def get_public_account_base_query() -> sa_orm.Query:
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
            sa.or_(
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
def search_pro_account(search_query: str, *_: typing.Any) -> sa_orm.Query:
    pro_accounts = (
        db.session.query(models.User)
        .filter(models.User.has_any_pro_role)
        .outerjoin(
            finance_models.Deposit,
            # load only the last deposit to avoid breaking line count
            sa.and_(
                models.User.id == finance_models.Deposit.userId,
                finance_models.Deposit.expirationDate > date_utils.get_naive_utc_now(),
            ),
        )
    )

    return _filter_user_accounts(pro_accounts, search_query).options(
        sa_orm.with_expression(models.User.suspension_reason_expression, models.User.suspension_reason.expression),
        sa_orm.with_expression(models.User.suspension_date_expression, models.User.suspension_date.expression),
        sa_orm.joinedload(models.User.UserOfferers).load_only(offerers_models.UserOfferer.validationStatus),
        sa_orm.contains_eager(models.User.deposits),
    )


def get_pro_account_base_query(pro_id: int) -> sa_orm.Query:
    return db.session.query(models.User).filter(
        models.User.id == pro_id,
        models.User.has_any_pro_role,
    )


def search_backoffice_accounts(search_query: str) -> sa_orm.Query:
    bo_accounts = (
        db.session.query(models.User)
        .join(models.User.backoffice_profile)
        .options(
            sa_orm.with_expression(models.User.suspension_reason_expression, models.User.suspension_reason.expression),
            sa_orm.with_expression(models.User.suspension_date_expression, models.User.suspension_date.expression),
        )
    )

    if not search_query:
        return bo_accounts

    return _filter_user_accounts(bo_accounts, search_query)


def validate_pro_user_email(user: models.User, author_user: models.User | None = None) -> None:
    user.isEmailValidated = True

    if author_user:
        history_api.add_action(history_models.ActionType.USER_EMAIL_VALIDATED, author=author_user, user=user)

    db.session.add(user)
    if transaction_manager.is_managed_transaction():
        db.session.flush()
    else:
        db.session.commit()

    # FIXME (prouzet-pass): accept_offerer_invitation_if_exists also add() and commit()... in a loop!
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
    db.session.add(trusted_device)
    if transaction_manager.is_managed_transaction():
        db.session.flush()
    else:
        db.session.commit()


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
    db.session.add(login_device)
    db.session.commit()

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
    yesterday = date_utils.get_naive_utc_now() - relativedelta(hours=24)
    recent_logins = (
        db.session.query(models.LoginDeviceHistory)
        .filter(
            models.LoginDeviceHistory.userId == user.id,
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
            constants.SUSPICIOUS_LOGIN_EMAIL_TOKEN_LIFE_TIME,
            user_id,
            {"dateCreated": date_utils.get_naive_utc_now().strftime(date_utils.DATE_ISO_FORMAT)},
        )

    passed_ttl = date_utils.get_naive_utc_now() - login_info.dateCreated
    remaining_ttl = constants.SUSPICIOUS_LOGIN_EMAIL_TOKEN_LIFE_TIME - passed_ttl

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
    five_years_ago = date_utils.get_naive_utc_now() - relativedelta(years=5)

    db.session.query(models.TrustedDevice).filter(models.TrustedDevice.dateCreated <= five_years_ago).delete()
    db.session.commit()


def delete_old_login_device_history() -> None:
    thirteen_months_ago = date_utils.get_naive_utc_now() - relativedelta(months=13)

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


def apply_filter_on_beneficiary_tag(query: sa_orm.Query, tag_ids: list[int]) -> sa_orm.Query:
    return query.join(models.User.tags).filter(models.UserTag.id.in_(tag_ids)) if tag_ids else query


def has_profile_expired(user: models.User) -> bool:
    should_check_for_profile_expiration = (
        models.UserRole.UNDERAGE_BENEFICIARY in user.roles or models.UserRole.BENEFICIARY in user.roles
    )
    if not should_check_for_profile_expiration:
        return False

    campaign_date = _get_current_profile_refresh_campaign_date()
    if not campaign_date:
        return False

    latest_profile_completion = subscription_repository.get_latest_completed_profile_check(user)
    has_completed_profile_after_campaign_start = (
        latest_profile_completion and latest_profile_completion.dateCreated >= campaign_date
    )

    latest_profile_modification = _get_latest_profile_modification(user)
    has_modified_profile_after_campaign_start = (
        latest_profile_modification
        and latest_profile_modification.actionDate
        and latest_profile_modification.actionDate >= campaign_date
    )

    # The profile has never been completed → it's not expired
    if latest_profile_completion is None and latest_profile_modification is None:
        logger.error("User %s is beneficiary without completing their profile", user.id)
        return False

    return not (has_completed_profile_after_campaign_start or has_modified_profile_after_campaign_start)


def _get_latest_profile_modification(user: models.User) -> history_models.ActionHistory | None:
    profile_modification_actions = [
        action for action in user.action_history if _has_modified_user_profile(action) and action.actionDate is not None
    ]
    last_profile_modification_action = max(
        profile_modification_actions, key=lambda action: action.actionDate, default=None
    )
    return last_profile_modification_action


def _has_modified_user_profile(action: history_models.ActionHistory) -> bool:
    profile_fields = ["activity", "address", "city", "postalCode", "schoolType"]
    return bool(
        action.actionType == history_models.ActionType.INFO_MODIFIED
        and action.extraData
        and "modified_info" in action.extraData
        and any(action.extraData["modified_info"].get(field) is not None for field in profile_fields)
    )


def _get_current_profile_refresh_campaign_date() -> datetime.datetime | None:
    """
    Fetch the first campaign starting from the current date
    """
    return (
        db.session.query(models.UserProfileRefreshCampaign)
        .with_entities(models.UserProfileRefreshCampaign.campaignDate)
        .filter(models.UserProfileRefreshCampaign.isActive.is_(True))
        .order_by(models.UserProfileRefreshCampaign.campaignDate.desc())
        .limit(1)
        .scalar()
    )


def get_user_is_eligible_for_bonification(user: models.User, *, is_from_backoffice: bool = False) -> bool:
    excluded_statuses = {
        subscription_models.QFBonificationStatus.GRANTED,
        subscription_models.QFBonificationStatus.NOT_ELIGIBLE,
    }
    if not is_from_backoffice:
        excluded_statuses |= {
            subscription_models.QFBonificationStatus.TOO_MANY_RETRIES,
            subscription_models.QFBonificationStatus.STARTED,
        }
    return deposit_api.can_receive_bonus_credit(user) and get_user_qf_bonification_status(user) not in excluded_statuses


def get_qf_bonus_credit_fraud_checks(user: models.User) -> list[subscription_models.BeneficiaryFraudCheck]:
    # `user.beneficiaryFraudChecks` are ordered by creation date
    return [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type == subscription_models.FraudCheckType.QF_BONUS_CREDIT
        and fraud_check.status != subscription_models.FraudCheckStatus.MOCK_CONFIG
    ]


def get_user_qf_bonification_status(user: models.User) -> subscription_models.QFBonificationStatus:
    is_18_years_old = user.age == 18
    has_v3_credit = user.received_pass_17_18

    if not is_18_years_old or not user.is_beneficiary or not has_v3_credit:
        return subscription_models.QFBonificationStatus.NOT_ELIGIBLE

    qf_bonus_credit_fraud_checks = get_qf_bonus_credit_fraud_checks(user)
    bonus_fraud_check = qf_bonus_credit_fraud_checks[-1] if qf_bonus_credit_fraud_checks else None
    bonus_fraud_check_status = bonus_fraud_check.status if bonus_fraud_check is not None else None

    if bonus_fraud_check_status in (
        subscription_models.FraudCheckStatus.STARTED,
        subscription_models.FraudCheckStatus.PENDING,
    ):
        return subscription_models.QFBonificationStatus.STARTED

    if bonus_fraud_check_status == subscription_models.FraudCheckStatus.OK:
        return subscription_models.QFBonificationStatus.GRANTED

    has_never_completely_tried = bonus_fraud_check_status in (
        None,
        subscription_models.FraudCheckStatus.CANCELED,
        subscription_models.FraudCheckStatus.ERROR,
    )

    if is_18_years_old and has_v3_credit and has_never_completely_tried:
        return subscription_models.QFBonificationStatus.ELIGIBLE

    if bonus_fraud_check_status == subscription_models.FraudCheckStatus.KO:
        reason_codes = (bonus_fraud_check.reasonCodes if bonus_fraud_check else None) or []

        if (
            sum(
                1
                for fraud_check in qf_bonus_credit_fraud_checks
                if not (fraud_check.reason and fraud_check.reason.startswith(bonus_constants.BACKOFFICE_ORIGIN_START))
            )
            >= constants.MAX_QF_BONUS_RETRIES
        ):
            return subscription_models.QFBonificationStatus.TOO_MANY_RETRIES

        if subscription_models.FraudReasonCode.NOT_IN_TAX_HOUSEHOLD in reason_codes:
            return subscription_models.QFBonificationStatus.NOT_IN_TAX_HOUSEHOLD

        if subscription_models.FraudReasonCode.QUOTIENT_FAMILIAL_TOO_HIGH in reason_codes:
            return subscription_models.QFBonificationStatus.QUOTIENT_FAMILIAL_TOO_HIGH

        if subscription_models.FraudReasonCode.CUSTODIAN_NOT_FOUND in reason_codes:
            return subscription_models.QFBonificationStatus.CUSTODIAN_NOT_FOUND

    return subscription_models.QFBonificationStatus.UNKNOWN_KO


def get_latest_user_recredit_type(user: models.User) -> finance_models.RecreditType | None:
    recredit = deposit_api.get_latest_age_related_user_recredit(user) if user.recreditAmountToShow else None
    return recredit.recreditType if recredit else None


def get_user_remaining_bonus_attempts(user: models.User) -> int:
    qf_bonification_status = get_user_qf_bonification_status(user)

    if qf_bonification_status in (
        subscription_models.QFBonificationStatus.TOO_MANY_RETRIES,
        subscription_models.QFBonificationStatus.GRANTED,
    ):
        return 0

    ko_qf_bonus_credit_fraud_checks = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type == subscription_models.FraudCheckType.QF_BONUS_CREDIT
        and fraud_check.status == subscription_models.FraudCheckStatus.KO
        if not (fraud_check.reason and fraud_check.reason.startswith(bonus_constants.BACKOFFICE_ORIGIN_START))
    ]
    return constants.MAX_QF_BONUS_RETRIES - len(ko_qf_bonus_credit_fraud_checks)
