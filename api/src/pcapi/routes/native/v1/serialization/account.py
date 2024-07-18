import datetime
import typing

from dateutil.relativedelta import relativedelta
from jwt import DecodeError
from jwt import ExpiredSignatureError
from jwt import InvalidSignatureError
from jwt import InvalidTokenError
import pydantic.v1 as pydantic_v1
from pydantic.v1.class_validators import validator
from pydantic.v1.utils import GetterDict
from sqlalchemy.orm import joinedload

from pcapi.core.bookings import models as bookings_models
import pcapi.core.finance.models as finance_models
from pcapi.core.offers import models as offers_models
from pcapi.core.subscription import api as subscription_api
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import young_status
import pcapi.core.users.models as users_models
from pcapi.core.users.utils import decode_jwt_token
from pcapi.models.feature import FeatureToggle
from pcapi.routes.native.v1.serialization import subscription as subscription_serialization
from pcapi.routes.serialization import ConfiguredBaseModel
from pcapi.routes.shared.price import convert_to_cent
from pcapi.utils.email import sanitize_email


class TrustedDevice(ConfiguredBaseModel):
    device_id: str
    os: str | None
    source: str | None

    class Config:
        anystr_strip_whitespace = True


class BaseAccountRequest(ConfiguredBaseModel):
    birthdate: datetime.date
    marketing_email_subscription: bool | None = False
    token: str
    apps_flyer_user_id: str | None = None
    apps_flyer_platform: str | None = None
    firebase_pseudo_id: str | None = None
    trusted_device: TrustedDevice | None = None


class AccountRequest(BaseAccountRequest):
    email: str
    password: str


class GoogleAccountRequest(BaseAccountRequest):
    account_creation_token: str


class NotificationSubscriptions(ConfiguredBaseModel):
    marketing_email: bool
    marketing_push: bool
    subscribed_themes: list[str] = []


class Credit(ConfiguredBaseModel):
    initial: int
    remaining: int

    _convert_initial = validator("initial", pre=True, allow_reuse=True)(convert_to_cent)
    _convert_remaining = validator("remaining", pre=True, allow_reuse=True)(convert_to_cent)


class DomainsCredit(ConfiguredBaseModel):
    all: Credit
    digital: Credit | None
    physical: Credit | None


class ChangeBeneficiaryEmailBody(ConfiguredBaseModel):
    token: str
    device_info: TrustedDevice | None = None


class ChangeBeneficiaryEmailResponse(ConfiguredBaseModel):
    access_token: str
    refresh_token: str


class ChangeEmailTokenContent(ConfiguredBaseModel):
    current_email: pydantic_v1.EmailStr
    new_email: pydantic_v1.EmailStr

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


class YoungStatusResponse(ConfiguredBaseModel):
    status_type: young_status.YoungStatusType
    subscription_status: young_status.SubscriptionStatus | None


class UserProfileGetterDict(GetterDict):
    def get(self, key: str, default: typing.Any | None = None) -> typing.Any:
        user = self._obj
        if key == "firstName":
            return user.firstName if user.firstName != users_models.VOID_FIRST_NAME else None
        if key == "showEligibleCard":
            return (
                relativedelta(user.dateCreated, user.birth_date).years < users_constants.ELIGIBILITY_AGE_18
                and user.has_beneficiary_role is False
                and user.eligibility == users_models.EligibilityType.AGE18
            )
        if key == "subscriptions":
            return user.get_notification_subscriptions()
        if key == "domainsCredit":
            return users_api.get_domains_credit(user)
        if key == "bookedOffers":
            not_cancelled_bookings = bookings_models.Booking.query.options(
                joinedload(bookings_models.Booking.stock)
                .joinedload(offers_models.Stock.offer)
                .load_only(offers_models.Offer.id)
            ).filter(
                bookings_models.Booking.userId == user.id,
                bookings_models.Booking.status != bookings_models.BookingStatus.CANCELLED,
            )

            return {booking.stock.offer.id: booking.id for booking in not_cancelled_bookings}
        if key == "isEligibleForBeneficiaryUpgrade":
            return users_api.is_eligible_for_beneficiary_upgrade(user, user.eligibility)
        if key == "eligibilityEndDatetime":
            return users_api.get_eligibility_end_datetime(user.birth_date)
        if key == "eligibilityStartDatetime":
            return users_api.get_eligibility_start_datetime(user.birth_date)
        if key == "isBeneficiary":
            return user.is_beneficiary
        if key == "subscriptionMessage":
            user_subscription_state = subscription_api.get_user_subscription_state(user)
            return user_subscription_state.subscription_message
        if key == "status":
            user_subscription_state = subscription_api.get_user_subscription_state(user)
            return user_subscription_state.young_status
        if key == "requiresIdCheck":
            return subscription_api.requires_identity_check_step(user)
        if key == "hasPassword":
            return user.password is not None
        if key == "needsToFillCulturalSurvey":
            return user.needsToFillCulturalSurvey and user.is_beneficiary and _is_cultural_survey_active()

        return super().get(key, default)


class UserProfileResponse(ConfiguredBaseModel):
    booked_offers: dict[str, int]
    birth_date: datetime.date | None
    deposit_activation_date: datetime.datetime | None
    deposit_expiration_date: datetime.datetime | None
    deposit_type: finance_models.DepositType | None
    domains_credit: DomainsCredit | None
    eligibility: users_models.EligibilityType | None
    eligibility_end_datetime: datetime.datetime | None
    eligibility_start_datetime: datetime.datetime | None
    email: str
    first_name: str | None
    id: int
    is_beneficiary: bool
    is_eligible_for_beneficiary_upgrade: bool
    has_password: bool
    last_name: str | None
    needs_to_fill_cultural_survey: bool
    phone_number: str | None
    recredit_amount_to_show: int | None
    requires_id_check: bool
    roles: list[users_models.UserRole]
    show_eligible_card: bool
    subscription_message: subscription_serialization.SubscriptionMessage | None
    subscriptions: NotificationSubscriptions  # if we send user.notification_subscriptions, pydantic will take the column and not the property
    status: YoungStatusResponse

    _convert_recredit_amount_to_show = validator("recredit_amount_to_show", pre=True, allow_reuse=True)(convert_to_cent)

    class Config:
        use_enum_values = True
        getter_dict = UserProfileGetterDict


def _is_cultural_survey_active() -> bool:
    # When the native form or typeform form is active, there is no reason to prevent
    return FeatureToggle.ENABLE_NATIVE_CULTURAL_SURVEY.is_active() or FeatureToggle.ENABLE_CULTURAL_SURVEY.is_active()


class UserProfileUpdateRequest(ConfiguredBaseModel):
    subscriptions: NotificationSubscriptions | None
    origin: str | None


class UserProfileEmailUpdate(ConfiguredBaseModel):
    email: pydantic_v1.EmailStr  # the new email address
    if typing.TYPE_CHECKING:  # https://github.com/pydantic/pydantic/issues/156
        password: str
    else:
        password: pydantic_v1.constr(strip_whitespace=True, min_length=8, strict=True)


class ValidateEmailRequest(ConfiguredBaseModel):
    token: str


class UpdateEmailTokenExpiration(ConfiguredBaseModel):
    expiration: datetime.datetime | None


class EmailUpdateStatus(ConfiguredBaseModel):
    newEmail: str
    expired: bool
    status: users_models.EmailHistoryEventTypeEnum


class ResendEmailValidationRequest(ConfiguredBaseModel):
    email: str


class EmailValidationRemainingResendsResponse(ConfiguredBaseModel):
    remainingResends: int
    counterResetDatetime: datetime.datetime | None


class ValidatePhoneNumberRequest(ConfiguredBaseModel):
    code: str


class SendPhoneValidationRequest(ConfiguredBaseModel):
    phoneNumber: str


class PhoneValidationRemainingAttemptsRequest(ConfiguredBaseModel):
    remainingAttempts: int
    counterResetDatetime: datetime.datetime | None


class UserSuspensionDateResponse(ConfiguredBaseModel):
    date: datetime.datetime | None


class UserSuspensionStatusResponse(ConfiguredBaseModel):
    status: users_models.AccountState


class SuspendAccountForSuspiciousLoginRequest(ConfiguredBaseModel):
    token: str
