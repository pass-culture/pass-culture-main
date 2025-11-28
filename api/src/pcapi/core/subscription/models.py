import datetime
import enum
import typing

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.dialects import postgresql

from pcapi.core.users import constants as users_constants
from pcapi.core.users import models as users_models
from pcapi.models import Model
from pcapi.models.pc_object import PcObject
from pcapi.utils import date as date_utils
from pcapi.utils.db import MagicEnum


if typing.TYPE_CHECKING:
    from pcapi.core.subscription.bonus.schemas import BonusCreditContent
    from pcapi.core.subscription.dms.schemas import DMSContent
    from pcapi.core.subscription.educonnect.schemas import EduconnectContent
    from pcapi.core.subscription.jouve.schemas import JouveContent
    from pcapi.core.subscription.schemas import HonorStatementContent
    from pcapi.core.subscription.schemas import PhoneValidationFraudData
    from pcapi.core.subscription.schemas import ProfileCompletionContent
    from pcapi.core.subscription.schemas import UserProfilingFraudData
    from pcapi.core.subscription.ubble.schemas import UbbleContent


class FraudCheckType(enum.Enum):
    BONUS_CREDIT = "bonus_credit"
    DMS = "dms"
    EDUCONNECT = "educonnect"
    HONOR_STATEMENT = "honor_statement"
    INTERNAL_REVIEW = "internal_review"
    PHONE_VALIDATION = "phone_validation"
    PROFILE_COMPLETION = "profile_completion"
    UBBLE = "ubble"
    # Deprecated but kept for backwards compatibility
    JOUVE = "jouve"
    USER_PROFILING = "user_profiling"


IDENTITY_CHECK_TYPES = [FraudCheckType.JOUVE, FraudCheckType.DMS, FraudCheckType.UBBLE, FraudCheckType.EDUCONNECT]


class FraudReasonCode(enum.Enum):
    # Common to all fraud checks
    AGE_NOT_VALID = "age_is_not_valid"
    DUPLICATE_USER = "duplicate_user"
    EMAIL_NOT_VALIDATED = "email_not_validated"
    MISSING_REQUIRED_DATA = "missing_required_data"
    NAME_INCORRECT = "name_incorrect"  # The user's name contains unaccepted characters
    NOT_ELIGIBLE = "not_eligible"

    # Specific to DMS
    EMPTY_ID_PIECE_NUMBER = "empty_id_piece_number"
    ERROR_IN_DATA = "error_in_data"  # The user's data has not passed our API validation
    REFUSED_BY_OPERATOR = "refused_by_operator"

    # Specific to Ubble
    # Ubble native errors
    BLURRY_DOCUMENT_VIDEO = "blurry_video"
    DOCUMENT_DAMAGED = "document_damaged"
    ELIGIBILITY_CHANGED = "eligibility_changed"  # The user's eligibility detected by ubble is different from the eligibility declared by the user
    ID_CHECK_BLOCKED_OTHER = (
        "id_check_blocked_other"  # Default reason code when the user's ID check is blocked for an unhandled reason
    )
    ID_CHECK_DATA_MATCH = "id_check_data_match"  # Ubble check did not match the data declared in the app (profile step)
    ID_CHECK_EXPIRED = "id_check_expired"
    ID_CHECK_NOT_AUTHENTIC = "id_check_not_authentic"
    ID_CHECK_NOT_SUPPORTED = "id_check_not_supported"
    ID_CHECK_UNPROCESSABLE = "id_check_unprocessable"
    INVALID_ID_PIECE_NUMBER = "invalid_id_piece_number"
    LACK_OF_LUMINOSITY = "lack_of_luminosity"
    NETWORK_CONNECTION_ISSUE = "network_connection_issue"
    NOT_DOCUMENT_OWNER = "not_document_owner"
    UBBLE_INTERNAL_ERROR = "ubble_internal_error"

    # Our API errors
    AGE_TOO_OLD = "age_too_old"
    AGE_TOO_YOUNG = "age_too_young"
    DUPLICATE_ID_PIECE_NUMBER = "duplicate_id_piece_number"

    # Specific to Educonnect
    DUPLICATE_INE = "duplicate_ine"

    # Specific to Phone Validation
    BLACKLISTED_PHONE_NUMBER = "blacklisted_phone_number"
    INVALID_PHONE_COUNTRY_CODE = "invalid_phone_country_code"
    PHONE_ALREADY_EXISTS = "phone_already_exists"
    PHONE_UNVALIDATED_BY_PEER = "phone_unvalidated_by_peer"
    PHONE_UNVALIDATION_FOR_PEER = "phone_unvalidation_for_peer"
    PHONE_VALIDATION_ATTEMPTS_LIMIT_REACHED = "phone_validation_attempts_limit_reached"
    SMS_SENDING_LIMIT_REACHED = "sms_sending_limit_reached"

    # Deprecated, kept for backward compatibility
    ALREADY_BENEFICIARY = "already_beneficiary"
    ALREADY_HAS_ACTIVE_DEPOSIT = "already_has_active_deposit"
    ID_CHECK_INVALID = "id_check_invalid"
    INE_NOT_WHITELISTED = "ine_not_whitelisted"
    PHONE_NOT_VALIDATED = "phone_not_validated"


class FraudReviewStatus(enum.Enum):
    KO = "KO"
    OK = "OK"
    REDIRECTED_TO_DMS = "REDIRECTED_TO_DMS"


class FraudCheckStatus(enum.Enum):
    CANCELED = "canceled"
    ERROR = "error"
    KO = "ko"
    OK = "ok"
    PENDING = "pending"
    STARTED = "started"
    SUSPICIOUS = "suspiscious"


VALID_IDENTITY_CHECK_TYPES_AFTER_UNDERAGE_DEPOSIT_EXPIRATION = [
    FraudCheckType.DMS,
    FraudCheckType.UBBLE,
]


FraudCheckContent = typing.Union[
    "BonusCreditContent",
    "DMSContent",
    "EduconnectContent",
    "UbbleContent",
    "ProfileCompletionContent",
    "HonorStatementContent",
    "PhoneValidationFraudData",
    # Deprecated. We keep USER_PROFILING for backward compatibility.
    "JouveContent",
    "UserProfilingFraudData",
]


def get_fraud_check_content_mapping() -> dict[FraudCheckType, type[FraudCheckContent]]:
    from pcapi.core.subscription.bonus.schemas import BonusCreditContent
    from pcapi.core.subscription.dms.schemas import DMSContent
    from pcapi.core.subscription.educonnect.schemas import EduconnectContent
    from pcapi.core.subscription.jouve.schemas import JouveContent
    from pcapi.core.subscription.schemas import HonorStatementContent
    from pcapi.core.subscription.schemas import PhoneValidationFraudData
    from pcapi.core.subscription.schemas import ProfileCompletionContent
    from pcapi.core.subscription.schemas import UserProfilingFraudData
    from pcapi.core.subscription.ubble.schemas import UbbleContent

    return {
        FraudCheckType.BONUS_CREDIT: BonusCreditContent,
        FraudCheckType.PROFILE_COMPLETION: ProfileCompletionContent,
        FraudCheckType.DMS: DMSContent,
        FraudCheckType.EDUCONNECT: EduconnectContent,
        FraudCheckType.HONOR_STATEMENT: HonorStatementContent,
        FraudCheckType.INTERNAL_REVIEW: PhoneValidationFraudData,
        FraudCheckType.PHONE_VALIDATION: PhoneValidationFraudData,
        FraudCheckType.UBBLE: UbbleContent,
        # Deprecated. Kept for backward compatibility.
        FraudCheckType.USER_PROFILING: UserProfilingFraudData,
        FraudCheckType.JOUVE: JouveContent,
    }


class BeneficiaryFraudCheck(PcObject, Model):
    __tablename__ = "beneficiary_fraud_check"

    dateCreated: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, server_default=sa.func.now(), default=date_utils.get_naive_utc_now
    )
    # The eligibility is null when the user is not eligible
    eligibilityType: sa_orm.Mapped[users_models.EligibilityType | None] = sa_orm.mapped_column(
        MagicEnum(users_models.EligibilityType, use_values=False), nullable=True
    )
    idPicturesStored: sa_orm.Mapped[bool | None] = sa_orm.mapped_column(sa.Boolean(), nullable=True)
    reason: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    reasonCodes: sa_orm.Mapped[list[FraudReasonCode] | None] = sa_orm.mapped_column(
        postgresql.ARRAY(sa.Enum(FraudReasonCode, create_constraint=False, native_enum=False)), nullable=True
    )
    resultContent: sa_orm.Mapped[dict | None] = sa_orm.mapped_column(
        sa.ext.mutable.MutableDict.as_mutable(sa.dialects.postgresql.JSONB(none_as_null=True)), nullable=True
    )
    status: sa_orm.Mapped[FraudCheckStatus | None] = sa_orm.mapped_column(
        MagicEnum(FraudCheckStatus, use_values=False), nullable=True
    )
    thirdPartyId: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.TEXT(), index=True, nullable=False)
    type: sa_orm.Mapped[FraudCheckType] = sa_orm.mapped_column(
        MagicEnum(FraudCheckType, use_values=False), nullable=False
    )
    updatedAt: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(
        sa.DateTime, nullable=True, default=date_utils.get_naive_utc_now, onupdate=sa.func.now()
    )
    userId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=False
    )
    user: sa_orm.Mapped[users_models.User] = sa_orm.relationship(
        "User", foreign_keys=[userId], back_populates="beneficiaryFraudChecks"
    )

    __table_args__ = (
        sa.Index(
            "ix_beneficiary_fraud_check_type_initiated_status",
            "id",
            "type",
            postgresql_where=sa.or_(status == FraudCheckStatus.STARTED, status == FraudCheckStatus.PENDING),
        ),
    )

    def get_detailed_source(self) -> str:
        if self.type == FraudCheckType.DMS.value:
            return f"démarches simplifiées dossier [{self.thirdPartyId}]"
        return f"dossier {self.type} [{self.thirdPartyId}]"

    def get_min_date_between_creation_and_registration(self) -> datetime.datetime:
        from pcapi.core.subscription.schemas import IdentityCheckContent

        if self.type not in IDENTITY_CHECK_TYPES or not self.resultContent:
            return self.dateCreated

        source_data = self.source_data()
        if not isinstance(source_data, IdentityCheckContent):
            return self.dateCreated

        try:
            registration_datetime = source_data.get_registration_datetime()
        except ValueError:
            # TODO(viconnex) migrate Educonnect fraud checks that do not have registration date in their content
            return self.dateCreated
        if registration_datetime:
            return min(self.dateCreated, registration_datetime)
        return self.dateCreated

    def get_identity_check_birth_date(self) -> datetime.date | None:
        from pcapi.core.subscription.schemas import IdentityCheckContent

        if self.type not in IDENTITY_CHECK_TYPES or not self.resultContent:
            return None

        source_data = self.source_data()
        if not isinstance(source_data, IdentityCheckContent):
            return self.dateCreated

        return source_data.get_birth_date()

    def source_data(self) -> FraudCheckContent:
        cls = get_fraud_check_content_mapping()[self.type]
        if not cls:
            raise NotImplementedError(f"Cannot unserialize type {self.type}")
        if self.resultContent is None or not isinstance(self.resultContent, dict):
            raise ValueError("No source data associated with this fraud check")
        return cls(**self.resultContent)

    @property
    def applicable_eligibilities(self) -> list[users_models.EligibilityType]:
        """
        A fraud check entry is always related to the eligibility for the single credit requested by the user at this
        time. However, id check may be valid for the next eligibility: the same user does not have to prove his/her
        identity again. Extended eligibility of a previous id check should not be considered as an action made in the
        subscription process once eligibility period has ended.
        """
        if self.is_id_check_ok_across_eligibilities_or_age:
            return [
                users_models.EligibilityType.UNDERAGE,
                users_models.EligibilityType.AGE18,
                users_models.EligibilityType.AGE17_18,
            ]

        return [self.eligibilityType] if self.eligibilityType else []

    @property
    def is_id_check_ok_across_eligibilities_or_age(self) -> bool:
        return (
            self.type in (FraudCheckType.UBBLE, FraudCheckType.DMS)
            and self.status == FraudCheckStatus.OK
            and self.eligibilityType in [users_models.EligibilityType.UNDERAGE, users_models.EligibilityType.AGE17_18]
            and (
                self.user.has_beneficiary_role
                or (self.user.age is not None and self.user.age >= users_constants.ELIGIBILITY_AGE_18)
            )
        )


class OrphanDmsApplication(PcObject, Model):
    # This model is used to store fraud checks that were not associated with a user.
    # This is mainly used for the DMS fraud check, when the user is not yet created, or in case of a failure.
    __tablename__ = "orphan_dms_application"
    application_id: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, primary_key=True, nullable=False
    )  # refers to DMS application "number"
    dateCreated: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(
        sa.DateTime, nullable=True, default=date_utils.get_naive_utc_now
    )  # no sql default because the column was added after table creation
    email: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True, index=True)
    latest_modification_datetime: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(
        sa.DateTime, nullable=True
    )  # This field copies the value provided in the DMS application
    process_id: sa_orm.Mapped[int | None] = sa_orm.mapped_column(sa.BigInteger, nullable=True)


class BeneficiaryFraudReview(PcObject, Model):
    __tablename__ = "beneficiary_fraud_review"
    authorId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=False
    )
    author: sa_orm.Mapped[users_models.User] = sa_orm.relationship(
        "User", foreign_keys=[authorId], back_populates="adminFraudReviews"
    )
    dateReviewed: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, server_default=sa.func.now()
    )
    eligibilityType: sa_orm.Mapped[users_models.EligibilityType | None] = sa_orm.mapped_column(
        sa.Enum(users_models.EligibilityType, create_constraint=False), nullable=True
    )
    reason: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    review: sa_orm.Mapped[FraudReviewStatus | None] = sa_orm.mapped_column(
        sa.Enum(FraudReviewStatus, create_constraint=False), nullable=True
    )
    userId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=False
    )
    user: sa_orm.Mapped[users_models.User] = sa_orm.relationship(
        "User", foreign_keys=[userId], back_populates="beneficiaryFraudReviews"
    )
