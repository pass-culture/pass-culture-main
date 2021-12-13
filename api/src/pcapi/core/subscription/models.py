import dataclasses
import datetime
import enum
import typing
from typing import Optional

from dateutil.relativedelta import relativedelta
import sqlalchemy

from pcapi.core.users import constants as user_constants
from pcapi.core.users.models import EligibilityType
from pcapi.domain.postal_code.postal_code import PostalCode
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


if typing.TYPE_CHECKING:
    import pcapi.core.fraud.models as fraud_models


class SubscriptionStep(enum.Enum):
    EMAIL_VALIDATION = "email-validation"
    MAINTENANCE = "maintenance"
    PHONE_VALIDATION = "phone-validation"
    PROFILE_COMPLETION = "profile-completion"
    IDENTITY_CHECK = "identity-check"
    USER_PROFILING = "user-profiling"
    HONOR_STATEMENT = "honor-statement"


class IdentityCheckMethod(enum.Enum):
    EDUCONNECT = "educonnect"
    JOUVE = "jouve"
    UBBLE = "ubble"


class MaintenancePageType(enum.Enum):
    WITH_DMS = "with-dms"
    WITHOUT_DMS = "without-dms"


@dataclasses.dataclass
class BeneficiaryPreSubscription:
    activity: str
    address: str
    application_id: int
    city: Optional[str]
    civility: str
    date_of_birth: datetime.date
    email: str
    first_name: str
    fraud_fields: dict
    id_piece_number: Optional[str]
    last_name: str
    phone_number: str
    postal_code: str
    registration_datetime: datetime.datetime
    source: str
    source_id: Optional[int]

    @property
    def department_code(self) -> str:
        return PostalCode(self.postal_code).get_departement_code()

    @property
    def deposit_source(self) -> str:
        return f"dossier {self.source} [{self.application_id}]"

    @property
    def eligibility_type(self) -> Optional[EligibilityType]:
        """Calculates EligibilityType from date_of_birth and registration_datetime"""
        if self.date_of_birth is None or self.registration_datetime is None:
            return None

        age_at_registration = relativedelta(self.registration_datetime.date(), self.date_of_birth).years
        if age_at_registration == user_constants.ELIGIBILITY_AGE_18:
            return EligibilityType.AGE18
        if age_at_registration in user_constants.ELIGIBILITY_UNDERAGE_RANGE:
            return EligibilityType.UNDERAGE

        return None

    @property
    def public_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def from_dms_source(cls, source_data: "fraud_models.DMSContent") -> "BeneficiaryPreSubscription":
        from pcapi.models.beneficiary_import import BeneficiaryImportSources

        return BeneficiaryPreSubscription(
            activity=source_data.activity,
            address=source_data.address,
            application_id=source_data.application_id,
            civility=source_data.civility,
            city=None,  # not provided in DMS applications
            date_of_birth=source_data.birth_date,
            email=source_data.email,
            first_name=source_data.first_name,
            id_piece_number=source_data.id_piece_number,
            last_name=source_data.last_name,
            phone_number=source_data.phone,
            postal_code=source_data.postal_code,
            registration_datetime=source_data.registration_datetime,
            source=BeneficiaryImportSources.demarches_simplifiees.value,
            source_id=source_data.procedure_id,
            fraud_fields={},
        )


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


class SubscriptionMessage(PcObject, Model):
    __tablename__ = "beneficiary_subscription_message"

    dateCreated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now())

    userId = sqlalchemy.Column(
        sqlalchemy.BigInteger, sqlalchemy.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )

    user = sqlalchemy.orm.relationship("User", foreign_keys=[userId], backref="subscriptionMessages")

    userMessage = sqlalchemy.Column(sqlalchemy.Text, nullable=False)

    callToActionTitle = sqlalchemy.Column(sqlalchemy.Text, nullable=True)

    callToActionLink = sqlalchemy.Column(sqlalchemy.Text, nullable=True)

    callToActionIcon = sqlalchemy.Column(sqlalchemy.Enum(CallToActionIcon, create_constraint=False), nullable=True)

    popOverIcon = sqlalchemy.Column(sqlalchemy.Enum(PopOverIcon, create_constraint=False), nullable=True)
