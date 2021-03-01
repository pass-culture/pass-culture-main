from dataclasses import asdict
from datetime import date
from datetime import datetime
from datetime import timedelta
import secrets
from typing import Optional

from jwt import DecodeError
from jwt import ExpiredSignatureError
from jwt import InvalidSignatureError
from jwt import InvalidTokenError

from pcapi import settings
from pcapi.core import mails
from pcapi.core.bookings.conf import LIMIT_CONFIGURATIONS
from pcapi.core.payments import api as payment_api
from pcapi.core.users.models import Expense
from pcapi.core.users.models import ExpenseDomain
from pcapi.core.users.models import NotificationSubscriptions
from pcapi.core.users.models import Token
from pcapi.core.users.models import TokenType
from pcapi.core.users.models import User
from pcapi.core.users.models import VOID_FIRST_NAME
from pcapi.core.users.models import VOID_PUBLIC_NAME
from pcapi.core.users.utils import create_custom_jwt_token
from pcapi.core.users.utils import decode_jwt_token
from pcapi.core.users.utils import encode_jwt_payload
from pcapi.core.users.utils import format_email
from pcapi.domain import user_emails
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription import BeneficiaryPreSubscription
from pcapi.domain.password import generate_reset_token
from pcapi.domain.password import random_password
from pcapi.domain.postal_code.postal_code import PostalCode
from pcapi.emails.beneficiary_email_change import build_beneficiary_confirmation_email_change_data
from pcapi.emails.beneficiary_email_change import build_beneficiary_information_email_change_data
from pcapi.models import BeneficiaryImport
from pcapi.models import ImportStatus
from pcapi.models.db import db
from pcapi.models.offerer import Offerer
from pcapi.models.user_offerer import UserOfferer
from pcapi.models.user_session import UserSession
from pcapi.repository import repository
from pcapi.repository.user_queries import find_user_by_email
from pcapi.routes.serialization.users import ProUserCreationBodyModel
from pcapi.scripts.beneficiary import THIRTY_DAYS_IN_HOURS
from pcapi.utils.logger import logger
from pcapi.utils.mailing import MailServiceException

from . import constants
from . import exceptions
from ..offerers.api import create_digital_venue


def create_email_validation_token(user: User) -> Token:
    return generate_and_save_token(
        user, TokenType.EMAIL_VALIDATION, life_time=constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME
    )


def create_reset_password_token(user: User) -> Token:
    return generate_and_save_token(user, TokenType.RESET_PASSWORD, life_time=constants.RESET_PASSWORD_TOKEN_LIFE_TIME)


def create_id_check_token(user: User) -> Optional[Token]:
    if not user.is_eligible:
        return None

    return generate_and_save_token(user, TokenType.ID_CHECK, constants.ID_CHECK_TOKEN_LIFE_TIME)


def generate_and_save_token(user: User, token_type: TokenType, life_time: Optional[timedelta] = None) -> Token:
    expiration_date = datetime.now() + life_time if life_time else None
    token_value = create_custom_jwt_token(user.id, token_type.value, expiration_date)

    token_with_same_value = Token.query.filter_by(value=token_value).first()
    if token_with_same_value:
        return token_with_same_value

    token = Token(userId=user.id, value=token_value, type=token_type, expirationDate=expiration_date)
    repository.save(token)

    return token


def delete_expired_tokens() -> None:
    Token.query.filter(Token.expirationDate < datetime.now()).delete()


def create_account(
    email: str,
    password: str,
    birthdate: date,
    marketing_email_subscription: bool = False,
    is_email_validated: bool = False,
    send_activation_mail: bool = True,
) -> User:
    if find_user_by_email(email):
        raise exceptions.UserAlreadyExistsException()

    user = User(
        email=format_email(email),
        dateOfBirth=datetime.combine(birthdate, datetime.min.time()),
        isEmailValidated=is_email_validated,
        departementCode="007",
        publicName=VOID_PUBLIC_NAME,  # Required because model validation requires 3+ chars
        hasSeenTutorials=False,
        firstName=VOID_FIRST_NAME,
        notificationSubscriptions=asdict(NotificationSubscriptions(marketing_email=marketing_email_subscription)),
    )

    age = user.calculate_age()
    if not age or age < constants.ACCOUNT_CREATION_MINIMUM_AGE:
        raise exceptions.UnderAgeUserException()

    user.setPassword(password)
    repository.save(user)

    if not is_email_validated and send_activation_mail:
        request_email_confirmation(user)
    return user


def activate_beneficiary(user: User, deposit_source: str) -> User:
    user.isBeneficiary = True
    deposit = payment_api.create_deposit(user, deposit_source=deposit_source)
    db.session.add_all((user, deposit))
    db.session.commit()
    return user


def attach_beneficiary_import_details(
    beneficiary: User, beneficiary_pre_subscription: BeneficiaryPreSubscription
) -> None:
    beneficiary_import = BeneficiaryImport()

    beneficiary_import.applicationId = beneficiary_pre_subscription.application_id
    beneficiary_import.sourceId = beneficiary_pre_subscription.source_id
    beneficiary_import.source = beneficiary_pre_subscription.source
    beneficiary_import.setStatus(status=ImportStatus.CREATED)

    beneficiary.beneficiaryImports = [beneficiary_import]


def request_email_confirmation(user: User) -> None:
    token = create_email_validation_token(user)
    user_emails.send_activation_email(user, native_version=True, token=token)


def request_password_reset(user: User) -> None:
    if not user or not user.isActive:
        return

    reset_password_token = create_reset_password_token(user)

    is_email_sent = user_emails.send_reset_password_email_to_native_app_user(
        user.email, reset_password_token.value, reset_password_token.expirationDate
    )

    if not is_email_sent:
        logger.error("Email service failure when user requested password reset for email '%s'", user.email)
        raise exceptions.EmailNotSent()


def fulfill_user_data(user: User, deposit_source: str, deposit_version: int = None) -> User:
    user.password = random_password()
    generate_reset_token(user, validity_duration_hours=THIRTY_DAYS_IN_HOURS)

    deposit = payment_api.create_deposit(user, deposit_source, version=deposit_version)
    user.deposits = [deposit]

    return user


def suspend_account(user: User, reason: constants.SuspensionReason, actor: User) -> None:
    user.isActive = False
    user.suspensionReason = str(reason)
    # If we ever unsuspend the account, we'll have to explictly enable
    # isAdmin again. An admin now may not be an admin later.
    user.isAdmin = False
    user.setPassword(secrets.token_urlsafe(30))
    repository.save(user)

    sessions = UserSession.query.filter_by(userId=user.id)
    repository.delete(*sessions)

    logger.info("user=%s has been suspended by actor=%s for reason=%s", user.id, actor.id, reason)


def unsuspend_account(user: User, actor: User) -> None:
    user.isActive = True
    user.suspensionReason = ""
    repository.save(user)

    logger.info("user=%s has been unsuspended by actor=%s", user.id, actor.id)


def send_user_emails_for_email_change(user: User, new_email: str) -> None:
    user_with_new_email = User.query.filter_by(email=new_email).first()
    if user_with_new_email:
        return

    information_data = build_beneficiary_information_email_change_data(user.firstName)
    information_sucessfully_sent = mails.send(recipients=[user.email], data=information_data)
    if not information_sucessfully_sent:
        raise MailServiceException()

    link_for_email_change = _build_link_for_email_change(user.email, new_email)
    confirmation_data = build_beneficiary_confirmation_email_change_data(
        user.firstName,
        link_for_email_change,
    )
    confirmation_sucessfully_sent = mails.send(recipients=[new_email], data=confirmation_data)
    if not confirmation_sucessfully_sent:
        raise MailServiceException()

    return


def change_user_email(token: str) -> None:
    try:
        jwt_payload = decode_jwt_token(token)
    except (
        ExpiredSignatureError,
        InvalidSignatureError,
        DecodeError,
        InvalidTokenError,
    ) as error:
        raise InvalidTokenError() from error

    if not {"exp", "new_email", "current_email"} <= set(jwt_payload):
        raise InvalidTokenError()

    new_email = jwt_payload["new_email"]
    if User.query.filter_by(email=new_email).first():
        return

    current_email = jwt_payload["current_email"]
    current_user = User.query.filter_by(email=current_email).first()
    if not current_user:
        return

    current_user.email = new_email
    sessions = UserSession.query.filter_by(userId=current_user.id)
    repository.delete(*sessions)
    repository.save(current_user)

    return


def _build_link_for_email_change(current_email: str, new_email: str) -> str:
    expiration_date = datetime.now() + constants.EMAIL_CHANGE_TOKEN_LIFE_TIME
    token = encode_jwt_payload(dict(current_email=current_email, new_email=new_email), expiration_date)

    return (
        f"{settings.WEBAPP_URL}/changement-email?token={token}&expiration_timestamp={int(expiration_date.timestamp())}"
    )


def user_expenses(user: User):
    version = user.deposit_version

    if not version:
        return []

    bookings = user.get_not_cancelled_bookings()
    config = LIMIT_CONFIGURATIONS[version]

    limits = [
        Expense(
            domain=ExpenseDomain.ALL,
            current=sum(booking.total_amount for booking in bookings),
            limit=config.TOTAL_CAP,
        )
    ]
    if config.DIGITAL_CAP:
        digital_bookings_total = sum(
            [booking.total_amount for booking in bookings if config.digital_cap_applies(booking.stock.offer)]
        )
        limits.append(Expense(domain=ExpenseDomain.DIGITAL, current=digital_bookings_total, limit=config.DIGITAL_CAP))
    if config.PHYSICAL_CAP:
        physical_bookings_total = sum(
            [booking.total_amount for booking in bookings if config.physical_cap_applies(booking.stock.offer)]
        )
        limits.append(
            Expense(
                domain=ExpenseDomain.PHYSICAL,
                current=physical_bookings_total,
                limit=config.PHYSICAL_CAP,
            )
        )

    return limits


def create_pro_user(pro_user: ProUserCreationBodyModel) -> User:
    objects_to_save = []

    new_pro_user = User(from_dict=pro_user.dict(by_alias=True))
    new_pro_user.hasAllowedRecommendations = pro_user.contact_ok

    existing_offerer = Offerer.query.filter_by(siren=pro_user.siren).first()

    if existing_offerer:
        user_offerer = _generate_user_offerer_when_existing_offerer(new_pro_user, existing_offerer)
        offerer = existing_offerer
    else:
        offerer = _generate_offerer(pro_user.dict(by_alias=True))
        user_offerer = offerer.grant_access(new_pro_user)
        digital_venue = create_digital_venue(offerer)
        objects_to_save.extend([digital_venue, offerer])
    objects_to_save.append(user_offerer)
    new_pro_user.isBeneficiary = False
    new_pro_user.isAdmin = False
    new_pro_user.needsToFillCulturalSurvey = False
    new_pro_user = _set_offerer_departement_code(new_pro_user, offerer)

    new_pro_user.generate_validation_token()
    objects_to_save.append(new_pro_user)

    repository.save(*objects_to_save)

    try:
        user_emails.send_user_validation_email(new_pro_user)
    except MailServiceException:
        logger.exception("Could not send validation email when creating pro user=%s", new_pro_user.id)

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
    if settings.IS_INTEGRATION:
        new_user.departementCode = "00"
    elif offerer.postalCode is not None:
        new_user.departementCode = PostalCode(offerer.postalCode).get_departement_code()
    else:
        new_user.departementCode = "XX"  # We don't want to trigger an error on this:
        # we want the error on user
    return new_user


def set_pro_tuto_as_seen(user: User) -> None:
    user.hasSeenProTutorials = True
    repository.save(user)
