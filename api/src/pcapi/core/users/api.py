from contextlib import contextmanager
from dataclasses import asdict
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from decimal import Decimal
import logging
import secrets
import typing
from typing import Optional
from typing import Union

from dateutil.relativedelta import relativedelta
from flask import current_app as app
from flask_jwt_extended import create_access_token
from redis import Redis

from pcapi import settings
import pcapi.core.bookings.models as bookings_models
import pcapi.core.bookings.repository as bookings_repository
import pcapi.core.fraud.api as fraud_api
from pcapi.core.fraud.common import models as common_fraud_models
import pcapi.core.fraud.models as fraud_models
import pcapi.core.fraud.ubble.models as ubble_fraud_models
from pcapi.core.mails.transactional import users as user_emails
from pcapi.core.mails.transactional.pro.email_validation import send_email_validation_to_pro_email
from pcapi.core.mails.transactional.users.email_address_change_confirmation import send_email_confirmation_email
import pcapi.core.payments.api as payment_api
from pcapi.core.subscription import api as subscription_api
from pcapi.core.users import utils as users_utils
from pcapi.core.users.external import update_external_pro
from pcapi.core.users.external import update_external_user
from pcapi.core.users.models import Credit
from pcapi.core.users.models import DomainsCredit
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import NotificationSubscriptions
from pcapi.core.users.models import PhoneValidationStatusType
from pcapi.core.users.models import Token
from pcapi.core.users.models import TokenType
from pcapi.core.users.models import User
from pcapi.core.users.models import UserEmailHistory
from pcapi.core.users.models import VOID_PUBLIC_NAME
from pcapi.core.users.repository import does_validated_phone_exist
from pcapi.core.users.repository import find_user_by_email
from pcapi.domain.password import random_hashed_password
from pcapi.domain.postal_code.postal_code import PostalCode
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.models.user_offerer import UserOfferer
from pcapi.models.user_session import UserSession
from pcapi.notifications.sms import send_transactional_sms
from pcapi.notifications.sms.sending_limit import is_SMS_sending_allowed
from pcapi.notifications.sms.sending_limit import update_sent_SMS_counter
from pcapi.repository import repository
from pcapi.routes.serialization.users import ProUserCreationBodyModel
from pcapi.tasks import batch_tasks
from pcapi.utils import phone_number as phone_number_utils

from . import constants
from . import exceptions
from . import models
from ..offerers.api import create_digital_venue
from ..offerers.models import Offerer


if typing.TYPE_CHECKING:
    from pcapi.routes.native.v1.serialization import account as account_serialization


UNCHANGED = object()
logger = logging.getLogger(__name__)


def create_email_validation_token(user: User) -> Token:
    return generate_and_save_token(
        user, TokenType.EMAIL_VALIDATION, life_time=constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME
    )


def create_reset_password_token(user: User, token_life_time: timedelta = None) -> Token:
    return generate_and_save_token(
        user, TokenType.RESET_PASSWORD, life_time=token_life_time or constants.RESET_PASSWORD_TOKEN_LIFE_TIME
    )


def create_phone_validation_token(user: User) -> Optional[Token]:
    secret_code = "{:06}".format(secrets.randbelow(1_000_000))  # 6 digits
    return generate_and_save_token(
        user,
        token_type=TokenType.PHONE_VALIDATION,
        life_time=constants.PHONE_VALIDATION_TOKEN_LIFE_TIME,
        token_value=secret_code,
    )


def generate_and_save_token(
    user: User, token_type: TokenType, life_time: Optional[timedelta] = None, token_value: Optional[str] = None
) -> Token:
    assert token_type.name in TokenType.__members__, "Only registered token types are allowed"

    expiration_date = datetime.now() + life_time if life_time else None

    if settings.IS_PERFORMANCE_TESTS:
        token_value = f"performance-tests_{token_type.value}_{user.id}"
    else:
        token_value = token_value or secrets.token_urlsafe(32)

    token = Token(user=user, value=token_value, type=token_type, expirationDate=expiration_date)
    repository.save(token)

    return token


def delete_expired_tokens() -> None:
    Token.query.filter(Token.expirationDate < datetime.now()).delete()


def delete_all_users_tokens(user: User) -> None:
    Token.query.filter(Token.user == user).delete()


def create_account(
    email: str,
    password: str,
    birthdate: date,
    marketing_email_subscription: bool = False,
    is_email_validated: bool = False,
    send_activation_mail: bool = True,
    remote_updates: bool = True,
    phone_number: str = None,
    apps_flyer_user_id: str = None,
    apps_flyer_platform: str = None,
) -> User:
    email = users_utils.sanitize_email(email)
    if find_user_by_email(email):
        raise exceptions.UserAlreadyExistsException()

    user = User(
        email=email,
        dateOfBirth=datetime.combine(birthdate, datetime.min.time()),
        isEmailValidated=is_email_validated,
        publicName=VOID_PUBLIC_NAME,  # Required because model validation requires 3+ chars
        hasSeenTutorials=False,
        notificationSubscriptions=asdict(NotificationSubscriptions(marketing_email=marketing_email_subscription)),
        phoneNumber=phone_number,
        lastConnectionDate=datetime.now(),
        subscriptionState=models.SubscriptionState.account_created,
    )

    if not user.age or user.age < constants.ACCOUNT_CREATION_MINIMUM_AGE:
        raise exceptions.UnderAgeUserException()

    return initialize_account(
        user, password, apps_flyer_user_id, apps_flyer_platform, send_activation_mail, remote_updates
    )


def initialize_account(
    user: User,
    password: str,
    apps_flyer_user_id: str = None,
    apps_flyer_platform: str = None,
    send_activation_mail: bool = True,
    remote_updates: bool = True,
) -> User:

    user.setPassword(password)
    if apps_flyer_user_id and apps_flyer_platform:
        if user.externalIds is None:
            user.externalIds = {}
        user.externalIds["apps_flyer"] = {"user": apps_flyer_user_id, "platform": apps_flyer_platform.upper()}

    repository.save(user)
    logger.info("Created user account", extra={"user": user.id})
    delete_all_users_tokens(user)

    if remote_updates:
        update_external_user(user)

    if not user.isEmailValidated and send_activation_mail:
        request_email_confirmation(user)

    return user


def validate_phone_number_and_activate_user(user: User, code: str) -> User:
    validate_phone_number(user, code)

    subscription_api.activate_beneficiary_if_no_missing_step(user)


def update_user_information_from_external_source(
    user: User,
    data: common_fraud_models.IdentityCheckContent,
    commit=False,
) -> User:
    if isinstance(data, fraud_models.DMSContent):
        user.lastName = data.last_name
        user.firstName = data.first_name
        user.publicName = "%s %s" % (data.first_name, data.last_name)
        user.departementCode = data.department
        user.postalCode = data.postal_code
        user.address = data.address
        user.civility = data.civility
        user.activity = data.activity
        user.remove_admin_role()
        user.hasSeenTutorials = False
        user.idPieceNumber = data.id_piece_number
        if data.birth_date:
            user.dateOfBirth = datetime.combine(data.birth_date, time(0, 0))
        if not user.phoneNumber:
            user.phoneNumber = data.phone

    elif isinstance(data, fraud_models.JouveContent):
        if data.activity:
            user.activity = data.activity
        if data.address:
            user.address = data.address
        if data.city:
            user.city = data.city
        if data.gender:
            user.civility = "Mme" if data.gender == "F" else "M."
        if data.birthDateTxt:
            user.dateOfBirth = data.birthDateTxt
        if data.firstName:
            user.firstName = data.firstName
        if data.lastName:
            user.lastName = data.lastName
        if data.postalCode and not user.postalCode:
            user.postalCode = data.postalCode
            user.departementCode = PostalCode(data.postalCode).get_departement_code()
        if data.firstName and data.lastName:
            user.publicName = f"{user.firstName} {user.lastName}"

        if data.bodyPieceNumber:
            items = (
                fraud_api.validate_id_piece_number_format_fraud_item(data.get_id_piece_number()),
                fraud_api.duplicate_id_piece_number_fraud_item(user, data.get_id_piece_number()),
            )
            if all((item.status == fraud_models.FraudStatus.OK) for item in items):
                user.idPieceNumber = data.bodyPieceNumber

        if not FeatureToggle.ENABLE_PHONE_VALIDATION.is_active():
            if not user.phoneNumber and data.phoneNumber:
                user.phoneNumber = data.phoneNumber

    elif isinstance(data, fraud_models.EduconnectContent):
        user.firstName = data.first_name
        user.lastName = data.last_name
        user.dateOfBirth = datetime.combine(data.birth_date, time(0, 0))
        user.ineHash = data.ine_hash

    elif isinstance(data, ubble_fraud_models.UbbleContent):
        user.firstName = data.first_name
        user.lastName = data.last_name
        user.dateOfBirth = datetime.combine(data.birth_date, time(0, 0))
        user.idPieceNumber = data.get_id_piece_number()
        user.gender = data.gender
        user.married_name = data.married_name

    # update user fields to be correctly initialized
    user.hasSeenTutorials = False
    user.remove_admin_role()

    db.session.add(user)
    db.session.flush()
    if commit:
        db.session.commit()
    return user


def request_email_confirmation(user: User) -> None:
    token = create_email_validation_token(user)
    send_email_confirmation_email(user, token=token)


def request_password_reset(user: User) -> None:
    if not user or not user.isActive:
        return

    is_email_sent = user_emails.send_reset_password_email_to_native_app_user(user)

    if not is_email_sent:
        logger.error("Email service failure when user requested password reset for email '%s'", user.email)
        raise exceptions.EmailNotSent()


def fulfill_account_password(user: User) -> User:
    _generate_random_password(user)
    return user


def fulfill_beneficiary_data(user: User, deposit_source: str, deposit_version: int = None) -> User:
    _generate_random_password(user)

    deposit = payment_api.create_deposit(user, deposit_source, version=deposit_version)
    user.deposits = [deposit]

    return user


def _generate_random_password(user):
    user.password = random_hashed_password()


def suspend_account(user: User, reason: constants.SuspensionReason, actor: User) -> dict[str, int]:
    import pcapi.core.bookings.api as bookings_api  # avoid import loop

    user.isActive = False
    user_suspension = models.UserSuspension(
        user=user,
        eventType=models.SuspensionEventType.SUSPENDED,
        actorUser=actor,
        reasonCode=reason,
    )
    user.remove_admin_role()
    user.setPassword(secrets.token_urlsafe(30))
    repository.save(user)
    repository.save(user_suspension)

    sessions = UserSession.query.filter_by(userId=user.id)
    repository.delete(*sessions)

    n_bookings = 0

    # Cancel all bookings of the related offerer if the suspended
    # account was the last active offerer's account.
    if reason == constants.SuspensionReason.FRAUD_SUSPICION:
        for offerer in user.offerers:
            if any(u.isActive and u != user for u in offerer.users):
                continue
            bookings = bookings_repository.find_cancellable_bookings_by_offerer(offerer.id)
            for booking in bookings:
                bookings_api.cancel_booking_for_fraud(booking)
                n_bookings += 1

    # Cancel all bookings of the user (the following works even if the
    # user is not a beneficiary).
    cancel_booking_callback = {
        constants.SuspensionReason.FRAUD_SUSPICION: bookings_api.cancel_booking_for_fraud,
        constants.SuspensionReason.UPON_USER_REQUEST: bookings_api.cancel_booking_on_user_requested_account_suspension,
    }.get(reason)
    if cancel_booking_callback:
        for booking in bookings_repository.find_cancellable_bookings_by_beneficiaries([user]):
            cancel_booking_callback(booking)
            n_bookings += 1

    logger.info(
        "Account has been suspended",
        extra={
            "actor": actor.id,
            "user": user.id,
            "reason": str(reason),
        },
    )
    return {"cancelled_bookings": n_bookings}


def unsuspend_account(user: User, actor: User) -> None:
    user.isActive = True
    user_suspension = models.UserSuspension(
        user=user,
        eventType=models.SuspensionEventType.UNSUSPENDED,
        actorUser=actor,
    )
    repository.save(user)
    repository.save(user_suspension)

    logger.info(
        "Account has been unsuspended",
        extra={
            "actor": actor.id,
            "user": user.id,
        },
    )


def bulk_unsuspend_account(user_ids: list[int], actor: User) -> None:
    User.query.filter(User.id.in_(user_ids)).update(
        values={"isActive": True},
        synchronize_session=False,
    )
    for user_id in user_ids:
        db.session.add(
            models.UserSuspension(
                userId=user_id,
                eventType=models.SuspensionEventType.UNSUSPENDED,
                actorUser=actor,
            )
        )
    db.session.commit()

    logger.info(
        "Some accounts have been reactivated",
        extra={
            "actor": actor.id,
            "users": user_ids,
        },
    )


def change_user_email(
    current_email: str,
    new_email: str,
    admin: bool = False,
) -> None:
    current_user = find_user_by_email(current_email)

    if not current_user:
        raise exceptions.UserDoesNotExist()

    email_history = UserEmailHistory.build_validation(user=current_user, new_email=new_email, admin=admin)

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

    sessions = UserSession.query.filter_by(userId=current_user.id)
    repository.delete(*sessions)

    logger.info("User has changed their email", extra={"user": current_user.id})


def update_user_password(user: User, new_password: str) -> None:
    user.setPassword(new_password)
    repository.save(user)


def update_password_and_external_user(user, new_password):
    user.setPassword(new_password)
    if not user.isEmailValidated:
        user.isEmailValidated = True
        update_external_user(user)
    repository.save(user)


def update_user_info(
    user,
    cultural_survey_filled_date=UNCHANGED,
    cultural_survey_id=UNCHANGED,
    email=UNCHANGED,
    first_name=UNCHANGED,
    has_seen_tutorials=UNCHANGED,
    last_name=UNCHANGED,
    needs_to_fill_cultural_survey=UNCHANGED,
    phone_number=UNCHANGED,
    public_name=UNCHANGED,
):
    old_email = None

    if cultural_survey_filled_date is not UNCHANGED:
        user.culturalSurveyFilledDate = cultural_survey_filled_date
    if cultural_survey_id is not UNCHANGED:
        user.culturalSurveyId = cultural_survey_id
    if email is not UNCHANGED:
        old_email = user.email
        user.email = users_utils.sanitize_email(email)
    if first_name is not UNCHANGED:
        user.firstName = first_name
    if has_seen_tutorials is not UNCHANGED:
        user.hasSeenTutorials = has_seen_tutorials
    if last_name is not UNCHANGED:
        user.lastName = last_name
    if needs_to_fill_cultural_survey is not UNCHANGED:
        user.needsToFillCulturalSurvey = needs_to_fill_cultural_survey
    if phone_number is not UNCHANGED:
        user.phoneNumber = phone_number
    if public_name is not UNCHANGED:
        user.publicName = public_name
    repository.save(user)

    # TODO(prouzet) even for young users, we should probbaly remove contact with former email from sendinblue lists
    if old_email and user.has_pro_role:
        update_external_pro(old_email)
    update_external_user(user)


def get_domains_credit(user: User, user_bookings: list[bookings_models.Booking] = None) -> Optional[DomainsCredit]:
    if not user.deposit:
        return None

    if user_bookings is None:
        deposit_bookings = bookings_repository.get_bookings_from_deposit(user.deposit.id)
    else:
        deposit_bookings = [
            booking
            for booking in user_bookings
            if booking.individualBooking is not None
            and booking.individualBooking.depositId == user.deposit.id
            and booking.status != bookings_models.BookingStatus.CANCELLED
        ]

    domains_credit = DomainsCredit(
        all=Credit(
            initial=user.deposit.amount,
            remaining=max(user.deposit.amount - sum(booking.total_amount for booking in deposit_bookings), Decimal("0"))
            if user.has_active_deposit
            else Decimal("0"),
        )
    )
    specific_caps = user.deposit.specific_caps

    if specific_caps.DIGITAL_CAP:
        digital_bookings_total = sum(
            [
                booking.total_amount
                for booking in deposit_bookings
                if specific_caps.digital_cap_applies(booking.stock.offer)
            ]
        )
        domains_credit.digital = Credit(
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
            [
                booking.total_amount
                for booking in deposit_bookings
                if specific_caps.physical_cap_applies(booking.stock.offer)
            ]
        )
        domains_credit.physical = Credit(
            initial=specific_caps.PHYSICAL_CAP,
            remaining=(
                min(
                    max(specific_caps.PHYSICAL_CAP - physical_bookings_total, Decimal("0")),
                    domains_credit.all.remaining,
                )
            ),
        )

    return domains_credit


def create_pro_user_and_offerer(pro_user: ProUserCreationBodyModel) -> User:
    objects_to_save = []

    new_pro_user = create_pro_user(pro_user)

    existing_offerer = Offerer.query.filter_by(siren=pro_user.siren).one_or_none()

    if existing_offerer:
        user_offerer = _generate_user_offerer_when_existing_offerer(new_pro_user, existing_offerer)
        offerer = existing_offerer
    else:
        offerer = _generate_offerer(pro_user.dict(by_alias=True))
        user_offerer = offerer.grant_access(new_pro_user)
        digital_venue = create_digital_venue(offerer)
        objects_to_save.extend([digital_venue, offerer])
    objects_to_save.append(user_offerer)
    new_pro_user = _set_offerer_departement_code(new_pro_user, offerer)

    objects_to_save.append(new_pro_user)

    repository.save(*objects_to_save)

    if not send_email_validation_to_pro_email(new_pro_user):
        logger.warning(
            "Could not send validation email when creating pro user",
            extra={"user": new_pro_user.id},
        )

    update_external_pro(new_pro_user.email)

    return new_pro_user


def create_pro_user(pro_user: ProUserCreationBodyModel) -> User:
    new_pro_user = User(from_dict=pro_user.dict(by_alias=True))
    new_pro_user.email = users_utils.sanitize_email(new_pro_user.email)
    new_pro_user.notificationSubscriptions = asdict(NotificationSubscriptions(marketing_email=pro_user.contact_ok))
    new_pro_user.remove_admin_role()
    new_pro_user.remove_beneficiary_role()
    new_pro_user.needsToFillCulturalSurvey = False
    new_pro_user.generate_validation_token()

    if pro_user.postal_code:
        new_pro_user.departementCode = PostalCode(pro_user.postal_code).get_departement_code()

    if settings.IS_INTEGRATION:
        new_pro_user.add_beneficiary_role()
        deposit = payment_api.create_deposit(new_pro_user, "integration_signup")
        new_pro_user.deposits = [deposit]

    return new_pro_user


def _generate_user_offerer_when_existing_offerer(new_user: User, offerer: Offerer) -> UserOfferer:
    user_offerer = offerer.grant_access(new_user)
    if not settings.IS_INTEGRATION:
        user_offerer.generate_validation_token()
    return user_offerer


def _generate_offerer(data: dict) -> Offerer:
    offerer = Offerer()
    offerer.populate_from_dict(data)

    if not settings.IS_INTEGRATION:
        offerer.generate_validation_token()
    return offerer


def _set_offerer_departement_code(new_user: User, offerer: Offerer) -> User:
    if offerer.postalCode is not None:
        new_user.departementCode = PostalCode(offerer.postalCode).get_departement_code()
    else:
        new_user.departementCode = None
    return new_user


def set_pro_tuto_as_seen(user: User) -> None:
    user.hasSeenProTutorials = True
    repository.save(user)


def change_user_phone_number(user: User, phone_number: str) -> None:
    _check_phone_number_validation_is_authorized(user)

    phone_data = phone_number_utils.ParsedPhoneNumber(phone_number)
    with fraud_manager(user=user, phone_number=phone_data.phone_number):
        check_phone_number_is_legit(phone_data.phone_number, phone_data.country_code)
        check_phone_number_not_used(phone_data.phone_number)

    user.phoneNumber = phone_data.phone_number
    Token.query.filter(Token.user == user, Token.type == TokenType.PHONE_VALIDATION).delete()
    repository.save(user)


def send_phone_validation_code(user: User) -> None:
    _check_phone_number_validation_is_authorized(user)

    phone_data = phone_number_utils.ParsedPhoneNumber(user.phoneNumber)
    with fraud_manager(user=user, phone_number=phone_data.phone_number):
        check_phone_number_is_legit(phone_data.phone_number, phone_data.country_code)
        check_phone_number_not_used(phone_data.phone_number)
        check_sms_sending_is_allowed(user)

    phone_validation_token = create_phone_validation_token(user)
    content = f"{phone_validation_token.value} est ton code de confirmation pass Culture"

    if not send_transactional_sms(phone_data.phone_number, content):
        raise exceptions.PhoneVerificationCodeSendingException()

    update_sent_SMS_counter(app.redis_client, user)


def validate_phone_number(user: User, code: str) -> None:
    _check_phone_number_validation_is_authorized(user)

    phone_data = phone_number_utils.ParsedPhoneNumber(user.phoneNumber)
    with fraud_manager(user=user, phone_number=phone_data.phone_number):
        check_phone_number_is_legit(phone_data.phone_number, phone_data.country_code)
        check_and_update_phone_validation_attempts(app.redis_client, user)

    token = Token.query.filter(
        Token.user == user, Token.value == code, Token.type == TokenType.PHONE_VALIDATION
    ).one_or_none()

    if not token:
        raise exceptions.NotValidCode()

    if token.expirationDate and token.expirationDate < datetime.now():
        raise exceptions.ExpiredCode()

    db.session.delete(token)

    # not wrapped inside a fraud_manager because we don't need to add any fraud
    # log in case this check raises an exception at this point
    check_phone_number_not_used(phone_data.phone_number)

    user.phoneValidationStatus = PhoneValidationStatusType.VALIDATED
    user.validate_phone()
    repository.save(user)


def check_phone_number_is_legit(phone_number: str, country_code: str) -> None:
    if phone_number in settings.BLACKLISTED_SMS_RECIPIENTS:
        raise exceptions.BlacklistedPhoneNumber(phone_number)

    if country_code not in constants.WHITELISTED_COUNTRY_PHONE_CODES:
        raise exceptions.InvalidCountryCode(country_code)


def _check_phone_number_validation_is_authorized(user: User) -> None:
    if user.is_phone_validated:
        raise exceptions.UserPhoneNumberAlreadyValidated()

    if not user.isEmailValidated:
        raise exceptions.UnvalidatedEmail()

    if user.has_beneficiary_role:
        raise exceptions.UserAlreadyBeneficiary()


def check_and_update_phone_validation_attempts(redis: Redis, user: User) -> None:
    phone_validation_attempts_key = f"phone_validation_attempts_user_{user.id}"
    phone_validation_attempts = redis.get(phone_validation_attempts_key)

    if phone_validation_attempts and int(phone_validation_attempts) >= settings.MAX_PHONE_VALIDATION_ATTEMPTS:
        logger.warning(
            "Phone number validation limit reached for user with id=%s",
            user.id,
            extra={"attempts_count": int(phone_validation_attempts)},
        )
        raise exceptions.PhoneValidationAttemptsLimitReached(int(phone_validation_attempts))

    count = redis.incr(phone_validation_attempts_key)
    if count == 1:
        redis.expire(phone_validation_attempts_key, settings.PHONE_VALIDATION_ATTEMPTS_TTL)


def check_phone_number_not_used(phone_number: str) -> None:
    if does_validated_phone_exist(phone_number):
        raise exceptions.PhoneAlreadyExists(phone_number)


def check_sms_sending_is_allowed(user: User) -> None:
    if not is_SMS_sending_allowed(app.redis_client, user):
        raise exceptions.SMSSendingLimitReached()


@contextmanager
def fraud_manager(user: User, phone_number: str) -> typing.Generator:
    try:
        yield
    except exceptions.BlacklistedPhoneNumber:
        fraud_api.handle_blacklisted_sms_recipient(user, phone_number)
        user.validate_phone_failed()
        repository.save(user)
        raise
    except exceptions.PhoneAlreadyExists:
        fraud_api.handle_phone_already_exists(user, phone_number)
        user.validate_phone_failed()
        repository.save(user)
        raise
    except exceptions.SMSSendingLimitReached:
        fraud_api.handle_sms_sending_limit_reached(user)
        user.validate_phone_failed()
        repository.save(user)
        raise
    except exceptions.PhoneValidationAttemptsLimitReached as error:
        fraud_api.handle_phone_validation_attempts_limit_reached(user, error.attempts)
        user.validate_phone_failed()
        repository.save(user)
        raise


def update_last_connection_date(user):
    previous_connection_date = user.lastConnectionDate
    last_connection_date = datetime.utcnow()

    should_save_last_connection_date = (
        not previous_connection_date or last_connection_date - previous_connection_date > timedelta(minutes=15)
    )
    should_update_sendinblue_last_connection_date = should_save_last_connection_date and (
        not previous_connection_date
        or last_connection_date.date() - previous_connection_date.date() >= timedelta(days=1)
    )

    if should_save_last_connection_date:
        user.lastConnectionDate = last_connection_date
        repository.save(user)

    if should_update_sendinblue_last_connection_date:
        update_external_user(user, skip_batch=True)


def create_user_access_token(user: User) -> str:
    return create_access_token(identity=user.email, additional_claims={"user_claims": {"user_id": user.id}})


def update_notification_subscription(
    user: User, subscriptions: "typing.Optional[account_serialization.NotificationSubscriptions]"
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


def reset_recredit_amount_to_show(user: User) -> None:
    user.recreditAmountToShow = None
    repository.save(user)


def get_eligibility_end_datetime(date_of_birth: Optional[Union[date, datetime]]) -> Optional[datetime]:
    if not date_of_birth:
        return None

    return datetime.combine(date_of_birth, time(0, 0)) + relativedelta(years=constants.ELIGIBILITY_AGE_18 + 1, hour=11)


def get_eligibility_start_datetime(date_of_birth: Optional[Union[date, datetime]]) -> Optional[datetime]:
    if not date_of_birth:
        return None

    date_of_birth = datetime.combine(date_of_birth, time(0, 0))
    fifteenth_birthday = date_of_birth + relativedelta(years=constants.ELIGIBILITY_UNDERAGE_RANGE[0])

    return fifteenth_birthday


def get_eligibility_at_date(
    date_of_birth: Optional[Union[date, datetime]], specified_datetime: datetime
) -> Optional[EligibilityType]:
    eligibility_start = get_eligibility_start_datetime(date_of_birth)
    eligibility_end = get_eligibility_end_datetime(date_of_birth)

    if not date_of_birth or not (eligibility_start <= specified_datetime < eligibility_end):
        return None

    age = users_utils.get_age_at_date(date_of_birth, specified_datetime)
    if not age:
        return None

    if age in constants.ELIGIBILITY_UNDERAGE_RANGE:
        return EligibilityType.UNDERAGE
    # If the user is older than 18 in UTC timezone, we consider them eligible until they reach eligibility_end
    if constants.ELIGIBILITY_AGE_18 <= age and specified_datetime < eligibility_end:
        return EligibilityType.AGE18

    return None


# TODO: add checks based on the age of the user
def is_eligible_for_beneficiary_upgrade(user: models.User, eligibility: Optional[EligibilityType]) -> bool:
    return (eligibility == EligibilityType.UNDERAGE and not user.has_underage_beneficiary_role) or (
        eligibility == EligibilityType.AGE18 and not user.has_beneficiary_role
    )


def get_activable_identity_fraud_check(user: User) -> typing.Optional[fraud_models.BeneficiaryFraudCheck]:
    """Finds first created activable identity fraud check for a user.

    Args:
        user (User): user to find activable identity fraud check for.

    Returns:
        BeneficiaryFraudCheck: activable identity fraud check for a user.
    """
    user_identity_fraud_checks = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.status == fraud_models.FraudCheckStatus.OK
        and fraud_check.type in fraud_models.IDENTITY_CHECK_TYPES
        and is_eligible_for_beneficiary_upgrade(user, fraud_check.eligibilityType)
        and not (
            fraud_check.eligibilityType == EligibilityType.UNDERAGE and user.age >= constants.ELIGIBILITY_AGE_18
        )  # TODO: put this condition inside is_eligible_for_beneficiary_upgrade
    ]
    if not user_identity_fraud_checks:
        return None

    return sorted(user_identity_fraud_checks, key=lambda fraud_check: fraud_check.dateCreated, reverse=True)[0]


def get_user_age_at_registration(user: User) -> Optional[int]:
    fraud_check = get_activable_identity_fraud_check(user)
    if not fraud_check:
        return None
    registration_datetime = fraud_check.source_data().get_registration_datetime()
    if registration_datetime is None:
        return None
    return users_utils.get_age_at_date(user.dateOfBirth, registration_datetime)
