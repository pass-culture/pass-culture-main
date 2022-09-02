import datetime
import re
from typing import Any
from uuid import UUID

from dateutil.relativedelta import relativedelta
from jwt import DecodeError
from jwt import ExpiredSignatureError
from jwt import InvalidSignatureError
from jwt import InvalidTokenError
import pydantic
from pydantic.class_validators import root_validator
from pydantic.class_validators import validator
from pydantic.fields import Field
from sqlalchemy.orm import joinedload

from pcapi.connectors.user_profiling import AgentType
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.payments.models import DepositType
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
import pcapi.core.users.models as users_models
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.core.users.models import VOID_FIRST_NAME
from pcapi.core.users.models import VOID_PUBLIC_NAME
from pcapi.core.users.utils import decode_jwt_token
from pcapi.core.users.utils import sanitize_email
from pcapi.models.feature import FeatureToggle
from pcapi.routes.native.utils import convert_to_cent
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
from pcapi.utils.date import format_into_utc_date


class AccountRequest(BaseModel):
    email: str
    password: str
    birthdate: datetime.date
    marketing_email_subscription: bool | None = False
    token: str
    apps_flyer_user_id: str | None = None
    apps_flyer_platform: str | None = None

    class Config:
        alias_generator = to_camel


class CulturalSurveyRequest(BaseModel):
    needs_to_fill_cultural_survey: bool
    cultural_survey_id: UUID | None

    class Config:
        alias_generator = to_camel


class NotificationSubscriptions(BaseModel):
    marketing_email: bool
    marketing_push: bool

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class Credit(BaseModel):
    initial: int
    remaining: int

    _convert_initial = validator("initial", pre=True, allow_reuse=True)(convert_to_cent)
    _convert_remaining = validator("remaining", pre=True, allow_reuse=True)(convert_to_cent)

    class Config:
        orm_mode = True


class DomainsCredit(BaseModel):
    all: Credit
    digital: Credit | None
    physical: Credit | None

    class Config:
        orm_mode = True


class CallToActionMessage(BaseModel):
    callToActionTitle: str | None
    callToActionLink: str | None
    callToActionIcon: subscription_models.CallToActionIcon | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        use_enum_values = True


class SubscriptionMessage(BaseModel):
    userMessage: str
    callToAction: CallToActionMessage | None
    popOverIcon: subscription_models.PopOverIcon | None
    updatedAt: datetime.datetime

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        json_encoders = {datetime.datetime: format_into_utc_date}
        use_enum_values = True

    @classmethod
    def from_model(cls, model_instance: subscription_models.SubscriptionMessage) -> "SubscriptionMessage":
        cta_message = None
        if any((model_instance.callToActionTitle, model_instance.callToActionLink, model_instance.callToActionIcon)):
            cta_message = CallToActionMessage(
                callToActionTitle=model_instance.callToActionTitle,
                callToActionLink=model_instance.callToActionLink,
                callToActionIcon=model_instance.callToActionIcon,
            )
        subscription_message = SubscriptionMessage(
            userMessage=model_instance.userMessage,
            callToAction=cta_message,
            popOverIcon=model_instance.popOverIcon,
            updatedAt=model_instance.dateCreated,
        )
        return subscription_message

    @classmethod
    def beneficiary_maintenance_message(cls) -> "SubscriptionMessage":
        return cls(
            userMessage="La vérification d'identité est momentanément indisponible. L'équipe du pass Culture met tout en oeuvre pour la rétablir au plus vite.",
            callToAction=None,
            popOverIcon=subscription_models.PopOverIcon.CLOCK,
            updatedAt=datetime.datetime.utcnow(),
        )


class ChangeBeneficiaryEmailBody(BaseModel):
    token: str


class ChangeEmailTokenContent(BaseModel):
    current_email: pydantic.EmailStr
    new_email: pydantic.EmailStr

    @validator("current_email", "new_email", pre=True)
    @classmethod
    def validate_emails(cls, email: str) -> str:
        try:
            return sanitize_email(email)
        except Exception as e:
            raise ValueError(email) from e

    @classmethod
    def from_token(cls, token: str) -> "ChangeEmailTokenContent":
        try:
            jwt_payload = decode_jwt_token(token)
        except (
            ExpiredSignatureError,
            InvalidSignatureError,
            DecodeError,
            InvalidTokenError,
        ) as error:
            raise InvalidTokenError() from error

        if not {"new_email", "current_email"} <= set(jwt_payload):
            raise InvalidTokenError()

        current_email = jwt_payload["current_email"]
        new_email = jwt_payload["new_email"]
        return cls(current_email=current_email, new_email=new_email)


class UserProfileResponse(BaseModel):
    booked_offers: dict[str, int]
    dateOfBirth: datetime.date | None
    deposit_expiration_date: datetime.datetime | None
    deposit_type: DepositType | None
    deposit_version: int | None
    domains_credit: DomainsCredit | None
    eligibility: EligibilityType | None
    eligibility_end_datetime: datetime.datetime | None
    eligibility_start_datetime: datetime.datetime | None
    email: str
    firstName: str | None
    id: int
    isBeneficiary: bool
    isEligibleForBeneficiaryUpgrade: bool
    lastName: str | None
    needsToFillCulturalSurvey: bool
    phoneNumber: str | None
    publicName: str | None = Field(None, alias="pseudo")
    recreditAmountToShow: int | None
    roles: list[UserRole]
    show_eligible_card: bool
    subscriptions: NotificationSubscriptions  # if we send user.notification_subscriptions, pydantic will take the column and not the property
    subscriptionMessage: SubscriptionMessage | None

    _convert_recredit_amount_to_show = validator("recreditAmountToShow", pre=True, allow_reuse=True)(convert_to_cent)

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True
        json_encoders = {datetime.datetime: format_into_utc_date}
        use_enum_values = True

    @validator("publicName", pre=True)
    def format_public_name(cls, publicName: str) -> str | None:  # pylint: disable=no-self-argument
        return publicName if publicName != VOID_PUBLIC_NAME else None

    @validator("firstName", pre=True)
    def format_first_name(cls, firstName: str | None) -> str | None:  # pylint: disable=no-self-argument
        return firstName if firstName != VOID_FIRST_NAME else None

    @staticmethod
    def _show_eligible_card(user: User) -> bool:
        return (
            relativedelta(user.dateCreated, user.dateOfBirth).years < users_constants.ELIGIBILITY_AGE_18
            and user.has_beneficiary_role is False
            and user.eligibility == EligibilityType.AGE18
        )

    @staticmethod
    def _get_booked_offers(user: User) -> dict:
        not_cancelled_bookings = (
            Booking.query.join(Booking.individualBooking)
            .options(joinedload(Booking.stock).joinedload(Stock.offer).load_only(Offer.id))
            .filter(
                IndividualBooking.userId == user.id,
                Booking.status != BookingStatus.CANCELLED,
            )
        )

        return {booking.stock.offer.id: booking.id for booking in not_cancelled_bookings}

    @classmethod
    def _get_subscription_message(cls, user: User) -> SubscriptionMessage | None:
        """
        Return the user's latest subscription message, regarding his
        signup process UNLESS the beneficiary signup process has been
        deactivated: return a generic maintenance message in this case.
        """
        if subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.MAINTENANCE:
            return SubscriptionMessage.beneficiary_maintenance_message()

        latest_message = subscription_api.get_latest_subscription_message(user)
        if latest_message:
            return SubscriptionMessage.from_model(latest_message)

        return None

    @classmethod
    def from_orm(cls, user: User):  # type: ignore
        user.show_eligible_card = cls._show_eligible_card(user)
        user.subscriptions = user.get_notification_subscriptions()
        user.domains_credit = users_api.get_domains_credit(user)
        user.booked_offers = cls._get_booked_offers(user)
        user.isEligibleForBeneficiaryUpgrade = users_api.is_eligible_for_beneficiary_upgrade(user, user.eligibility)
        user.eligibility_end_datetime = users_api.get_eligibility_end_datetime(user.dateOfBirth)
        user.eligibility_start_datetime = users_api.get_eligibility_start_datetime(user.dateOfBirth)
        user.isBeneficiary = user.is_beneficiary
        user.subscriptionMessage = cls._get_subscription_message(user)

        if _should_prevent_from_filling_cultural_survey(user):
            user.needsToFillCulturalSurvey = False

        return super().from_orm(user)


def _should_prevent_from_filling_cultural_survey(user: User) -> bool:
    # when the native form is active, there is no reason to prevent
    if FeatureToggle.ENABLE_NATIVE_CULTURAL_SURVEY.is_active():
        return False
    # when the typeform is active, it should be limited to only beneficiaries to respect the quota
    return not FeatureToggle.ENABLE_CULTURAL_SURVEY.is_active() or not user.is_beneficiary


class UserProfileUpdateRequest(BaseModel):
    subscriptions: NotificationSubscriptions | None


class UserProfileEmailUpdate(BaseModel):
    email: pydantic.EmailStr
    password: pydantic.constr(strip_whitespace=True, min_length=8, strict=True)  # type: ignore


class ValidateEmailRequest(BaseModel):
    token: str


class UpdateEmailTokenExpiration(BaseModel):
    expiration: datetime.datetime | None


class ResendEmailValidationRequest(BaseModel):
    email: str


class ValidatePhoneNumberRequest(BaseModel):
    code: str


class SendPhoneValidationRequest(BaseModel):
    phoneNumber: str


class PhoneValidationRemainingAttemptsRequest(BaseModel):
    remainingAttempts: int
    counterResetDatetime: datetime.datetime | None

    class Config:
        json_encoders = {datetime.datetime: format_into_utc_date}


class UserProfilingFraudRequest(BaseModel):
    # Moving from session_id to sessionId - remove session_id and set sessionId not Optional when app version is forced
    # to a new minimal version. Also restore a simple validator session_id_alphanumerics for sessionId
    session_id: str | None
    sessionId: str | None
    agentType: AgentType | None

    @root_validator()
    def session_id_alphanumerics(cls, values: dict[str, Any]) -> dict[str, Any]:  # pylint: disable=no-self-argument
        session_id = values.get("sessionId") or values.get("session_id")
        if not session_id:
            raise ValueError("L'identifiant de session est manquant")
        if not re.match(r"^[A-Za-z0-9_-]{1,128}$", session_id):
            raise ValueError(
                "L'identifiant de session ne doit être composé exclusivement que de caratères alphanumériques"
            )
        values["sessionId"] = session_id
        return values

    @validator("agentType", always=True)
    def agent_type_validation(cls, agent_type: str) -> str:  # pylint: disable=no-self-argument
        if agent_type is None:
            agent_type = AgentType.AGENT_MOBILE
        if agent_type not in (AgentType.BROWSER_COMPUTER, AgentType.BROWSER_MOBILE, AgentType.AGENT_MOBILE):
            raise ValueError("agentType est invalide")
        return agent_type


class UserProfilingSessionIdResponse(BaseModel):
    sessionId: str


class UserSuspensionDateResponse(BaseModel):
    date: datetime.datetime | None

    class Config:
        json_encoders = {datetime.datetime: format_into_utc_date}


class UserSuspensionStatusResponse(BaseModel):
    status: users_models.AccountState
