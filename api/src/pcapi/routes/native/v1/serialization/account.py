import datetime
import re
import typing
from enum import Enum

import email_validator
import pydantic as pydantic_v2
from sqlalchemy.orm import joinedload

import pcapi.core.finance.models as finance_models
import pcapi.core.users.models as users_models
from pcapi import settings
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance.utils import CurrencyEnum
from pcapi.core.offers import models as offers_models
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import profile_options
from pcapi.core.users import api as users_api
from pcapi.core.users import eligibility_api
from pcapi.core.users import young_status
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.routes.native.v1.serialization import achievements as achievements_serialization
from pcapi.routes.native.v1.serialization import subscription as subscription_serialization
from pcapi.routes.native.v1.serialization.common_models import DeviceInfo
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel
from pcapi.routes.shared.price import convert_to_cent
from pcapi.utils.email import sanitize_email


class AccountRequest(HttpQueryParamsModel):
    birthdate: datetime.date
    marketing_email_subscription: bool | None = False
    token: str
    firebase_pseudo_id: str | None = None
    trusted_device: DeviceInfo | None = None
    email: pydantic_v2.EmailStr
    password: str
    apps_flyer_user_id: str | None = None  # XXX Deprecated. It's here to keep compatibility with older app versions
    apps_flyer_platform: str | None = None  # XXX Deprecated. It's here to keep compatibility with older app versions

    @pydantic_v2.field_validator("email", mode="after")
    @classmethod
    def validate_email(cls, email: typing.Any) -> str:
        try:
            emailinfo = email_validator.validate_email(
                email, check_deliverability=settings.ENABLE_EMAIL_DELIVERABILITY_CHECK
            )
            sanitized_email = sanitize_email(emailinfo.normalized)

            # check for non-ascii and special characters
            allowed_pattern = re.compile(r"^[a-zA-Z0-9+\-_.@]+$")
            if not allowed_pattern.match(sanitized_email):
                raise ValueError("unsupported special characters detected")

            return sanitized_email
        except Exception as e:
            raise ValueError(email) from e


class SSOAccountRequest(HttpQueryParamsModel):
    birthdate: datetime.date
    marketing_email_subscription: bool | None = False
    token: str
    firebase_pseudo_id: str | None = None
    trusted_device: DeviceInfo | None = None
    account_creation_token: str
    apps_flyer_user_id: str | None = None  # XXX Deprecated. It's here to keep compatibility with older app versions
    apps_flyer_platform: str | None = None  # XXX Deprecated. It's here to keep compatibility with older app versions


class SSOProvider(Enum):
    APPLE = "apple"
    GOOGLE = "google"


class NotificationSubscriptions(HttpBodyModel):
    marketing_email: bool
    marketing_push: bool
    subscribed_themes: list[str] = []


class Credit(HttpBodyModel):
    initial: int
    remaining: int

    @pydantic_v2.field_validator("initial", "remaining", mode="before")
    @classmethod
    def _to_cent(cls, amount: typing.Any) -> int | None:
        return convert_to_cent(amount)


class DomainsCredit(HttpBodyModel):
    all: Credit
    digital: Credit | None = None
    physical: Credit | None = None


class ChangeBeneficiaryEmailBody(HttpQueryParamsModel):
    token: str
    device_info: DeviceInfo | None = None


class ChangeBeneficiaryEmailResponse(HttpBodyModel):
    access_token: str
    refresh_token: str


class YoungStatusResponse(HttpBodyModel):
    status_type: young_status.YoungStatusType
    subscription_status: young_status.SubscriptionStatus | None = None


class UserProfileResponse(HttpBodyModel):
    achievements: list[achievements_serialization.AchievementResponse]
    activity_id: profile_options.ActivityIdEnum | None = None
    address: str | None = pydantic_v2.Field(default=None, alias="street")
    birth_date: datetime.date | None = None
    booked_offers: dict[str, int]
    city: str | None = None
    currency: CurrencyEnum
    deposit_activation_date: datetime.datetime | None = None
    deposit_expiration_date: datetime.datetime | None = None
    deposit_type: finance_models.DepositType | None = None
    domains_credit: DomainsCredit | None = None
    eligibility: users_models.EligibilityType | None = None
    eligibility_end_datetime: datetime.datetime | None = None
    eligibility_start_datetime: datetime.datetime | None = None
    email: str
    first_deposit_activation_date: datetime.datetime | None = None
    first_name: str | None = None
    has_password: bool
    has_profile_expired: bool
    id: int
    is_beneficiary: bool
    is_eligible_for_beneficiary_upgrade: bool
    last_name: str | None = None
    needs_to_fill_cultural_survey: bool
    phone_number: str | None = None
    postal_code: str | None = None
    qf_bonification_status: subscription_models.QFBonificationStatus | None = None
    recredit_amount_to_show: int | None = None
    recredit_type_to_show: finance_models.RecreditType | None = None
    remaining_bonus_attempts: int | None = None
    requires_id_check: bool
    roles: list[users_models.UserRole]
    show_eligible_card: bool
    status: YoungStatusResponse
    subscription_message: subscription_serialization.SubscriptionMessageV2 | None = None
    subscriptions: NotificationSubscriptions

    @staticmethod
    def _get_activity(user_activity: str | None) -> profile_options.ActivityIdEnum | None:
        try:
            activity = users_models.ActivityEnum(user_activity)
            return profile_options.ActivityIdEnum(activity.name)
        except ValueError:
            return None

    @staticmethod
    def _get_booked_offers(user_id: int) -> dict[str, int]:
        not_cancelled_bookings = (
            db.session.query(bookings_models.Booking)
            .options(
                joinedload(bookings_models.Booking.stock)
                .joinedload(offers_models.Stock.offer)
                .load_only(offers_models.Offer.id)
            )
            .filter(
                bookings_models.Booking.userId == user_id,
                bookings_models.Booking.status != bookings_models.BookingStatus.CANCELLED,
            )
        )
        return {str(booking.stock.offer.id): booking.id for booking in not_cancelled_bookings}

    @staticmethod
    def _get_eligibility_start_datetime(user: users_models.User) -> datetime.datetime | None:
        return eligibility_api.get_eligibility_start_datetime(user.birth_date, user.departementCode)

    @staticmethod
    def _get_status(user: users_models.User) -> YoungStatusResponse:
        user_subscription_state = subscription_api.get_user_subscription_state(user)
        status = user_subscription_state.young_status
        return YoungStatusResponse(
            status_type=status.status_type,
            subscription_status=getattr(status, "subscription_status", None),
        )

    @staticmethod
    def _get_subscription_message(user: users_models.User) -> subscription_serialization.SubscriptionMessageV2 | None:
        user_subscription_state = subscription_api.get_user_subscription_state(user)
        message = user_subscription_state.subscription_message
        if message is not None:
            message_call_to_action = message.call_to_action
            call_to_action = (
                subscription_serialization.CallToActionMessageV2(
                    title=message_call_to_action.title,
                    link=message_call_to_action.link,
                    icon=message_call_to_action.icon,
                )
                if message_call_to_action
                else None
            )
            return subscription_serialization.SubscriptionMessageV2(
                user_message=message.user_message,
                message_summary=message.message_summary,
                call_to_action=call_to_action,
                pop_over_icon=message.pop_over_icon,
                updated_at=message.updated_at,
            )
        return None

    @pydantic_v2.model_validator(mode="before")
    @classmethod
    def _pre_validate(cls, data: typing.Any) -> typing.Any:
        if isinstance(data, users_models.User):
            user: users_models.User = data
            return cls(
                achievements=[
                    achievements_serialization.AchievementResponse.model_validate(achievement)
                    for achievement in user.achievements
                ],
                activity_id=cls._get_activity(user.activity),
                address=user.address,
                birth_date=user.birth_date,
                booked_offers=cls._get_booked_offers(user.id),
                city=user.city,
                currency=CurrencyEnum.XPF if user.is_caledonian else CurrencyEnum.EUR,
                deposit_activation_date=user.deposit_activation_date,
                deposit_expiration_date=user.deposit_expiration_date,
                deposit_type=user.deposit_type,
                domains_credit=users_api.get_domains_credit(user),
                eligibility=user.eligibility,
                eligibility_end_datetime=eligibility_api.get_eligibility_end_datetime(
                    user.birth_date, user.departementCode
                ),
                eligibility_start_datetime=cls._get_eligibility_start_datetime(user),
                email=user.email,
                first_deposit_activation_date=user.first_deposit_activation_date,
                first_name=user.firstName or None,
                has_password=user.password is not None,
                has_profile_expired=users_api.has_profile_expired(user),
                id=user.id,
                is_beneficiary=user.is_beneficiary,
                is_eligible_for_beneficiary_upgrade=eligibility_api.is_eligible_for_next_recredit_activation_steps(
                    user
                ),
                last_name=user.lastName,
                needs_to_fill_cultural_survey=(
                    user.needsToFillCulturalSurvey and user.is_eligible and _is_cultural_survey_active()
                ),
                phone_number=user.phoneNumber,
                postal_code=user.postalCode,
                qf_bonification_status=users_api.get_user_qf_bonification_status(user),
                recredit_amount_to_show=convert_to_cent(user.recreditAmountToShow),
                recredit_type_to_show=users_api.get_latest_user_recredit_type(user),
                remaining_bonus_attempts=users_api.get_user_remaining_bonus_attempts(user),
                requires_id_check=subscription_api.requires_identity_check_step(user),
                roles=user.roles,
                show_eligible_card=not user.has_beneficiary_role and user.is_18_or_above_eligible,
                status=cls._get_status(user),
                subscription_message=cls._get_subscription_message(user),
                subscriptions=user.get_notification_subscriptions(),
            )
        return data

    model_config = pydantic_v2.ConfigDict(
        use_enum_values=True,
    )


def _is_cultural_survey_active() -> bool:
    # When the native form or typeform form is active, there is no reason to prevent
    return FeatureToggle.ENABLE_NATIVE_CULTURAL_SURVEY.is_active() or FeatureToggle.ENABLE_CULTURAL_SURVEY.is_active()


class UserProfilePatchRequest(HttpQueryParamsModel):
    activity_id: profile_options.ActivityIdEnum | None = None
    address: str | None = None
    city: str | None = None
    postal_code: str | None = None
    phone_number: str | None = None
    subscriptions: NotificationSubscriptions | None = None
    origin: str | None = None


class UpdateEmailTokenExpiration(HttpBodyModel):
    expiration: datetime.datetime | None = None


class ResendEmailValidationRequest(HttpQueryParamsModel):
    email: pydantic_v2.EmailStr

    @pydantic_v2.field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, email: str) -> str:
        try:
            return sanitize_email(email)
        except Exception as e:
            raise ValueError(email) from e


class EmailValidationRemainingResendsResponse(HttpBodyModel):
    remainingResends: int
    counterResetDatetime: datetime.datetime | None = None


class ValidatePhoneNumberRequest(HttpQueryParamsModel):
    code: str


class SendPhoneValidationRequest(HttpQueryParamsModel):
    phoneNumber: str


class PhoneValidationRemainingAttemptsRequest(HttpBodyModel):
    remainingAttempts: int
    counterResetDatetime: datetime.datetime | None = None


class UserSuspensionDateResponse(HttpBodyModel):
    date: datetime.datetime | None = None


class UserSuspensionStatusResponse(HttpBodyModel):
    status: users_models.AccountState


class SuspendAccountForSuspiciousLoginRequest(HttpQueryParamsModel):
    token: str
