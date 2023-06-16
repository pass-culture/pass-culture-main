import dataclasses
import datetime
import enum
import typing

from pcapi.core.fraud import models as fraud_models
from pcapi.utils.string import u_nbsp


if typing.TYPE_CHECKING:
    from pcapi.core.users.young_status import YoungStatus


VALID_IDENTITY_CHECK_TYPES_AFTER_UNDERAGE_DEPOSIT_EXPIRATION = [
    fraud_models.FraudCheckType.DMS,
    fraud_models.FraudCheckType.UBBLE,
]


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

    def get_title(self) -> str:
        return self.value.title().replace("-", " ")


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
    identity_fraud_check: fraud_models.BeneficiaryFraudCheck | None = None

    # is_activable is True if beneficiary role can be upgraded.
    is_activable: bool = False

    # subscription_message is the message to display to the user.
    # Be careful : in the frontend, this message is displayed with higher priority than next_step call to action
    subscription_message: SubscriptionMessage | None = None
