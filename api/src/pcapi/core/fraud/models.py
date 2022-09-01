import dataclasses
import datetime
import enum
import typing

import pydantic
from pydantic.class_validators import validator
import pydantic.datetime_parse
import pydantic.errors
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from pcapi.connectors.dms import models as dms_models
from pcapi.core.users import models as users_models
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject

from .common import models as common_models
from .ubble import models as ubble_fraud_models


class FraudCheckType(enum.Enum):
    DMS = "dms"
    EDUCONNECT = "educonnect"
    HONOR_STATEMENT = "honor_statement"
    INTERNAL_REVIEW = "internal_review"
    JOUVE = "jouve"
    PHONE_VALIDATION = "phone_validation"
    PROFILE_COMPLETION = "profile_completion"
    UBBLE = "ubble"
    USER_PROFILING = "user_profiling"


IDENTITY_CHECK_TYPES = [FraudCheckType.JOUVE, FraudCheckType.DMS, FraudCheckType.UBBLE, FraudCheckType.EDUCONNECT]


class FraudStatus(enum.Enum):
    OK = "OK"
    KO = "KO"
    SUSPICIOUS = "SUSPICIOUS"
    SUBSCRIPTION_ON_HOLD = "SUBSCRIPTION_ON_HOLD"  # todo : find a name


class FraudReviewStatus(enum.Enum):
    OK = "OK"
    KO = "KO"
    REDIRECTED_TO_DMS = "REDIRECTED_TO_DMS"


def _parse_level(level: str | None) -> int | None:
    if not level:
        return None
    try:
        return int(level)
    except ValueError:
        return None


def _parse_jouve_date(date: str | None) -> datetime.datetime | None:
    if not date:
        return None
    # this function has to support two parsings string format:
    # 1. the "classical" format such as "year/month/day" which is expressed when calling .dict()
    # 2. jouve format, when parsing incoming data
    try:
        return pydantic.datetime_parse.parse_datetime(date)
    except pydantic.DateTimeError:
        pass

    try:
        return datetime.datetime.strptime(date, "%d/%m/%Y")
    except ValueError:
        pass

    try:
        return datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return None


def _parse_jouve_datetime(date: str | None) -> datetime.datetime | None:
    if not date:
        return None
    try:
        return pydantic.datetime_parse.parse_datetime(date)
    except pydantic.DateTimeError:
        pass
    try:
        return datetime.datetime.strptime(date, "%m/%d/%Y %H:%M %p")  # production format
    except ValueError:
        pass
    try:
        return datetime.datetime.strptime(date, "%d/%m/%Y %H:%M")  # testing format
    except ValueError:
        return None


class EduconnectContent(common_models.IdentityCheckContent):
    birth_date: datetime.date
    educonnect_id: str
    first_name: str
    ine_hash: str
    last_name: str
    registration_datetime: datetime.datetime
    school_uai: str | None
    student_level: str | None

    def get_registration_datetime(self) -> datetime.datetime:
        return self.registration_datetime

    def get_first_name(self) -> str:
        return self.first_name

    def get_last_name(self) -> str:
        return self.last_name

    def get_birth_date(self) -> datetime.date:
        return self.birth_date

    def get_ine_hash(self) -> str | None:
        return self.ine_hash


class JouveContent(common_models.IdentityCheckContent):
    activity: str | None
    address: str | None
    birthDateTxt: datetime.datetime | None
    birthLocationCtrl: str | None
    bodyBirthDateCtrl: str | None
    bodyBirthDateLevel: int | None
    bodyFirstnameCtrl: str | None
    bodyFirstnameLevel: int | None
    bodyNameLevel: int | None
    bodyNameCtrl: str | None
    bodyPieceNumber: str | None
    bodyPieceNumberCtrl: str | None
    bodyPieceNumberLevel: int | None
    city: str | None
    creatorCtrl: str | None
    id: int
    email: str | None
    firstName: str | None
    gender: str | None
    initialNumberCtrl: str | None
    initialSizeCtrl: str | None
    lastName: str | None
    phoneNumber: str | None
    postalCode: str | None
    posteCodeCtrl: str | None
    registrationDate: datetime.datetime | None
    serviceCodeCtrl: str | None

    _parse_body_birth_date_level = validator("bodyBirthDateLevel", pre=True, allow_reuse=True)(_parse_level)
    _parse_body_first_name_level = validator("bodyFirstnameLevel", pre=True, allow_reuse=True)(_parse_level)
    _parse_body_name_level = validator("bodyNameLevel", pre=True, allow_reuse=True)(_parse_level)
    _parse_body_piece_number_level = validator("bodyPieceNumberLevel", pre=True, allow_reuse=True)(_parse_level)
    _parse_birth_date = validator("birthDateTxt", pre=True, allow_reuse=True)(_parse_jouve_date)
    _parse_registration_date = validator("registrationDate", pre=True, allow_reuse=True)(_parse_jouve_datetime)

    def get_registration_datetime(self) -> datetime.datetime | None:
        return self.registrationDate

    def get_first_name(self) -> str | None:
        return self.firstName

    def get_last_name(self) -> str | None:
        return self.lastName

    def get_married_name(self) -> None:
        return None

    def get_birth_date(self) -> datetime.date | None:
        return self.birthDateTxt.date() if self.birthDateTxt else None

    def get_id_piece_number(self) -> str | None:
        return self.bodyPieceNumber


class DMSContent(common_models.IdentityCheckContent):
    activity: str | None
    address: str | None
    application_number: int = pydantic.Field(..., alias="application_id")  # keep alias for old data
    birth_date: datetime.date | None
    city: str | None
    civility: users_models.GenderEnum | None
    deletion_datetime: datetime.datetime | None
    department: str | None  # this field is not filled anymore
    email: str
    first_name: str
    id_piece_number: str | None
    last_name: str
    latest_modification_datetime: datetime.datetime | None
    phone: str | None
    postal_code: str | None
    procedure_number: int = pydantic.Field(..., alias="procedure_id")  # keep alias for old data
    processed_datetime: datetime.datetime | None
    registration_datetime: datetime.datetime | None
    state: str | None

    class Config:
        allow_population_by_field_name = True

    def get_birth_date(self) -> datetime.date | None:
        return self.birth_date

    def get_first_name(self) -> str:
        return self.first_name

    def get_last_name(self) -> str:
        return self.last_name

    def get_activity(self) -> str | None:
        return self.activity

    def get_address(self) -> str | None:
        return self.address

    def get_civility(self) -> str | None:
        return self.civility.value if self.civility else None

    def get_city(self) -> str | None:
        return self.city

    def get_id_piece_number(self) -> str | None:
        return self.id_piece_number

    def get_phone_number(self) -> str | None:
        return self.phone

    def get_postal_code(self) -> str | None:
        return self.postal_code

    def get_registration_datetime(self) -> datetime.datetime | None:
        return dms_models.parse_dms_datetime(self.registration_datetime) if self.registration_datetime else None

    def get_latest_modification_datetime(self) -> datetime.datetime | None:
        return self.latest_modification_datetime


class UserProfilingRiskRating(enum.Enum):
    TRUSTED = "trusted"
    NEUTRAL = "neutral"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class UserProfilingFraudData(pydantic.BaseModel):
    account_email: str
    account_email_first_seen: datetime.date | None
    account_email_result: str
    account_email_score: int | None
    account_telephone_result: str | None  # Optional because Phone Validation may be disabled by FF
    account_telephone_first_seen: datetime.date | None
    account_telephone_score: int | None
    account_telephone_is_valid: str | None  # Optional because Phone Validation may be disabled by FF
    bb_bot_rating: str
    bb_bot_score: float
    bb_fraud_rating: str
    bb_fraud_score: float
    device_id: str | None
    digital_id: str
    digital_id_result: str
    digital_id_trust_score: float
    digital_id_trust_score_rating: str
    digital_id_trust_score_reason_code: typing.List[str]
    digital_id_confidence: int
    digital_id_confidence_rating: str
    event_datetime: datetime.datetime
    policy_score: int
    reason_code: typing.List[str]
    request_id: str
    risk_rating: UserProfilingRiskRating
    session_id: str
    tmx_risk_rating: str
    tmx_summary_reason_code: typing.List[str] | None
    summary_risk_score: int
    unknown_session: str | None


IdCheckContent = typing.TypeVar(
    "IdCheckContent",
    DMSContent,
    EduconnectContent,
    JouveContent,
    ubble_fraud_models.UbbleContent,
    UserProfilingFraudData,
)


class InternalReviewSource(enum.Enum):
    SMS_SENDING_LIMIT_REACHED = "sms_sending_limit_reached"
    PHONE_VALIDATION_ATTEMPTS_LIMIT_REACHED = "phone_validation_attempts_limit_reached"
    PHONE_ALREADY_EXISTS = "phone_already_exists"
    BLACKLISTED_PHONE_NUMBER = "blacklisted_phone_number"
    DOCUMENT_VALIDATION_ERROR = "document_validation_error"


class PhoneValidationFraudData(pydantic.BaseModel):
    source: InternalReviewSource | None  # legacy field, still present in database
    message: str | None  # legacy field, still present in database
    phone_number: str | None


class ProfileCompletionContent(pydantic.BaseModel):
    activity: str
    city: str
    first_name: str
    last_name: str
    origin: str  # Where the profile was completed by the user. Can be the APP or DMS
    postalCode: str
    school_type: users_models.SchoolTypeEnum | None


FRAUD_CHECK_MAPPING = {
    FraudCheckType.DMS: DMSContent,
    FraudCheckType.EDUCONNECT: EduconnectContent,
    FraudCheckType.INTERNAL_REVIEW: PhoneValidationFraudData,
    FraudCheckType.JOUVE: JouveContent,
    FraudCheckType.PHONE_VALIDATION: PhoneValidationFraudData,
    FraudCheckType.PROFILE_COMPLETION: ProfileCompletionContent,
    FraudCheckType.UBBLE: ubble_fraud_models.UbbleContent,
    FraudCheckType.USER_PROFILING: UserProfilingFraudData,
}

FRAUD_CONTENT_MAPPING = {type: cls for cls, type in FRAUD_CHECK_MAPPING.items()}


class FraudReasonCode(enum.Enum):
    ALREADY_BENEFICIARY = "already_beneficiary"
    ALREADY_HAS_ACTIVE_DEPOSIT = "already_has_active_deposit"
    AGE_NOT_VALID = "age_is_not_valid"
    AGE_TOO_OLD = "age_too_old"
    AGE_TOO_YOUNG = "age_too_young"
    BLACKLISTED_PHONE_NUMBER = "blacklisted_phone_number"
    DUPLICATE_ID_PIECE_NUMBER = "duplicate_id_piece_number"
    DUPLICATE_INE = "duplicate_ine"
    DUPLICATE_USER = "duplicate_user"
    EMAIL_NOT_VALIDATED = "email_not_validated"
    ELIGIBILITY_CHANGED = "eligibility_changed"
    EMPTY_ID_PIECE_NUMBER = "empty_id_piece_number"
    ERROR_IN_DATA = "error_in_data"
    ID_CHECK_DATA_MATCH = "id_check_data_match"
    ID_CHECK_EXPIRED = "id_check_expired"
    ID_CHECK_INVALID = "id_check_invalid"
    ID_CHECK_BLOCKED_OTHER = "id_check_bocked_other"
    ID_CHECK_NOT_AUTHENTIC = "id_check_not_authentic"
    ID_CHECK_NOT_SUPPORTED = "id_check_not_supported"
    ID_CHECK_UNPROCESSABLE = "id_check_unprocessable"
    INVALID_ID_PIECE_NUMBER = "invalid_id_piece_number"
    INVALID_PHONE_COUNTRY_CODE = "invalid_phone_country_code"
    INE_NOT_WHITELISTED = "ine_not_whitelisted"  # the value is kept because it still exists in the database
    MISSING_REQUIRED_DATA = "missing_required_data"
    NAME_INCORRECT = "name_incorrect"
    NOT_ELIGIBLE = "not_eligible"
    PHONE_ALREADY_EXISTS = "phone_already_exists"
    PHONE_NOT_VALIDATED = "phone_not_validated"
    PHONE_UNVALIDATED_BY_PEER = "phone_unvalidated_by_peer"
    PHONE_UNVALIDATION_FOR_PEER = "phone_unvalidation_for_peer"
    PHONE_VALIDATION_ATTEMPTS_LIMIT_REACHED = "phone_validation_attempts_limit_reached"
    REFUSED_BY_OPERATOR = "refused_by_operator"
    SMS_SENDING_LIMIT_REACHED = "sms_sending_limit_reached"


# FIXME: ce status fait un peu doublon avec FraudStatus
#  il faudra probablement en supprimer un quand le refacto du parcours
#  d'inscription sera terminé
class FraudCheckStatus(enum.Enum):
    KO = "ko"
    OK = "ok"
    STARTED = "started"
    SUSPICIOUS = "suspiscious"
    PENDING = "pending"
    CANCELED = "canceled"
    ERROR = "error"


class BeneficiaryFraudCheck(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    __tablename__ = "beneficiary_fraud_check"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    dateCreated = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now(), default=datetime.datetime.utcnow)

    userId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=False)

    user = sa.orm.relationship("User", foreign_keys=[userId], backref="beneficiaryFraudChecks")  # type: ignore [misc]

    type = sa.Column(sa.Enum(FraudCheckType, create_constraint=False), nullable=False)

    thirdPartyId = sa.Column(sa.TEXT(), nullable=False)

    resultContent = sa.Column(sa.dialects.postgresql.JSONB(none_as_null=True))

    status = sa.Column(sa.Enum(FraudCheckStatus, create_constraint=False), nullable=True)

    reason = sa.Column(sa.Text, nullable=True)

    reasonCodes = sa.Column(
        postgresql.ARRAY(sa.Enum(FraudReasonCode, create_constraint=False, native_enum=False)),
        nullable=True,
    )

    # The eligibility is null when the user is not eligible
    eligibilityType = sa.Column(
        sa.Enum(users_models.EligibilityType, create_constraint=False),
        nullable=True,
    )

    idPicturesStored = sa.Column(
        sa.Boolean(),
        nullable=True,
    )

    def source_data(self) -> common_models.IdentityCheckContent | UserProfilingFraudData:
        if self.type not in FRAUD_CHECK_MAPPING:
            raise NotImplementedError(f"Cannot unserialize type {self.type}")
        if self.resultContent is None:
            raise ValueError("No source data associated with this fraud check")
        return FRAUD_CHECK_MAPPING[self.type](**self.resultContent)  # type: ignore [arg-type]

    def get_detailed_source(self) -> str:
        if self.type == FraudCheckType.DMS.value:
            return f"démarches simplifiées dossier [{self.thirdPartyId}]"
        return f"dossier {self.type} [{self.thirdPartyId}]"

    def get_min_date_between_creation_and_registration(self) -> datetime.datetime:
        if self.type not in IDENTITY_CHECK_TYPES or not self.resultContent:
            return self.dateCreated  # type: ignore [return-value]
        try:
            registration_datetime = self.source_data().get_registration_datetime()  # type: ignore [union-attr]
        except ValueError:  # TODO(viconnex) migrate Educonnect fraud checks that do not have registration date in their content
            return self.dateCreated  # type: ignore [return-value]
        if registration_datetime:
            return min(self.dateCreated, registration_datetime)  # type: ignore [type-var, return-value]
        return self.dateCreated  # type: ignore [return-value]

    @property
    def applicable_eligibilities(self) -> list[users_models.EligibilityType]:
        if (
            self.type == FraudCheckType.UBBLE
            and self.status == FraudCheckStatus.OK
            and self.eligibilityType == users_models.EligibilityType.UNDERAGE
        ):
            return [users_models.EligibilityType.UNDERAGE, users_models.EligibilityType.AGE18]

        return [self.eligibilityType] if self.eligibilityType else []


class OrphanDmsApplication(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    # This model is used to store fraud checks that were not associated with a user.
    # This is mainly used for the DMS fraud check, when the user is not yet created, or in case of a failure.
    dateCreated = sa.Column(
        sa.DateTime, nullable=True, default=datetime.datetime.utcnow
    )  # no sql default because the column was added after table creation
    latest_modification_datetime = sa.Column(
        sa.DateTime, nullable=True
    )  # This field copies the value provided in the DMS application
    email = sa.Column(sa.Text, nullable=True, index=True)
    application_id = sa.Column(sa.BigInteger, primary_key=True)  # refers to DMS application "number"
    process_id = sa.Column(sa.BigInteger)


class BeneficiaryFraudReview(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    __tablename__ = "beneficiary_fraud_review"

    userId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=False)

    user = sa.orm.relationship("User", foreign_keys=[userId], backref=sa.orm.backref("beneficiaryFraudReviews"))  # type: ignore [misc]

    authorId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=False)

    author = sa.orm.relationship("User", foreign_keys=[authorId], backref="adminFraudReviews")  # type: ignore [misc]

    review = sa.Column(sa.Enum(FraudReviewStatus, create_constraint=False))

    dateReviewed = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    reason = sa.Column(sa.Text)


@dataclasses.dataclass
class FraudItem:
    status: FraudStatus
    detail: str
    reason_code: FraudReasonCode | None = None

    def __bool__(self) -> bool:
        return self.status == FraudStatus.OK
