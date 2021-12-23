import dataclasses
import datetime
import enum
import typing

import pydantic
from pydantic.class_validators import validator
import pydantic.datetime_parse
import pydantic.errors
import pytz
import sqlalchemy.dialects.postgresql
import sqlalchemy.orm

from pcapi.core.users import models as users_models
from pcapi.models import Model
from pcapi.models.pc_object import PcObject

from . import ubble as ubble_models
from .common import IdentityCheckContent


class FraudCheckType(enum.Enum):
    JOUVE = "jouve"
    USER_PROFILING = "user_profiling"
    DMS = "dms"
    INTERNAL_REVIEW = "internal_review"
    EDUCONNECT = "educonnect"
    UBBLE = "ubble"
    HONOR_STATEMENT = "honor_statement"


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


def _parse_level(level: typing.Optional[str]) -> typing.Optional[int]:
    if not level:
        return None
    try:
        return int(level)
    except ValueError:
        return None


def _parse_jouve_date(date: typing.Optional[str]) -> typing.Optional[datetime.datetime]:
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
        return None


def _parse_jouve_datetime(date: typing.Optional[str]) -> typing.Optional[datetime.datetime]:
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


class EduconnectContent(IdentityCheckContent):
    birth_date: datetime.date
    educonnect_id: str
    first_name: str
    ine_hash: str
    last_name: str
    registration_datetime: datetime.datetime
    school_uai: typing.Optional[str]
    student_level: typing.Optional[str]

    def get_registration_datetime(self) -> datetime.datetime:
        return self.registration_datetime

    def get_birth_date(self) -> datetime.date:
        return self.birth_date


class JouveContent(IdentityCheckContent):
    # TODO: analyze jouve results to see where we can remove "optional"
    activity: typing.Optional[str]
    address: typing.Optional[str]
    birthDateTxt: typing.Optional[datetime.datetime]
    birthLocationCtrl: typing.Optional[str]
    bodyBirthDateCtrl: typing.Optional[str]
    bodyBirthDateLevel: typing.Optional[int]
    bodyFirstnameCtrl: typing.Optional[str]
    bodyFirstnameLevel: typing.Optional[int]
    bodyNameLevel: typing.Optional[int]
    bodyNameCtrl: typing.Optional[str]
    bodyPieceNumber: typing.Optional[str]
    bodyPieceNumberCtrl: typing.Optional[str]
    bodyPieceNumberLevel: typing.Optional[int]
    city: typing.Optional[str]
    creatorCtrl: typing.Optional[str]
    id: int
    email: typing.Optional[str]
    firstName: typing.Optional[str]
    gender: typing.Optional[str]
    initialNumberCtrl: typing.Optional[str]
    initialSizeCtrl: typing.Optional[str]
    lastName: typing.Optional[str]
    phoneNumber: typing.Optional[str]
    postalCode: typing.Optional[str]
    posteCodeCtrl: typing.Optional[str]
    registrationDate: typing.Optional[datetime.datetime]
    serviceCodeCtrl: typing.Optional[str]

    _parse_body_birth_date_level = validator("bodyBirthDateLevel", pre=True, allow_reuse=True)(_parse_level)
    _parse_body_first_name_level = validator("bodyFirstnameLevel", pre=True, allow_reuse=True)(_parse_level)
    _parse_body_name_level = validator("bodyNameLevel", pre=True, allow_reuse=True)(_parse_level)
    _parse_body_piece_number_level = validator("bodyPieceNumberLevel", pre=True, allow_reuse=True)(_parse_level)
    _parse_birth_date = validator("birthDateTxt", pre=True, allow_reuse=True)(_parse_jouve_date)
    _parse_registration_date = validator("registrationDate", pre=True, allow_reuse=True)(_parse_jouve_datetime)

    def get_registration_datetime(self) -> typing.Optional[datetime.datetime]:
        return self.registrationDate

    def get_birth_date(self) -> typing.Optional[datetime.date]:
        return self.birthDateTxt.date() if self.birthDateTxt else None


class DMSContent(IdentityCheckContent):
    last_name: str
    first_name: str
    civility: str
    email: str
    application_id: int
    procedure_id: int
    department: typing.Optional[str]
    birth_date: typing.Optional[datetime.date]
    phone: typing.Optional[str]
    postal_code: typing.Optional[str]
    activity: typing.Optional[str]
    address: typing.Optional[str]
    id_piece_number: typing.Optional[str]
    registration_datetime: typing.Optional[datetime.datetime]

    def get_registration_datetime(self) -> typing.Optional[datetime.datetime]:
        return (
            self.registration_datetime.astimezone(pytz.utc).replace(tzinfo=None) if self.registration_datetime else None
        )

    def get_birth_date(self) -> datetime.date:
        return self.birth_date


class UserProfilingRiskRating(enum.Enum):
    TRUSTED = "trusted"
    NEUTRAL = "neutral"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class UserProfilingFraudData(pydantic.BaseModel):
    account_email: str
    account_email_first_seen: typing.Optional[datetime.date]
    account_email_result: str
    account_email_score: typing.Optional[int]
    account_telephone_result: typing.Optional[str]  # Optional because Phone Validation may be disabled by FF
    account_telephone_first_seen: typing.Optional[datetime.date]
    account_telephone_score: typing.Optional[int]
    account_telephone_is_valid: typing.Optional[str]  # Optional because Phone Validation may be disabled by FF
    bb_bot_rating: str
    bb_bot_score: float
    bb_fraud_rating: str
    bb_fraud_score: float
    device_id: typing.Optional[str]
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
    tmx_summary_reason_code: typing.Optional[typing.List[str]]
    summary_risk_score: int
    unknown_session: typing.Optional[str]


IdCheckContent = typing.TypeVar(
    "IdCheckContent",
    DMSContent,
    EduconnectContent,
    JouveContent,
    ubble_models.UbbleContent,
    UserProfilingFraudData,
)


class InternalReviewSource(enum.Enum):
    SMS_SENDING_LIMIT_REACHED = "sms_sending_limit_reached"
    PHONE_VALIDATION_ATTEMPTS_LIMIT_REACHED = "phone_validation_attempts_limit_reached"
    PHONE_ALREADY_EXISTS = "phone_already_exists"
    BLACKLISTED_PHONE_NUMBER = "blacklisted_phone_number"
    DOCUMENT_VALIDATION_ERROR = "document_validation_error"


class InternalReviewFraudData(pydantic.BaseModel):
    source: InternalReviewSource
    message: str
    phone_number: typing.Optional[str]


FRAUD_CHECK_MAPPING = {
    FraudCheckType.DMS: DMSContent,
    FraudCheckType.USER_PROFILING: UserProfilingFraudData,
    FraudCheckType.JOUVE: JouveContent,
    FraudCheckType.INTERNAL_REVIEW: InternalReviewFraudData,
    FraudCheckType.EDUCONNECT: EduconnectContent,
    FraudCheckType.UBBLE: ubble_models.UbbleContent,
}

FRAUD_CONTENT_MAPPING = {type: cls for cls, type in FRAUD_CHECK_MAPPING.items()}


class FraudReasonCode(enum.Enum):
    ALREADY_BENEFICIARY = "already_beneficiary"
    ALREADY_HAS_ACTIVE_DEPOSIT = "already_has_active_deposit"
    AGE_NOT_VALID = "age_is_not_valid"
    DUPLICATE_ID_PIECE_NUMBER = "duplicate_id_piece_number"
    DUPLICATE_INE = "duplicate_ine"
    DUPLICATE_USER = "duplicate_user"
    EMAIL_NOT_VALIDATED = "email_not_validated"
    EMPTY_ID_PIECE_NUMBER = "empty_id_piece_number"
    ID_CHECK_INVALID = "id_check_invalid"
    ID_CHECK_UNPROCESSABLE = "id_check_unprocessable"
    INE_NOT_WHITELISTED = "ine_not_whitelisted"
    INVALID_ID_PIECE_NUMBER = "invalid_id_piece_number"
    PHONE_NOT_VALIDATED = "phone_not_validated"


# FIXME: ce status fait un peu doublon avec FraudStatus
#  il faudra probablement en supprimer un quand le refacto du parcours
#  d'inscription sera terminé
class FraudCheckStatus(enum.Enum):
    KO = "ko"
    OK = "ok"
    SUSPICIOUS = "suspiscious"
    PENDING = "pending"
    CANCELED = "canceled"


class BeneficiaryFraudCheck(PcObject, Model):
    __tablename__ = "beneficiary_fraud_check"

    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True, autoincrement=True)

    dateCreated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now())

    userId = sqlalchemy.Column(sqlalchemy.BigInteger, sqlalchemy.ForeignKey("user.id"), index=True, nullable=False)

    user = sqlalchemy.orm.relationship("User", foreign_keys=[userId], backref="beneficiaryFraudChecks")

    type = sqlalchemy.Column(sqlalchemy.Enum(FraudCheckType, create_constraint=False), nullable=False)

    thirdPartyId = sqlalchemy.Column(sqlalchemy.TEXT(), nullable=False)

    resultContent = sqlalchemy.Column(sqlalchemy.dialects.postgresql.JSONB)

    status = sqlalchemy.Column(sqlalchemy.Enum(FraudCheckStatus, create_constraint=False), nullable=True)

    reason = sqlalchemy.Column(sqlalchemy.Text, nullable=True)

    reasonCodes = sqlalchemy.Column(
        sqlalchemy.ARRAY(sqlalchemy.Enum(FraudReasonCode, create_constraint=False, native_enum=False)),
        nullable=True,
    )

    # Unlike BeneficiaryFraudResult, the eligibility is nullable here to support existing objects.
    # A script may fill in this column for past objects.
    eligibilityType = sqlalchemy.Column(
        sqlalchemy.Enum(users_models.EligibilityType, create_constraint=False),
        nullable=True,
    )

    def source_data(self) -> typing.Union[IdentityCheckContent, UserProfilingFraudData]:
        if self.type not in FRAUD_CHECK_MAPPING:
            raise NotImplementedError(f"Cannot unserialize type {self.type}")
        return FRAUD_CHECK_MAPPING[self.type](**self.resultContent)


class BeneficiaryFraudResult(PcObject, Model):
    __tablename__ = "beneficiary_fraud_result"

    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True, autoincrement=True)

    userId = sqlalchemy.Column(sqlalchemy.BigInteger, sqlalchemy.ForeignKey("user.id"), index=True, nullable=False)

    user = sqlalchemy.orm.relationship(
        "User", foreign_keys=[userId], backref=sqlalchemy.orm.backref("beneficiaryFraudResults")
    )

    eligibilityType = sqlalchemy.Column(
        sqlalchemy.Enum(users_models.EligibilityType, create_constraint=False),
        nullable=True,
    )

    status = sqlalchemy.Column(sqlalchemy.Enum(FraudStatus, create_constraint=False))

    reason = sqlalchemy.Column(sqlalchemy.Text)

    reason_codes = sqlalchemy.Column(
        sqlalchemy.ARRAY(sqlalchemy.Enum(FraudReasonCode, create_constraint=False, native_enum=False)),
        nullable=False,
        server_default="{}",
        default=[],
    )

    dateCreated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now())

    dateUpdated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, onupdate=sqlalchemy.func.now())


class BeneficiaryFraudReview(PcObject, Model):
    __tablename__ = "beneficiary_fraud_review"

    userId = sqlalchemy.Column(sqlalchemy.BigInteger, sqlalchemy.ForeignKey("user.id"), index=True, nullable=False)

    user = sqlalchemy.orm.relationship(
        "User", foreign_keys=[userId], backref=sqlalchemy.orm.backref("beneficiaryFraudReview", uselist=False)
    )

    authorId = sqlalchemy.Column(sqlalchemy.BigInteger, sqlalchemy.ForeignKey("user.id"), index=True, nullable=False)

    author = sqlalchemy.orm.relationship("User", foreign_keys=[authorId], backref="adminFraudReviews")

    review = sqlalchemy.Column(sqlalchemy.Enum(FraudReviewStatus, create_constraint=False))

    dateReviewed = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now())

    reason = sqlalchemy.Column(sqlalchemy.Text)


@dataclasses.dataclass
class FraudItem:
    status: FraudStatus
    detail: str
    reason_code: typing.Optional[FraudReasonCode] = None

    def __bool__(self) -> bool:
        return self.status == FraudStatus.OK


### TODO: remove after 15-17 test phase ###
class IneHashWhitelist(Model):
    ine_hash = sqlalchemy.Column(sqlalchemy.TEXT, nullable=False, primary_key=True)


### END ###
