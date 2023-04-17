from dataclasses import asdict
import datetime
from decimal import Decimal
import enum
import logging
import secrets
import typing

from dateutil.relativedelta import relativedelta
from flask_jwt_extended import create_access_token
from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa

from pcapi import settings
from pcapi.connectors import sirene
import pcapi.core.bookings.models as bookings_models
import pcapi.core.bookings.repository as bookings_repository
from pcapi.core.external.attributes import api as external_attributes_api
import pcapi.core.finance.api as finance_api
import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.common.models as common_fraud_models
import pcapi.core.history.api as history_api
import pcapi.core.history.models as history_models
import pcapi.core.mails.transactional as transactional_mails
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.models as offerers_models
import pcapi.core.subscription.phone_validation.exceptions as phone_validation_exceptions
import pcapi.core.users.constants as users_constants
import pcapi.core.users.email.update as email_update
import pcapi.core.users.models as users_models
import pcapi.core.users.repository as users_repository
import pcapi.core.users.utils as users_utils
from pcapi.domain.password import random_hashed_password
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.repository import repository
from pcapi.routes.serialization.users import ProUserCreationBodyModel
from pcapi.routes.serialization.users import ProUserCreationBodyV2Model
from pcapi.tasks import batch_tasks
from pcapi.utils.clean_accents import clean_accents
import pcapi.utils.db as db_utils
import pcapi.utils.email as email_utils
import pcapi.utils.phone_number as phone_number_utils
import pcapi.utils.postal_code as postal_code_utils

from . import constants
from . import exceptions
from . import models


if typing.TYPE_CHECKING:
    from pcapi.routes.native.v1.serialization import account as account_serialization


class T_UNCHANGED(enum.Enum):
    TOKEN = 0


UNCHANGED = T_UNCHANGED.TOKEN

logger = logging.getLogger(__name__)


def create_email_validation_token(user: models.User) -> models.Token:
    return generate_and_save_token(
        user,
        models.TokenType.EMAIL_VALIDATION,
        expiration=datetime.datetime.utcnow() + constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME,
    )


def create_reset_password_token(user: models.User, expiration: datetime.datetime | None = None) -> models.Token:
    return generate_and_save_token(
        user,
        models.TokenType.RESET_PASSWORD,
        expiration=expiration or datetime.datetime.utcnow() + constants.RESET_PASSWORD_TOKEN_LIFE_TIME,
    )


def create_phone_validation_token(
    user: models.User,
    phone_number: str,
    expiration: datetime.datetime | None = None,
) -> models.Token | None:
    secret_code = "{:06}".format(secrets.randbelow(1_000_000))  # 6 digits
    return generate_and_save_token(
        user,
        token_type=models.TokenType.PHONE_VALIDATION,
        expiration=expiration,
        token_value=secret_code,
        extra_data=models.TokenExtraData(phone_number=phone_number),
    )


def generate_and_save_token(
    user: models.User,
    token_type: models.TokenType,
    expiration: datetime.datetime | None = None,
    token_value: str | None = None,
    extra_data: models.TokenExtraData | None = None,
) -> models.Token:
    assert token_type.name in models.TokenType.__members__, "Only registered token types are allowed"

    if settings.IS_PERFORMANCE_TESTS:
        token_value = f"performance-tests_{token_type.value}_{user.id}"
    else:
        token_value = token_value or secrets.token_urlsafe(32)

    token = models.Token(
        user=user,
        value=token_value,
        type=token_type,
        expirationDate=expiration,
        extraData=asdict(extra_data) if extra_data else None,  # type: ignore [arg-type]
    )
    repository.save(token)

    return token


def delete_expired_tokens() -> None:
    models.Token.query.filter(
        models.Token.expirationDate < datetime.datetime.utcnow() - users_constants.TOKEN_DELETION_AFTER_EXPIRATION_DELAY
    ).delete()


def delete_all_users_tokens(user: models.User) -> None:
    models.Token.query.filter(models.Token.user == user).delete()


def delete_all_users_phone_validation_tokens(user: models.User) -> None:
    models.Token.query.filter(
        models.Token.user == user, users_models.Token.type == users_models.TokenType.PHONE_VALIDATION
    ).delete()


def create_account(
    email: str,
    password: str,
    birthdate: datetime.date,
    marketing_email_subscription: bool = False,
    is_email_validated: bool = False,
    send_activation_mail: bool = True,
    remote_updates: bool = True,
    phone_number: str = None,
    apps_flyer_user_id: str = None,
    apps_flyer_platform: str = None,
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

    user.setPassword(password)

    if apps_flyer_user_id and apps_flyer_platform:
        if user.externalIds is None:
            user.externalIds = {}
        user.externalIds["apps_flyer"] = {"user": apps_flyer_user_id, "platform": apps_flyer_platform.upper()}  # type: ignore [index, call-overload]

    repository.save(user)
    logger.info("Created user account", extra={"user": user.id})

    delete_all_users_tokens(user)

    if remote_updates:
        external_attributes_api.update_external_user(user)

    if not user.isEmailValidated and send_activation_mail:
        request_email_confirmation(user)

    return user


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
    token = create_email_validation_token(user)
    transactional_mails.send_email_confirmation_email(user, token=token)


def request_password_reset(user: models.User | None) -> None:
    if not user:
        return

    token = create_reset_password_token(user)
    is_email_sent = transactional_mails.send_reset_password_email_to_user(user, token)

    if not is_email_sent:
        logger.error("Email service failure when user requested password reset for email '%s'", user.email)
        raise exceptions.EmailNotSent()


def handle_create_account_with_existing_email(user: models.User) -> None:
    if not user:
        return

    token = create_reset_password_token(user)
    is_email_sent = transactional_mails.send_email_already_exists_email(user, token)

    if not is_email_sent:
        logger.error("Email service failure when user email already exists in database '%s'", user.email)
        raise exceptions.EmailNotSent()


def fulfill_account_password(user: models.User) -> models.User:
    _generate_random_password(user)
    return user


def fulfill_beneficiary_data(
    user: models.User, deposit_source: str, eligibility: models.EligibilityType
) -> models.User:
    _generate_random_password(user)

    deposit = finance_api.create_deposit(user, deposit_source, eligibility=eligibility)
    user.deposits = [deposit]

    return user


def _generate_random_password(user):  # type: ignore [no-untyped-def]
    user.password = random_hashed_password()


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
    if reason == constants.SuspensionReason.FRAUD_SUSPICION:
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
            bookings_models.Booking.cancellationLimitDate == None,
        ),
    ).all()

    cancelled_bookings_count = 0

    for booking in bookings_to_cancel:
        match reason:
            case constants.SuspensionReason.FRAUD_SUSPICION:
                bookings_api.cancel_booking_for_fraud(booking)
                cancelled_bookings_count += 1

            case constants.SuspensionReason.UPON_USER_REQUEST:
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


def change_email(
    current_user: models.User,
    new_email: str,
    by_admin: bool = False,
) -> None:
    email_history = models.UserEmailHistory.build_validation(user=current_user, new_email=new_email, by_admin=by_admin)

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

    sessions = models.UserSession.query.filter_by(userId=current_user.id)
    repository.delete(*sessions)

    logger.info("User has changed their email", extra={"user": current_user.id})


def change_user_email(
    current_email: str,
    new_email: str,
    by_admin: bool = False,
) -> None:
    """
    Change a user's email and add a new (validation) entry to its email
    history.

    If no user if found, check whether a validated update request
    exists: if so, there is no need to panic nor to redo the update
    since it already has been done.

    Therefore this function can be called multiple times with the same
    inputs safely.
    """
    current_user = users_repository.find_user_by_email(current_email)

    if not current_user:
        if not email_update.validated_update_request_exists(current_email, new_email):
            raise exceptions.UserDoesNotExist()
    else:
        change_email(current_user, new_email, by_admin)


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


def update_password_and_external_user(user, new_password):  # type: ignore [no-untyped-def]
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
        user.phoneNumber = phone_number  # type: ignore [assignment]
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
    if id_piece_number is not UNCHANGED:
        if id_piece_number != user.idPieceNumber:
            snapshot.set("idPieceNumber", old=user.idPieceNumber, new=id_piece_number)
        user.idPieceNumber = id_piece_number

    repository.save(user)

    # TODO(prouzet) even for young users, we should probably remove contact with former email from sendinblue lists
    if old_email and user.has_pro_role:
        external_attributes_api.update_external_pro(old_email)
    external_attributes_api.update_external_user(user)

    return snapshot


def add_comment_to_user(user: models.User, author_user: models.User, comment: str) -> None:
    history_api.log_action(history_models.ActionType.COMMENT, author_user, user=user, comment=comment)


def get_domains_credit(
    user: models.User, user_bookings: list[bookings_models.Booking] = None
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
            remaining=max(user.deposit.amount - sum(booking.total_amount for booking in deposit_bookings), Decimal("0"))
            if user.has_active_deposit
            else Decimal("0"),
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


def create_pro_user_and_offerer(pro_user: ProUserCreationBodyModel) -> models.User:
    objects_to_save = []

    new_pro_user = create_pro_user(pro_user)

    existing_offerer = offerers_models.Offerer.query.filter_by(siren=pro_user.siren).one_or_none()
    is_new_offerer = False

    if existing_offerer:
        if existing_offerer.isRejected:
            existing_offerer = _generate_offerer(pro_user.dict(by_alias=True), existing_offerer=existing_offerer)
            user_offerer = offerers_api.grant_user_offerer_access(existing_offerer, new_pro_user)
            # When offerer was rejected, it is considered as a new offerer in validation process;
            # history is kept with same id and siren
            is_new_offerer = True
            comment = "Nouvelle demande sur un SIREN précédemment rejeté"
            objects_to_save += [existing_offerer]
        else:
            user_offerer = _generate_user_offerer_when_existing_offerer(new_pro_user, existing_offerer)
            objects_to_save += [
                history_api.log_action(
                    history_models.ActionType.USER_OFFERER_NEW,
                    new_pro_user,
                    user=new_pro_user,
                    offerer=existing_offerer,
                    save=False,
                    comment="Demande de rattachement à la création de compte pro",
                ),
            ]
        offerer = existing_offerer
    else:
        is_new_offerer = True
        offerer = _generate_offerer(pro_user.dict(by_alias=True))
        user_offerer = offerers_api.grant_user_offerer_access(offerer, new_pro_user)
        digital_venue = offerers_api.create_digital_venue(offerer)
        objects_to_save.extend([digital_venue, offerer, user_offerer])
        comment = None

    new_pro_user = _set_offerer_departement_code(new_pro_user, offerer)

    action = history_api.log_action(
        history_models.ActionType.USER_CREATED, author=new_pro_user, user=new_pro_user, offerer=offerer, save=False
    )
    objects_to_save.append(action)

    repository.save(new_pro_user, user_offerer, *objects_to_save)

    if is_new_offerer:
        try:
            siren_info = sirene.get_siren(offerer.siren)
        except sirene.SireneException as exc:
            logger.info("Could not fetch info from Sirene API", extra={"exc": exc})
            siren_info = None

        offerers_api.auto_tag_new_offerer(offerer, siren_info, new_pro_user)
        extra_data = {}
        if siren_info:
            extra_data = {"sirene_info": dict(siren_info)}

        history_api.log_action(
            history_models.ActionType.OFFERER_NEW,
            new_pro_user,
            user=new_pro_user,
            offerer=offerer,
            comment=comment,
            **extra_data,  # type: ignore [arg-type]
        )

    if not transactional_mails.send_email_validation_to_pro_email(new_pro_user):
        logger.warning(
            "Could not send validation email when creating pro user",
            extra={"user": new_pro_user.id},
        )

    external_attributes_api.update_external_pro(new_pro_user.email)

    return new_pro_user


def create_pro_user_V2(pro_user: ProUserCreationBodyV2Model) -> models.User:
    new_pro_user = create_pro_user(pro_user)

    action = history_api.log_action(
        history_models.ActionType.USER_CREATED, author=new_pro_user, user=new_pro_user, save=False
    )

    repository.save(new_pro_user, action)

    if not transactional_mails.send_email_validation_to_pro_email(new_pro_user):
        logger.warning(
            "Could not send validation email when creating pro user",
            extra={"user": new_pro_user.id},
        )

    external_attributes_api.update_external_pro(new_pro_user.email)
    return new_pro_user


def create_pro_user(pro_user: ProUserCreationBodyModel | ProUserCreationBodyV2Model) -> models.User:
    new_pro_user = models.User(from_dict=pro_user.dict(by_alias=True))
    new_pro_user.email = email_utils.sanitize_email(new_pro_user.email)
    new_pro_user.notificationSubscriptions = asdict(
        models.NotificationSubscriptions(marketing_email=pro_user.contact_ok)
    )
    new_pro_user.add_non_attached_pro_role()
    new_pro_user.remove_admin_role()
    new_pro_user.remove_beneficiary_role()
    new_pro_user.needsToFillCulturalSurvey = False
    new_pro_user.generate_validation_token()

    if hasattr(pro_user, "postal_code") and pro_user.postal_code:
        new_pro_user.departementCode = postal_code_utils.PostalCode(pro_user.postal_code).get_departement_code()

    if settings.IS_INTEGRATION:
        new_pro_user.add_beneficiary_role()
        new_pro_user.validatedBirthDate = new_pro_user.dateOfBirth
        deposit = finance_api.create_deposit(new_pro_user, "integration_signup", models.EligibilityType.AGE18)
        new_pro_user.deposits = [deposit]

    return new_pro_user


def _generate_user_offerer_when_existing_offerer(
    new_user: models.User, offerer: offerers_models.Offerer
) -> offerers_models.UserOfferer:
    user_offerer = offerers_api.grant_user_offerer_access(offerer, new_user)
    if not settings.IS_INTEGRATION:
        user_offerer.validationStatus = ValidationStatus.NEW
    return user_offerer


def _generate_offerer(data: dict, existing_offerer: offerers_models.Offerer | None = None) -> offerers_models.Offerer:
    if existing_offerer is not None:
        offerer = existing_offerer
    else:
        offerer = offerers_models.Offerer()
    offerer.populate_from_dict(data)

    # If offerer was rejected, it appears as deleted from the view. When registering again with the same SIREN, it
    # should look like it was created again, with up-to-date data, and start a new validation process.
    # So in any case, creation date is now:
    offerer.dateCreated = datetime.datetime.utcnow()

    if not settings.IS_INTEGRATION:
        offerer.validationStatus = ValidationStatus.NEW
    else:
        offerer.validationStatus = ValidationStatus.VALIDATED

    return offerer


def _set_offerer_departement_code(new_user: models.User, offerer: offerers_models.Offerer) -> models.User:
    if offerer.postalCode:  # not None, not ""
        new_user.departementCode = postal_code_utils.PostalCode(offerer.postalCode).get_departement_code()
    else:
        new_user.departementCode = None
    return new_user


def set_pro_tuto_as_seen(user: models.User) -> None:
    user.hasSeenProTutorials = True
    repository.save(user)


def set_pro_rgs_as_seen(user: models.User) -> None:
    user.hasSeenProRgs = True
    repository.save(user)


def update_last_connection_date(user):  # type: ignore [no-untyped-def]
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


def update_notification_subscription(
    user: models.User, subscriptions: "account_serialization.NotificationSubscriptions | None"
) -> None:
    if subscriptions is None:
        return

    user.notificationSubscriptions = {
        "marketing_push": subscriptions.marketing_push,
        "marketing_email": subscriptions.marketing_email,
    }

    repository.save(user)

    if not subscriptions.marketing_push:
        payload = batch_tasks.DeleteBatchUserAttributesRequest(user_id=user.id)
        batch_tasks.delete_user_attributes_task.delay(payload)


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

    if not date_of_birth or not (eligibility_start <= specified_datetime < eligibility_end):  # type: ignore [operator]
        return None

    age = users_utils.get_age_at_date(date_of_birth, specified_datetime)
    if not age:
        return None

    if age in constants.ELIGIBILITY_UNDERAGE_RANGE:
        return models.EligibilityType.UNDERAGE
    # If the user is older than 18 in UTC timezone, we consider them eligible until they reach eligibility_end
    if constants.ELIGIBILITY_AGE_18 <= age and specified_datetime < eligibility_end:  # type: ignore [operator]
        return models.EligibilityType.AGE18

    return None


def is_eligible_for_beneficiary_upgrade(user: models.User, eligibility: models.EligibilityType | None) -> bool:
    return (eligibility == models.EligibilityType.UNDERAGE and not user.has_underage_beneficiary_role) or (
        eligibility == models.EligibilityType.AGE18 and not user.has_beneficiary_role
    )


def is_user_age_compatible_with_eligibility(user_age: int | None, eligibility: models.EligibilityType | None) -> bool:
    if eligibility == models.EligibilityType.UNDERAGE:
        return user_age in constants.ELIGIBILITY_UNDERAGE_RANGE
    if eligibility == models.EligibilityType.AGE18:
        return user_age is not None and user_age >= constants.ELIGIBILITY_AGE_18
    return False


def _filter_user_accounts(accounts: BaseQuery, search_term: str, order_by: list[str] | None = None) -> BaseQuery:
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
        term_filters.append(models.User.phoneNumber == term_as_phone_number)  # type: ignore [arg-type]

    # numeric
    if search_term.isnumeric():
        term_filters.append(models.User.id == int(search_term))

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
                sa.func.unaccent(sa.func.concat(models.User.firstName, " ", models.User.lastName)).ilike(
                    f"%{clean_accents(name)}%"
                )
            )
        filters.append(sa.and_(*term_filters) if len(term_filters) > 1 else term_filters[0])

    else:
        filters.append(sa.or_(*term_filters) if len(term_filters) > 1 else term_filters[0])

    # each result must match all terms in any column
    accounts = accounts.filter(*filters).from_self()

    if order_by:
        try:
            accounts = accounts.order_by(*db_utils.get_ordering_clauses(models.User, order_by))
        except db_utils.BadSortError as err:
            raise ApiErrors({"sorting": str(err)})

    if name_term:
        name_term = name_term.lower()
        accounts = accounts.order_by(
            sa.func.levenshtein(
                sa.func.lower(sa.func.concat(models.User.firstName, " ", models.User.lastName)), name_term
            )
        )

    if not order_by:
        accounts = accounts.order_by(models.User.id)

    return accounts


def search_public_account(search_query: str, order_by: list[str] | None = None) -> BaseQuery:
    # There is no fully reliable condition to be sure that a user account is used as a public account (vs only pro).
    # In Flask-Admin backoffice, the difference was made from user_offerer table, which turns the user into a "pro"
    # account ; the same filter is kept here.
    # However, some young users, including beneficiaries, work for organizations and are associated with offerers
    # using the same email as their personal account. So let's include "pro" users who are beneficiaries (doesn't
    # include those who are only in the subscription process).
    public_accounts = (
        models.User.query.outerjoin(offerers_models.UserOfferer)
        .filter(
            sa.or_(
                offerers_models.UserOfferer.userId.is_(None),
                models.User.is_beneficiary.is_(True),  # type: ignore [attr-defined]
            )
        )
        .distinct(models.User.id)
    )
    return _filter_user_accounts(public_accounts, search_query, order_by=order_by)


def search_pro_account(search_query: str, order_by: list[str] | None = None) -> BaseQuery:
    # Any account which is associated with at least one offerer
    pro_accounts = models.User.query.join(offerers_models.UserOfferer).distinct(models.User.id)
    return _filter_user_accounts(pro_accounts, search_query, order_by=order_by)


def get_pro_account_base_query(pro_id: int) -> BaseQuery:
    return models.User.query.join(offerers_models.UserOfferer).filter(models.User.id == pro_id)


def skip_phone_validation_step(user: models.User) -> None:
    if user.phoneValidationStatus == models.PhoneValidationStatusType.VALIDATED:
        raise phone_validation_exceptions.UserPhoneNumberAlreadyValidated()

    user.phoneValidationStatus = models.PhoneValidationStatusType.SKIPPED_BY_SUPPORT.name
    repository.save(user)


def validate_pro_user_email(user: users_models.User, author_user: users_models.User | None = None) -> None:
    user.validationToken = None
    user.isEmailValidated = True
    if author_user:
        action = history_api.log_action(
            history_models.ActionType.USER_EMAIL_VALIDATED,
            author=author_user,
            user=user,
            save=False,
        )
        repository.save(user, action)
    else:
        repository.save(user)

    if not transactional_mails.send_welcome_to_pro_email(user):
        logger.warning(
            "Could not send welcome email when pro user is valid",
            extra={"user": user.id},
        )


def save_firebase_flags(user: models.User, firebase_value: dict) -> None:
    if user.pro_flags:
        if user.pro_flags.firebase and user.pro_flags.firebase != firebase_value:
            logger.warning("%s now has different Firebase flags than before", user)
        user.pro_flags.firebase = firebase_value
    else:
        user.pro_flags = users_models.UserProFlags(user=user, firebase=firebase_value)
    db.session.commit()


def save_flags(user: models.User, flags: dict) -> None:
    for flag, value in flags.items():
        match flag:
            case "firebase":
                save_firebase_flags(user, value)
            case _:
                raise ValueError()
