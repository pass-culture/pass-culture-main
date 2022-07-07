import dataclasses
import enum

import sqlalchemy

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


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


class SubscriptionMessage(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    __tablename__ = "beneficiary_subscription_message"

    dateCreated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now())

    userId = sqlalchemy.Column(
        sqlalchemy.BigInteger, sqlalchemy.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )

    user = sqlalchemy.orm.relationship("User", foreign_keys=[userId], backref="subscriptionMessages")  # type: ignore [misc]

    userMessage = sqlalchemy.Column(sqlalchemy.Text, nullable=False)

    callToActionTitle = sqlalchemy.Column(sqlalchemy.Text, nullable=True)

    callToActionLink = sqlalchemy.Column(sqlalchemy.Text, nullable=True)

    callToActionIcon = sqlalchemy.Column(sqlalchemy.Enum(CallToActionIcon, create_constraint=False), nullable=True)

    popOverIcon = sqlalchemy.Column(sqlalchemy.Enum(PopOverIcon, create_constraint=False), nullable=True)
