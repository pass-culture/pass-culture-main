import dataclasses
import enum


class SubscriptionStep(enum.Enum):
    EMAIL_VALIDATION = "email-validation"
    MAINTENANCE = "maintenance"
    PHONE_VALIDATION = "phone-validation"
    PROFILE_COMPLETION = "profile-completion"
    IDENTITY_CHECK = "identity-check"
    USER_PROFILING = "user-profiling"
    HONOR_STATEMENT = "honor-statement"


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
    call_to_action: CallToActionMessage | None = None
    pop_over_icon: PopOverIcon | None = None
