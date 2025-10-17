import dataclasses
import datetime
import enum
import typing

import pydantic.v1 as pydantic_v1
from pydantic.v1.class_validators import validator

from pcapi.core.subscription.models import BeneficiaryFraudCheck
from pcapi.core.subscription.models import FraudReasonCode
from pcapi.core.users import models as users_models
from pcapi.serialization.utils import to_camel
from pcapi.utils.string import u_nbsp


if typing.TYPE_CHECKING:
    from pcapi.core.users.young_status import YoungStatus


STEPPER_DEFAULT_TITLE = f"C'est très rapide{u_nbsp}!"
STEPPER_DEFAULT_SUBTITLE = "Pour débloquer tes {}€ tu dois suivre les étapes suivantes\u00a0:"
STEPPER_HAS_ISSUES_TITLE = "La vérification de ton identité a échoué"
PROFILE_COMPLETION_STEP_EXISTING_DATA_SUBTITLE = "Confirme tes informations"


class SubscriptionStep(enum.Enum):
    EMAIL_VALIDATION = "email-validation"
    MAINTENANCE = "maintenance"
    PHONE_VALIDATION = "phone-validation"
    PROFILE_COMPLETION = "profile-completion"
    IDENTITY_CHECK = "identity-check"
    HONOR_STATEMENT = "honor-statement"


class SubscriptionStepTitle(enum.Enum):
    PHONE_VALIDATION = "Numéro de téléphone"
    PROFILE_COMPLETION = "Profil"
    IDENTITY_CHECK = "Identification"
    HONOR_STATEMENT = "Confirmation"


class SubscriptionItemStatus(enum.Enum):
    KO = "ko"
    NOT_APPLICABLE = "not-applicable"
    NOT_ENABLED = "not-enabled"
    OK = "ok"
    PENDING = "pending"
    SKIPPED = "skipped"
    SUSPICIOUS = "suspicious"
    TODO = "todo"
    VOID = "void"


class SubscriptionStepCompletionState(enum.Enum):
    COMPLETED = "completed"
    CURRENT = "current"
    DISABLED = "disabled"
    RETRY = "retry"


@dataclasses.dataclass
class SubscriptionStepDetails:
    completion_state: SubscriptionStepCompletionState
    name: SubscriptionStep
    title: SubscriptionStepTitle
    subtitle: str | None = None


@dataclasses.dataclass
class SubscriptionStepperDetails:
    title: str
    subtitle: str | None = None


@dataclasses.dataclass
class SubscriptionItem:
    type: SubscriptionStep
    status: SubscriptionItemStatus


class IdentityCheckMethod(enum.Enum):
    EDUCONNECT = "educonnect"
    UBBLE = "ubble"


class MaintenancePageType(enum.Enum):
    WITH_DMS = "with-dms"
    WITHOUT_DMS = "without-dms"


class CallToActionIcon(enum.Enum):
    EMAIL = "EMAIL"
    RETRY = "RETRY"
    EXTERNAL = "EXTERNAL"


class PopOverIcon(enum.Enum):
    INFO = "INFO"
    ERROR = "ERROR"
    WARNING = "WARNING"
    CLOCK = "CLOCK"
    FILE = "FILE"
    MAGNIFYING_GLASS = "MAGNIFYING_GLASS"


@dataclasses.dataclass
class CallToActionMessage:
    title: str | None = None
    link: str | None = None
    icon: CallToActionIcon | None = None


@dataclasses.dataclass
class SubscriptionMessage:
    user_message: str
    message_summary: str | None = None
    action_hint: str | None = None
    call_to_action: CallToActionMessage | None = None
    pop_over_icon: PopOverIcon | None = None
    updated_at: datetime.datetime | None = None


@dataclasses.dataclass
class UserSubscriptionState:
    # fraud_status holds the user status relative to its fraud checks. It is mainly used in the admin interface.
    fraud_status: SubscriptionItemStatus

    # next_step holds the next step to be done by the user to complete its subscription.
    # In the frontend, each enum value corresponds to a call to action.
    next_step: SubscriptionStep | None

    # young_status holds the user status relative to its subscription. It is mainly used in the frontend.
    young_status: "YoungStatus"

    # identity_fraud_check is the relevant identity fraud check used to calculate their status.
    identity_fraud_check: BeneficiaryFraudCheck | None = None

    # is_activable is True if beneficiary role can be upgraded.
    is_activable: bool = False

    # subscription_message is the message to display to the user.
    # Be careful : in the frontend, this message is displayed with higher priority than next_step call to action
    subscription_message: SubscriptionMessage | None = None


# FIXME: deprecate this class in favor of FraudCheckStatus
class FraudStatus(enum.Enum):
    KO = "KO"
    OK = "OK"
    SUBSCRIPTION_ON_HOLD = "SUBSCRIPTION_ON_HOLD"
    SUSPICIOUS = "SUSPICIOUS"


@dataclasses.dataclass
class FraudItem:
    detail: str
    status: FraudStatus
    extra_data: dict = dataclasses.field(default_factory=dict)
    reason_codes: list[FraudReasonCode] = dataclasses.field(default_factory=list)

    def __bool__(self) -> bool:
        return self.status == FraudStatus.OK

    def get_duplicate_beneficiary_id(self) -> int | None:
        return self.extra_data.get("duplicate_id")


class ProfileCompletionContent(pydantic_v1.BaseModel):
    activity: (
        users_models.ActivityEnum | str | None
    )  # str for backward compatibility. All new data should be ActivityEnum
    address: str | None  # Optional because it was not saved up until now
    city: str | None  # Optional because it was not saved up until now
    first_name: str
    last_name: str
    origin: str  # Where the profile was completed by the user. Can be the APP or DMS
    postal_code: str | None  # Optional because it was not saved up until now
    school_type: users_models.SchoolTypeEnum | None

    @validator("activity", pre=True)
    def validate_activity(cls, value: users_models.ActivityEnum | str | None) -> users_models.ActivityEnum | str | None:
        # Avoid validation error for old data because of rewording
        if value == "Chômeur":
            return users_models.ActivityEnum.UNEMPLOYED.value
        return value

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True
        alias_generator = to_camel


class IdentityCheckContent(pydantic_v1.BaseModel):
    def get_birth_date(self) -> datetime.date | None:
        raise NotImplementedError()

    def get_birth_place(self) -> str | None:
        return None

    def get_first_name(self) -> str | None:
        raise NotImplementedError()

    def get_last_name(self) -> str | None:
        raise NotImplementedError()

    def get_activity(self) -> str | None:
        return None

    def get_address(self) -> str | None:
        return None

    def get_civility(self) -> str | None:
        return None

    def get_city(self) -> str | None:
        return None

    def get_id_piece_number(self) -> str | None:
        return None

    def get_ine_hash(self) -> str | None:
        return None

    def get_latest_modification_datetime(self) -> datetime.datetime | None:
        return None

    def get_married_name(self) -> str | None:
        return None

    def get_phone_number(self) -> str | None:
        return None

    def get_postal_code(self) -> str | None:
        return None

    def get_registration_datetime(self) -> datetime.datetime | None:
        return None


class InternalReviewSource(enum.Enum):
    BLACKLISTED_PHONE_NUMBER = "blacklisted_phone_number"
    DOCUMENT_VALIDATION_ERROR = "document_validation_error"
    PHONE_ALREADY_EXISTS = "phone_already_exists"
    PHONE_VALIDATION_ATTEMPTS_LIMIT_REACHED = "phone_validation_attempts_limit_reached"
    SMS_SENDING_LIMIT_REACHED = "sms_sending_limit_reached"


class PhoneValidationFraudData(pydantic_v1.BaseModel):
    message: str | None = None  # legacy field, still present in database
    phone_number: str | None = None
    source: InternalReviewSource | None = None  # legacy field, still present in database


class HonorStatementContent(pydantic_v1.BaseModel):
    pass


# Deprecated classes kept for backwards compatibility
class UserProfilingRiskRating(enum.Enum):
    HIGH = "high"
    LOW = "low"
    MEDIUM = "medium"
    NEUTRAL = "neutral"
    TRUSTED = "trusted"


class UserProfilingFraudData(pydantic_v1.BaseModel):
    account_email_first_seen: datetime.date | None
    account_email_result: str
    account_email_score: int | None
    account_email: str
    account_telephone_first_seen: datetime.date | None
    account_telephone_is_valid: str | None  # Optional because Phone Validation may be disabled by FF
    account_telephone_result: str | None  # Optional because Phone Validation may be disabled by FF
    account_telephone_score: int | None
    bb_bot_rating: str
    bb_bot_score: float
    bb_fraud_rating: str
    bb_fraud_score: float
    device_id: str | None
    digital_id_confidence: int
    digital_id_confidence_rating: str
    digital_id_result: str
    digital_id_trust_score_rating: str
    digital_id_trust_score_reason_code: list[str]
    digital_id_trust_score: float
    digital_id: str
    event_datetime: datetime.datetime
    policy_score: int
    reason_code: list[str]
    request_id: str
    risk_rating: UserProfilingRiskRating
    session_id: str
    summary_risk_score: int
    tmx_risk_rating: str
    tmx_summary_reason_code: list[str] | None
    unknown_session: str | None
