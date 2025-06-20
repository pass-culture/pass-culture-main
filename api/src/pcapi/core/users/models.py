from __future__ import annotations  # to type models before their declaration

import enum
import typing
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import date
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from operator import attrgetter
from uuid import UUID

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy import func
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.sql import expression
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.elements import BooleanClauseList

from pcapi.connectors.dms import models as dms_models
from pcapi.core.finance.models import DepositType
from pcapi.core.geography.models import IrisFrance
from pcapi.core.users import constants
from pcapi.core.users import utils as users_utils
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.pc_object import PcObject
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.utils import crypto
from pcapi.utils import regions as regions_utils
from pcapi.utils.db import MagicEnum
from pcapi.utils.phone_number import ParsedPhoneNumber


if typing.TYPE_CHECKING:
    from pcapi.core.finance.models import Deposit
    from pcapi.core.offerers.models import UserOfferer
    from pcapi.core.offers.models import Offer
    from pcapi.core.permissions.models import BackOfficeUserProfile
    from pcapi.core.reactions.models import Reaction


VOID_FIRST_NAME = ""


class PhoneValidationStatusType(enum.Enum):
    SKIPPED_BY_SUPPORT = "skipped-by-support"
    UNVALIDATED = "unvalidated"
    VALIDATED = "validated"


class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    ANONYMIZED = "ANONYMIZED"
    BENEFICIARY = "BENEFICIARY"
    UNDERAGE_BENEFICIARY = "UNDERAGE_BENEFICIARY"
    FREE_BENEFICIARY = "FREE_BENEFICIARY"
    PRO = "PRO"
    NON_ATTACHED_PRO = "NON_ATTACHED_PRO"
    TEST = "TEST"  # used to mark imported test users on staging


class EligibilityType(enum.Enum):
    AGE17_18 = "age-17-18"
    FREE = "free"
    # legacy eligibilities that are present in the database
    UNDERAGE = "underage"
    AGE18 = "age-18"


@dataclass
class NotificationSubscriptions:
    marketing_push: bool = True
    marketing_email: bool = True
    subscribed_themes: list[str] = field(default_factory=list)


# calculate date of latest birthday
def _get_latest_birthday(birth_date: date | None) -> date | None:
    """
    Calculates the latest birthday of a given person.
    :param birth_date: The person's birthday.
    :return: The latest birthday's date.
    """
    if not birth_date:
        return None

    today = date.today()

    try:
        this_year_birthday = birth_date.replace(year=today.year)
    except ValueError:  # handle February 29
        this_year_birthday = birth_date.replace(year=today.year, day=28)
    try:
        previous_year_birthday = birth_date.replace(year=today.year - 1)
    except ValueError:  # handle February 29
        previous_year_birthday = birth_date.replace(year=today.year - 1, day=28)

    if this_year_birthday <= today:
        return this_year_birthday
    return previous_year_birthday


class ActivityEnum(enum.Enum):
    MIDDLE_SCHOOL_STUDENT = "Collégien"
    HIGH_SCHOOL_STUDENT = "Lycéen"
    STUDENT = "Étudiant"
    EMPLOYEE = "Employé"
    APPRENTICE = "Apprenti"
    APPRENTICE_STUDENT = "Alternant"
    VOLUNTEER = "Volontaire"
    INACTIVE = "Inactif"
    UNEMPLOYED = "Demandeur d'emploi"


class SchoolTypeEnum(enum.Enum):
    AGRICULTURAL_HIGH_SCHOOL = "Lycée agricole"
    APPRENTICE_FORMATION_CENTER = "Centre de formation d'apprentis"
    MILITARY_HIGH_SCHOOL = "Lycée militaire"
    HOME_OR_REMOTE_SCHOOLING = "Accompagnement spécialisé"
    NAVAL_HIGH_SCHOOL = "Lycée maritime"
    PRIVATE_HIGH_SCHOOL = "Lycée privé"
    PRIVATE_SECONDARY_SCHOOL = "Collège privé"
    PUBLIC_HIGH_SCHOOL = "Lycée public"
    PUBLIC_SECONDARY_SCHOOL = "Collège public"


class GenderEnum(enum.Enum):
    M = "M."
    F = "Mme"


class AccountState(enum.Enum):
    ACTIVE = "ACTIVE"
    ANONYMIZED = "ANONYMIZED"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    SUSPENDED_UPON_USER_REQUEST = "SUSPENDED_UPON_USER_REQUEST"
    SUSPICIOUS_LOGIN_REPORTED_BY_USER = "SUSPICIOUS_LOGIN_REPORTED_BY_USER"
    DELETED = "DELETED"
    WAITING_FOR_ANONYMIZATION = "WAITING_FOR_ANONYMIZATION"

    @property
    def is_deleted(self) -> bool:
        return self == AccountState.DELETED


class UserTagMapping(PcObject, Base, Model):
    __tablename__ = "user_tag_mapping"

    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)
    tagId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user_tag.id", ondelete="CASCADE"), index=True, nullable=False)

    __table_args__ = (sa.UniqueConstraint("userId", "tagId", name="unique_user_tag"),)


class User(PcObject, Base, Model, DeactivableMixin):
    __tablename__ = "user"

    activity = sa.Column(sa.String(128), nullable=True)
    address = sa.Column(sa.Text, nullable=True)
    city = sa.Column(sa.String(100), nullable=True)
    civility = sa.Column(sa.VARCHAR(length=20), nullable=True)
    comment = sa.Column(sa.Text(), nullable=True)
    culturalSurveyFilledDate = sa.Column(sa.DateTime, nullable=True)
    # culturalSurveyId is obsolete. the column is kept for backward compatibility with the existing data
    culturalSurveyId = sa.Column(postgresql.UUID(as_uuid=True), nullable=True)
    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)
    dateOfBirth = sa.Column(sa.DateTime, nullable=True)  # declared at signup
    departementCode = sa.Column(sa.String(3), nullable=True)
    discordUser: sa_orm.Mapped[DiscordUser] = sa_orm.relationship(
        "DiscordUser", uselist=False, back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    email: str = sa.Column(sa.String(120), nullable=False, unique=True)
    externalIds: dict = sa.Column(postgresql.json.JSONB, nullable=True, default={}, server_default="{}")
    extraData: dict = sa.Column(
        MutableDict.as_mutable(postgresql.json.JSONB), nullable=True, default={}, server_default="{}"
    )
    firstName = sa.Column(sa.String(128), nullable=True)
    hasSeenProTutorials: bool = sa.Column(sa.Boolean, nullable=False, server_default=expression.false())
    hasSeenProRgs: bool = sa.Column(sa.Boolean, nullable=False, server_default=expression.false())
    idPieceNumber = sa.Column(sa.String, nullable=True, unique=True)
    ineHash = sa.Column(sa.Text(), nullable=True, unique=True)
    irisFranceId = sa.Column(sa.BigInteger, sa.ForeignKey("iris_france.id"), nullable=True)
    irisFrance: sa_orm.Mapped[IrisFrance] = sa_orm.relationship(IrisFrance, foreign_keys=[irisFranceId])
    isEmailValidated = sa.Column(sa.Boolean, nullable=True, server_default=expression.false())
    lastConnectionDate = sa.Column(sa.DateTime, nullable=True)
    lastName = sa.Column(sa.String(128), nullable=True)
    married_name = sa.Column(sa.String(128), nullable=True)
    needsToFillCulturalSurvey = sa.Column(sa.Boolean, server_default=expression.true(), default=True)
    notificationSubscriptions: dict = sa.Column(
        MutableDict.as_mutable(postgresql.json.JSONB),
        nullable=True,
        default=asdict(NotificationSubscriptions()),
        server_default="""{"marketing_push": true, "marketing_email": true, "subscribed_themes": []}""",
    )
    password: bytes = sa.Column(sa.LargeBinary(60), nullable=True)
    _phoneNumber = sa.Column(sa.String(20), nullable=True, index=True, name="phoneNumber")
    phoneValidationStatus = sa.Column(sa.Enum(PhoneValidationStatusType, create_constraint=False), nullable=True)
    postalCode = sa.Column(sa.String(5), nullable=True)
    recreditAmountToShow = sa.Column(sa.Numeric(10, 2), nullable=True)
    UserOfferers: sa_orm.Mapped[list["UserOfferer"]] = sa_orm.relationship("UserOfferer", back_populates="user")
    roles: list[UserRole] = sa.Column(
        MutableList.as_mutable(postgresql.ARRAY(sa.Enum(UserRole, native_enum=False, create_constraint=False))),
        nullable=False,
        server_default="{}",
    )
    schoolType = sa.Column(sa.Enum(SchoolTypeEnum, create_constraint=False), nullable=True)
    trusted_devices: sa_orm.Mapped[list["TrustedDevice"]] = sa_orm.relationship("TrustedDevice", back_populates="user")
    login_device_history: sa_orm.Mapped[list["LoginDeviceHistory"]] = sa_orm.relationship(
        "LoginDeviceHistory", back_populates="user"
    )
    single_sign_ons: sa_orm.Mapped[list["SingleSignOn"]] = sa_orm.relationship(
        "SingleSignOn", back_populates="user", cascade="delete"
    )
    validatedBirthDate = sa.Column(sa.Date, nullable=True)  # validated by an Identity Provider
    backoffice_profile: sa_orm.Mapped["BackOfficeUserProfile"] = sa_orm.relationship(
        "BackOfficeUserProfile", uselist=False, back_populates="user"
    )
    sa.Index("ix_user_validatedBirthDate", validatedBirthDate)

    gdprUserDataExtracts: sa_orm.Mapped[list["GdprUserDataExtract"]] = sa_orm.relationship(
        "GdprUserDataExtract", back_populates="user", foreign_keys="GdprUserDataExtract.userId"
    )
    tags: sa_orm.Mapped[list["UserTag"]] = sa_orm.relationship("UserTag", secondary=UserTagMapping.__table__)
    reactions: sa_orm.Mapped[list["Reaction"]] = sa_orm.relationship("Reaction", back_populates="user", uselist=True)
    # unaccent is not immutable, so it can't be used for an index.
    # Searching by sa.func.unaccent(something) does not use the index and causes a sequential scan.
    # immutable_unaccent is a wrapper so that index uses an immutable function.
    # Note that unaccented indexes should be re-generated if we change internal dictionary used by Postgresql for
    # accents, which will probably never happen.
    __table_args__ = (
        sa.Index(
            "ix_user_trgm_unaccent_full_name",
            sa.func.immutable_unaccent(firstName + " " + lastName),
            postgresql_using="gin",
        ),
        # Index to be used with ORDER BY id LIMIT 21,
        # otherwise an index on the single email domain is not used by the query planner
        sa.Index("ix_user_email_domain_and_id", sa.func.email_domain(email), "id"),
    )

    def __init__(self, **kwargs: typing.Any) -> None:
        kwargs.setdefault("roles", [])
        super().__init__(**kwargs)

    def _add_role(self, role: UserRole) -> None:
        from pcapi.core.users.exceptions import InvalidUserRoleException

        if role in self.roles:
            return

        updated_roles = self.roles + [role]

        if (
            len(set(updated_roles) & {UserRole.ADMIN, UserRole.BENEFICIARY, UserRole.UNDERAGE_BENEFICIARY}) > 1
            or len(set(updated_roles) & {UserRole.PRO, UserRole.NON_ATTACHED_PRO}) > 1
        ):
            role_exception = InvalidUserRoleException()
            role_exception.add_error(
                "roles",
                "User can't have roles " + " and ".join(r.value for r in updated_roles),
            )
            raise role_exception

        self.roles = updated_roles

    def add_admin_role(self) -> None:
        self._add_role(UserRole.ADMIN)

    def add_beneficiary_role(self) -> None:
        self.remove_underage_beneficiary_role()
        self.remove_free_beneficiary_role()
        self._add_role(UserRole.BENEFICIARY)

    def add_underage_beneficiary_role(self) -> None:
        from pcapi.core.users.exceptions import InvalidUserRoleException

        if self.has_admin_role:
            role_exception = InvalidUserRoleException()
            role_exception.add_error(
                "roles",
                "User can't have both ADMIN and BENEFICIARY role",
            )
            raise role_exception

        self.remove_free_beneficiary_role()
        self._add_role(UserRole.UNDERAGE_BENEFICIARY)

    def add_free_beneficiary_role(self) -> None:
        self._add_role(UserRole.FREE_BENEFICIARY)

    def add_pro_role(self) -> None:
        self.remove_non_attached_pro_role()
        self._add_role(UserRole.PRO)

    def add_non_attached_pro_role(self) -> None:
        self.remove_pro_role()
        self._add_role(UserRole.NON_ATTACHED_PRO)

    def add_test_role(self) -> None:
        self._add_role(UserRole.TEST)

    def replace_roles_by_anonymized_role(self) -> None:
        self.roles = [UserRole.ANONYMIZED]

    def remove_admin_role(self) -> None:
        if self.has_admin_role:
            self.roles.remove(UserRole.ADMIN)

    def remove_underage_beneficiary_role(self) -> None:
        if self.has_underage_beneficiary_role:
            self.roles.remove(UserRole.UNDERAGE_BENEFICIARY)

    def remove_beneficiary_role(self) -> None:
        if self.has_beneficiary_role:
            self.roles.remove(UserRole.BENEFICIARY)

    def remove_free_beneficiary_role(self) -> None:
        if self.has_free_beneficiary_role:
            self.roles.remove(UserRole.FREE_BENEFICIARY)

    def remove_pro_role(self) -> None:
        if self.has_pro_role:
            self.roles.remove(UserRole.PRO)

    def remove_non_attached_pro_role(self) -> None:
        if self.has_non_attached_pro_role:
            self.roles.remove(UserRole.NON_ATTACHED_PRO)

    def checkPassword(self, passwordToCheck: str) -> bool:
        return crypto.check_password(passwordToCheck, self.password)

    def get_notification_subscriptions(self) -> NotificationSubscriptions:
        return NotificationSubscriptions(**self.notificationSubscriptions or {})

    def set_marketing_email_subscription(self, subscribe: bool) -> None:
        self.notificationSubscriptions = (self.notificationSubscriptions or {}) | {"marketing_email": subscribe}

    @property
    def is_authenticated(self) -> bool:  # required by flask-login
        return True

    @property
    def is_active(self) -> bool:  # required by flask-login
        return self.isActive

    @property
    def is_anonymous(self) -> bool:  # required by flask-login
        return False

    def get_id(self) -> str:  # required by flask-login
        return str(self.id)

    @property
    def clearTextPassword(self) -> str | None:
        return getattr(self, "_clearTextPassword", None)

    def setClearTextPassword(self, newpass: str) -> None:
        self._clearTextPassword = newpass

    def setPassword(self, newpass: str) -> None:
        self.setClearTextPassword(newpass)
        self.password = crypto.hash_password(newpass)

    @property
    def age(self) -> int | None:
        return users_utils.get_age_from_birth_date(self.birth_date, self.departementCode) if self.birth_date else None

    @hybrid_property
    def birth_date(self) -> date | None:
        """
        Returns the birth date validated by an Identity Provider if it exists,
        otherwise the birth date declared by the user at signup.
        """
        if self.validatedBirthDate:
            return self.validatedBirthDate
        if self.dateOfBirth:
            return self.dateOfBirth.date()
        return None

    @birth_date.expression  # type: ignore[no-redef]
    def birth_date(cls) -> date | None:
        return sa.case(
            (cls.validatedBirthDate.is_not(None), cls.validatedBirthDate),
            (cls.dateOfBirth.is_not(None), sa.cast(cls.dateOfBirth, sa.Date)),
            else_=None,
        )

    @property
    def deposit(self) -> "Deposit | None":
        if len(self.deposits) == 0:
            return None
        return sorted(self.deposits, key=attrgetter("expirationDate"), reverse=True)[0]

    @property
    def deposit_activation_date(self) -> datetime | None:
        return self.deposit.dateCreated if self.deposit else None

    @property
    def deposit_expiration_date(self) -> datetime | None:
        return self.deposit.expirationDate if self.deposit else None

    @property
    def deposit_type(self) -> "DepositType | None":
        return self.deposit.type if self.deposit else None

    @property
    def first_deposit_activation_date(self) -> datetime | None:
        return min((deposit.dateCreated for deposit in self.deposits), default=None)

    @property
    def received_pass_17_18(self) -> bool:
        return DepositType.GRANT_17_18 in [deposit.type for deposit in self.deposits]

    @property
    def received_pass_15_17(self) -> bool:
        return DepositType.GRANT_15_17 in [deposit.type for deposit in self.deposits]

    @property
    def received_pass_18(self) -> bool:
        return DepositType.GRANT_18 in [deposit.type for deposit in self.deposits]

    @property
    def received_pass_18_v3(self) -> bool:
        from pcapi.core.finance.models import RecreditType

        if not self.received_pass_17_18:
            return False

        return RecreditType.RECREDIT_18 in [r.recreditType for r in self.deposit.recredits] if self.deposit else False

    @property
    def deposit_version(self) -> int | None:
        return self.deposit.version if self.deposit else None

    @property
    def is_underage_eligible(self) -> bool:
        from pcapi.core.users import eligibility_api

        return eligibility_api.is_underage_eligibility(self.eligibility, self.age)

    @property
    def is_18_or_above_eligible(self) -> bool:
        from pcapi.core.users import eligibility_api

        return eligibility_api.is_18_or_above_eligibility(self.eligibility, self.age)

    @property
    def eligibility(self) -> EligibilityType | None:
        from pcapi.core.users import eligibility_api

        return eligibility_api.decide_eligibility(self, self.birth_date, datetime.utcnow())

    @hybrid_property
    def full_name(self) -> str:
        # full_name is used for display and should never be empty, which would be confused with no user.
        # We use the email as a fallback because it is the most human-readable way to identify a single user
        return (f"{self.firstName or ''} {self.lastName or ''}".strip()) or self.email

    @full_name.expression  # type: ignore[no-redef]
    def full_name(cls) -> str:
        return sa.func.coalesce(
            sa.func.nullif(
                sa.func.trim(
                    sa.func.concat(
                        sa.case((cls.firstName.is_not(None), cls.firstName), else_=""),
                        " ",
                        sa.case((cls.lastName.is_not(None), cls.lastName), else_=""),
                    )
                ),
                "",
            ),
            cls.email,
        )

    @property
    def has_active_deposit(self) -> bool:
        if not self.deposit:
            return False
        if not self.deposit.expirationDate:
            return True
        return self.deposit.expirationDate > datetime.utcnow()

    @property
    def is_eligible(self) -> bool:
        return self.eligibility is not None

    @property
    def latest_birthday(self) -> date | None:
        return _get_latest_birthday(self.birth_date)

    @property
    def wallet_balance(self) -> Decimal:
        balance = db.session.query(sa.func.get_wallet_balance(self.id, False)).scalar()
        return max(0, balance)

    @property
    # list[history_models.ActionHistory] -> None, untyped due to import loop
    def suspension_action_history(self) -> list:
        import pcapi.core.history.models as history_models

        return sorted(
            [
                action
                for action in self.action_history
                if action.actionType
                in (
                    history_models.ActionType.USER_SUSPENDED,
                    history_models.ActionType.USER_UNSUSPENDED,
                )
            ],
            key=lambda action: action.actionDate.isoformat() if action.actionDate else "",
        )

    @hybrid_property
    def suspension_reason(self) -> constants.SuspensionReason | None:
        """
        Reason for the active suspension.
        """
        import pcapi.core.history.models as history_models

        suspension_action_history = self.suspension_action_history
        if (
            not self.isActive
            and suspension_action_history
            and suspension_action_history[-1].actionType == history_models.ActionType.USER_SUSPENDED
        ):
            reason = suspension_action_history[-1].extraData.get("reason")
            if reason:
                return constants.SuspensionReason(reason)
        return None

    @suspension_reason.expression  # type: ignore[no-redef]
    def suspension_reason(cls) -> BinaryExpression:
        import pcapi.core.history.models as history_models

        return (
            sa.select(history_models.ActionHistory.extraData["reason"])
            .select_from(history_models.ActionHistory)
            .where(
                sa.and_(
                    history_models.ActionHistory.userId == User.id,
                    history_models.ActionHistory.actionType.in_(
                        [history_models.ActionType.USER_SUSPENDED, history_models.ActionType.USER_UNSUSPENDED]
                    ),
                )
            )
            .order_by(history_models.ActionHistory.actionDate.desc())
            .limit(1)
            .correlate(User)
            .scalar_subquery()
        )

    suspension_reason_expression: sa_orm.Mapped["str | None"] = sa_orm.query_expression()

    @hybrid_property
    def suspension_date(self) -> datetime | None:
        """
        Date and time when the inactive account was suspended for the last time.
        """
        import pcapi.core.history.models as history_models

        suspension_action_history = self.suspension_action_history
        if (
            not self.isActive
            and suspension_action_history
            and suspension_action_history[-1].actionType == history_models.ActionType.USER_SUSPENDED
        ):
            return suspension_action_history[-1].actionDate
        return None

    @suspension_date.expression  # type: ignore[no-redef]
    def suspension_date(cls) -> BinaryExpression:
        import pcapi.core.history.models as history_models

        return (
            sa.select(history_models.ActionHistory.actionDate)
            .select_from(history_models.ActionHistory)
            .where(
                sa.and_(
                    history_models.ActionHistory.userId == User.id,
                    history_models.ActionHistory.actionType.in_(
                        [history_models.ActionType.USER_SUSPENDED, history_models.ActionType.USER_UNSUSPENDED]
                    ),
                )
            )
            .order_by(history_models.ActionHistory.actionDate.desc())
            .limit(1)
            .correlate(User)
            .scalar_subquery()
        )

    suspension_date_expression: sa_orm.Mapped["datetime | None"] = sa_orm.query_expression()

    @property
    def account_state(self) -> AccountState:
        import pcapi.core.history.models as history_models

        if UserRole.ANONYMIZED in self.roles:
            return AccountState.ANONYMIZED

        if self.isActive:
            return AccountState.ACTIVE

        suspension_action_history = self.suspension_action_history
        if suspension_action_history:
            last_suspension_action = suspension_action_history[-1]

            if last_suspension_action.actionType == history_models.ActionType.USER_SUSPENDED:
                match self.suspension_reason:
                    case constants.SuspensionReason.DELETED:
                        return AccountState.DELETED
                    case constants.SuspensionReason.UPON_USER_REQUEST:
                        return AccountState.SUSPENDED_UPON_USER_REQUEST
                    case constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER:
                        return AccountState.SUSPICIOUS_LOGIN_REPORTED_BY_USER
                    case constants.SuspensionReason.WAITING_FOR_ANONYMIZATION:
                        return AccountState.WAITING_FOR_ANONYMIZATION

                return AccountState.SUSPENDED

        return AccountState.INACTIVE

    @property
    def is_account_suspended_upon_user_request(self) -> bool:
        return self.account_state == AccountState.SUSPENDED_UPON_USER_REQUEST

    @property
    def proValidationStatus(self) -> ValidationStatus | None:
        validation_statuses = [user_offerer.validationStatus for user_offerer in self.UserOfferers]
        for status in (ValidationStatus.VALIDATED, ValidationStatus.PENDING, ValidationStatus.NEW):  # by priority
            if status in validation_statuses:
                return status
        return None

    @hybrid_property
    def is_beneficiary(self) -> bool:
        return self.has_beneficiary_role or self.has_underage_beneficiary_role or self.has_free_beneficiary_role

    @is_beneficiary.expression  # type: ignore[no-redef]
    def is_beneficiary(cls) -> BooleanClauseList:
        return expression.or_(
            cls.roles.contains([UserRole.BENEFICIARY]),
            cls.roles.contains([UserRole.UNDERAGE_BENEFICIARY]),
            cls.roles.contains([UserRole.FREE_BENEFICIARY]),
        )

    @property
    def has_user_offerer(self) -> bool:
        return bool(len(self.UserOfferers) > 0)

    @hybrid_property
    def phoneNumber(self) -> str | None:
        return self._phoneNumber

    @phoneNumber.setter  # type: ignore[no-redef]
    def phoneNumber(self, value: str | None) -> None:
        if not value:
            self._phoneNumber = None
        else:
            self._phoneNumber = ParsedPhoneNumber(value).phone_number

    @phoneNumber.expression  # type: ignore[no-redef]
    def phoneNumber(cls) -> str | None:
        return cls._phoneNumber

    @hybrid_property
    def is_phone_validated(self) -> bool:
        return self.phoneValidationStatus == PhoneValidationStatusType.VALIDATED

    @is_phone_validated.expression  # type: ignore[no-redef]
    def is_phone_validated(cls) -> BinaryExpression:
        return cls.phoneValidationStatus == PhoneValidationStatusType.VALIDATED

    @hybrid_property
    def is_phone_validation_skipped(self) -> bool:
        return self.phoneValidationStatus == PhoneValidationStatusType.SKIPPED_BY_SUPPORT

    @is_phone_validation_skipped.expression  # type: ignore[no-redef]
    def is_phone_validation_skipped(cls) -> BinaryExpression:
        return cls.phoneValidationStatus == PhoneValidationStatusType.SKIPPED_BY_SUPPORT

    @hybrid_property
    def has_admin_role(self) -> bool:
        return UserRole.ADMIN in self.roles

    @has_admin_role.expression  # type: ignore[no-redef]
    def has_admin_role(cls) -> BinaryExpression:
        return cls.roles.contains([UserRole.ADMIN])

    @hybrid_property
    def has_pro_role(self) -> bool:
        return UserRole.PRO in self.roles

    @has_pro_role.expression  # type: ignore[no-redef]
    def has_pro_role(cls) -> BinaryExpression:
        return cls.roles.contains([UserRole.PRO])

    @hybrid_property
    def has_non_attached_pro_role(self) -> bool:
        return UserRole.NON_ATTACHED_PRO in self.roles

    @has_non_attached_pro_role.expression  # type: ignore[no-redef]
    def has_non_attached_pro_role(cls) -> BinaryExpression:
        return cls.roles.contains([UserRole.NON_ATTACHED_PRO])

    @hybrid_property
    def has_any_pro_role(self) -> bool:
        return self.has_pro_role or self.has_non_attached_pro_role

    @has_any_pro_role.expression  # type: ignore[no-redef]
    def has_any_pro_role(cls) -> BinaryExpression:
        return expression.or_(cls.roles.contains([UserRole.PRO]), cls.roles.contains([UserRole.NON_ATTACHED_PRO]))

    @hybrid_property
    def has_beneficiary_role(self) -> bool:
        return UserRole.BENEFICIARY in self.roles

    @has_beneficiary_role.expression  # type: ignore[no-redef]
    def has_beneficiary_role(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.roles.contains([UserRole.BENEFICIARY])

    @hybrid_property
    def has_underage_beneficiary_role(self) -> bool:
        return UserRole.UNDERAGE_BENEFICIARY in self.roles

    @has_underage_beneficiary_role.expression  # type: ignore[no-redef]
    def has_underage_beneficiary_role(cls) -> BinaryExpression:
        return cls.roles.contains([UserRole.UNDERAGE_BENEFICIARY])

    @hybrid_property
    def has_free_beneficiary_role(self) -> bool:
        return UserRole.FREE_BENEFICIARY in self.roles

    @has_free_beneficiary_role.expression  # type: ignore[no-redef]
    def has_free_beneficiary_role(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.roles.contains([UserRole.FREE_BENEFICIARY])

    @hybrid_property
    def has_test_role(self) -> bool:
        return UserRole.TEST in self.roles

    @has_test_role.expression  # type: ignore[no-redef]
    def has_test_role(cls) -> BinaryExpression:
        return cls.roles.contains([UserRole.TEST])

    @hybrid_property
    def has_anonymized_role(self) -> bool:
        return UserRole.ANONYMIZED in self.roles

    @has_anonymized_role.expression  # type: ignore[no-redef]
    def has_anonymized_role(cls) -> BinaryExpression:
        return cls.roles.contains([UserRole.ANONYMIZED])

    @property
    def impersonator(self) -> "User | None":
        return getattr(self, "_impersonator", None)

    @impersonator.setter
    def impersonator(self, impersonator: "User") -> None:
        self._impersonator = impersonator

    @property
    def real_user(self) -> "User":
        return self.impersonator or self

    @property
    def is_impersonated(self) -> bool:
        return bool(self.impersonator)

    @property
    def is_caledonian(self) -> bool:
        return self.postalCode.startswith(regions_utils.NEW_CALEDONIA_DEPARTMENT_CODE) if self.postalCode else False


class DiscordUser(PcObject, Base, Model):
    __tablename__ = "discord_user"

    userId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    user: sa_orm.Mapped["User"] = sa_orm.relationship("User", back_populates="discordUser")
    discordId = sa.Column(sa.Text, nullable=True, unique=True)
    hasAccess = sa.Column(sa.Boolean, nullable=False, server_default=expression.true())
    isBanned = sa.Column(sa.Boolean, nullable=False, server_default=expression.false(), default=False)
    lastUpdated = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())

    @hybrid_property
    def is_active(self) -> bool:
        return bool(self.discordId) and not self.isBanned

    @is_active.expression  # type: ignore[no-redef]
    def is_active(cls) -> BinaryExpression:
        return cls.discordId.is_not(None) and cls.isBanned.is_(False)


User.trig_ensure_password_or_sso_exists_ddl = sa.DDL(
    """
    CREATE OR REPLACE FUNCTION ensure_password_or_sso_exists()
    RETURNS TRIGGER AS $$
    BEGIN
        IF NEW.password IS NULL THEN
            IF NOT EXISTS (SELECT 1 FROM single_sign_on WHERE "userId" = NEW.id) THEN
                RAISE EXCEPTION 'missingLoginMethod' USING HINT = 'User must have either a password or a single sign-on';
            END IF;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS ensure_password_or_sso_exists ON "user";
    CREATE CONSTRAINT TRIGGER ensure_password_or_sso_exists
    AFTER INSERT OR UPDATE OF password ON "user"
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW EXECUTE PROCEDURE ensure_password_or_sso_exists();
    """
)


sa.event.listen(
    User.__table__,
    "after_create",
    User.trig_ensure_password_or_sso_exists_ddl,
)


class ExpenseDomain(enum.Enum):
    ALL = "all"
    DIGITAL = "digital"
    PHYSICAL = "physical"


@dataclass
class Credit:
    initial: Decimal
    remaining: Decimal


@dataclass
class DomainsCredit:
    all: Credit
    digital: Credit | None = None
    physical: Credit | None = None


class Favorite(PcObject, Base, Model):
    __tablename__ = "favorite"

    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)

    user: sa_orm.Mapped["User"] = sa_orm.relationship("User", foreign_keys=[userId], backref="favorites")

    offerId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id"), index=True, nullable=False)

    offer: sa_orm.Mapped["Offer"] = sa_orm.relationship("Offer", foreign_keys=[offerId], backref="favorites")

    dateCreated = sa.Column(sa.DateTime, nullable=True, default=datetime.utcnow)

    __table_args__ = (
        sa.UniqueConstraint(
            "userId",
            "offerId",
            name="unique_favorite",
        ),
    )


def split_email(email: str) -> tuple[str, str]:
    user_email, domain_email = email.split("@")
    return user_email, domain_email


class EmailHistoryEventTypeEnum(enum.Enum):
    UPDATE_REQUEST = "UPDATE_REQUEST"
    CONFIRMATION = "CONFIRMATION"
    CANCELLATION = "CANCELLATION"
    NEW_EMAIL_SELECTION = "NEW_EMAIL_SELECTION"
    VALIDATION = "VALIDATION"
    ADMIN_VALIDATION = "ADMIN_VALIDATION"
    ADMIN_UPDATE_REQUEST = "ADMIN_UPDATE_REQUEST"
    ADMIN_UPDATE = "ADMIN_UPDATE"


class UserEmailHistory(PcObject, Base, Model):
    __tablename__ = "user_email_history"

    userId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="SET NULL"), index=True, nullable=True)
    user: sa_orm.Mapped["User"] = sa_orm.relationship(
        "User", foreign_keys=[userId], backref=sa_orm.backref("email_history", passive_deletes=True)
    )

    oldUserEmail: str = sa.Column(sa.String(120), nullable=False, unique=False)
    oldDomainEmail: str = sa.Column(sa.String(120), nullable=False, unique=False)

    newUserEmail: str | None = sa.Column(sa.String(120), nullable=True, unique=False)
    newDomainEmail: str | None = sa.Column(sa.String(120), nullable=True, unique=False)

    creationDate: datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    eventType: EmailHistoryEventTypeEnum = sa.Column(sa.Enum(EmailHistoryEventTypeEnum), nullable=False)

    __table_args__ = (sa.Index("ix_user_email_history_oldEmail", oldUserEmail + "@" + oldDomainEmail),)

    @classmethod
    def _build(
        cls,
        user: User,
        new_email: str | None,
        event_type: EmailHistoryEventTypeEnum,
    ) -> "UserEmailHistory":
        old_user_email, old_domain_email = split_email(user.email)
        new_user_email, new_domain_email = split_email(new_email) if new_email else (None, None)
        return cls(
            user=user,
            oldUserEmail=old_user_email,
            oldDomainEmail=old_domain_email,
            newUserEmail=new_user_email,
            newDomainEmail=new_domain_email,
            eventType=event_type,
        )

    @classmethod
    def build_update_request(
        cls, user: User, new_email: str | None = None, by_admin: bool = False
    ) -> "UserEmailHistory":
        if by_admin:
            return cls._build(user, new_email, event_type=EmailHistoryEventTypeEnum.ADMIN_UPDATE_REQUEST)
        return cls._build(user, new_email, event_type=EmailHistoryEventTypeEnum.UPDATE_REQUEST)

    @classmethod
    def build_confirmation(cls, user: User, new_email: str | None = None) -> "UserEmailHistory":
        return cls._build(user, new_email, event_type=EmailHistoryEventTypeEnum.CONFIRMATION)

    @classmethod
    def build_cancellation(cls, user: User, new_email: str | None) -> "UserEmailHistory":
        return cls._build(user, new_email, event_type=EmailHistoryEventTypeEnum.CANCELLATION)

    @classmethod
    def build_new_email_selection(cls, user: User, new_email: str) -> "UserEmailHistory":
        return cls._build(user, new_email, event_type=EmailHistoryEventTypeEnum.NEW_EMAIL_SELECTION)

    @classmethod
    def build_validation(cls, user: User, new_email: str, by_admin: bool) -> "UserEmailHistory":
        if by_admin:
            return cls._build(user, new_email, event_type=EmailHistoryEventTypeEnum.ADMIN_VALIDATION)
        return cls._build(user, new_email, event_type=EmailHistoryEventTypeEnum.VALIDATION)

    @classmethod
    def build_admin_update(cls, user: User, new_email: str) -> "UserEmailHistory":
        return cls._build(user, new_email, event_type=EmailHistoryEventTypeEnum.ADMIN_UPDATE)

    @hybrid_property
    def oldEmail(self) -> str:
        return f"{self.oldUserEmail}@{self.oldDomainEmail}"

    @oldEmail.expression  # type: ignore[no-redef]
    def oldEmail(cls):
        return cls.oldUserEmail + "@" + cls.oldDomainEmail

    @hybrid_property
    def newEmail(self) -> str | None:
        if self.newUserEmail and self.newDomainEmail:
            return f"{self.newUserEmail}@{self.newDomainEmail}"
        return None

    @newEmail.expression  # type: ignore[no-redef]
    def newEmail(cls):
        return sa.case(
            (
                sa.and_(cls.newUserEmail.is_not(None), cls.newDomainEmail.is_not(None)),
                cls.newUserEmail + "@" + cls.newDomainEmail,
            ),
            else_=None,
        )


class UserAccountUpdateType(enum.Enum):
    EMAIL = "EMAIL"
    PHONE_NUMBER = "PHONE_NUMBER"
    FIRST_NAME = "FIRST_NAME"
    LAST_NAME = "LAST_NAME"
    ACCOUNT_HAS_SAME_INFO = "ACCOUNT_HAS_SAME_INFO"


class UserAccountUpdateFlag(enum.Enum):
    MISSING_VALUE = "MISSING_VALUE"
    INVALID_VALUE = "INVALID_VALUE"
    WAITING_FOR_CORRECTION = "WAITING_FOR_CORRECTION"
    CORRECTION_RESOLVED = "CORRECTION_RESOLVED"
    DUPLICATE_NEW_EMAIL = "DUPLICATE_NEW_EMAIL"


class UserAccountUpdateRequest(PcObject, Base, Model):
    __tablename__ = "user_account_update_request"
    dsApplicationId: int = sa.Column(sa.BigInteger, nullable=False, index=True, unique=True)
    dsTechnicalId: str = sa.Column(sa.Text, nullable=False)
    status: dms_models.GraphQLApplicationStates = sa.Column(
        MagicEnum(dms_models.GraphQLApplicationStates), nullable=False
    )
    dateCreated: datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.utcnow, server_default=sa.func.now()
    )
    dateLastStatusUpdate: datetime = sa.Column(
        sa.DateTime, nullable=True, default=datetime.utcnow, server_default=sa.func.now()
    )
    # Information about applicant, used to match with a single user
    firstName: str = sa.Column(sa.Text, nullable=True)
    lastName: str = sa.Column(sa.Text, nullable=True)
    email: str = sa.Column(sa.Text, nullable=False)
    birthDate = sa.Column(sa.Date, nullable=True)
    # User found from his/her email - may be null in case of wrong email
    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=True)
    user: sa_orm.Mapped[User] = sa_orm.relationship(User, foreign_keys=[userId], backref="accountUpdateRequests")
    # One or several changes may be requested
    updateTypes: sa_orm.Mapped[list[UserAccountUpdateType]] = sa.Column(
        postgresql.ARRAY(MagicEnum(UserAccountUpdateType)), nullable=False, server_default="{}"
    )
    oldEmail: str = sa.Column(sa.Text, nullable=True)
    newEmail: str = sa.Column(sa.Text, nullable=True)
    newPhoneNumber: str = sa.Column(sa.Text, nullable=True)
    newFirstName: str = sa.Column(sa.Text, nullable=True)
    newLastName: str = sa.Column(sa.Text, nullable=True)
    # Ensures that all checkboxes are checked (GCU, sworn statement)
    allConditionsChecked: bool = sa.Column(sa.Boolean, nullable=False, default=False)
    lastInstructorId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=True)
    lastInstructor: sa_orm.Mapped[User] = sa_orm.relationship(User, foreign_keys=[lastInstructorId])
    dateLastUserMessage: datetime = sa.Column(sa.DateTime, nullable=True)
    dateLastInstructorMessage: datetime = sa.Column(sa.DateTime, nullable=True)
    # Additional information to filter and/or show icons, badges...
    flags: sa_orm.Mapped[list[UserAccountUpdateFlag]] = sa.Column(
        postgresql.ARRAY(MagicEnum(UserAccountUpdateFlag)), nullable=False, server_default="{}"
    )

    @property
    def applicant_age(self) -> int | None:
        return users_utils.get_age_from_birth_date(self.birthDate) if self.birthDate else None

    @property
    def is_draft(self) -> bool:
        return self.status == dms_models.GraphQLApplicationStates.draft

    @property
    def is_accepted(self) -> bool:
        return self.status == dms_models.GraphQLApplicationStates.accepted

    @property
    def is_closed(self) -> bool:
        return self.status in (
            dms_models.GraphQLApplicationStates.accepted,
            dms_models.GraphQLApplicationStates.refused,
            dms_models.GraphQLApplicationStates.without_continuation,
        )

    @property
    def data_check_flags(self) -> list[UserAccountUpdateFlag]:
        return [
            flag
            for flag in self.flags
            if flag
            in (
                UserAccountUpdateFlag.MISSING_VALUE,
                UserAccountUpdateFlag.INVALID_VALUE,
                UserAccountUpdateFlag.DUPLICATE_NEW_EMAIL,
            )
        ]

    @property
    def correction_flags(self) -> list[UserAccountUpdateFlag]:
        if self.is_closed:
            return []
        return [
            flag
            for flag in self.flags
            if flag in (UserAccountUpdateFlag.WAITING_FOR_CORRECTION, UserAccountUpdateFlag.CORRECTION_RESOLVED)
        ]

    @property
    def has_email_update(self) -> bool:
        return UserAccountUpdateType.EMAIL in self.updateTypes

    @property
    def has_phone_number_update(self) -> bool:
        return UserAccountUpdateType.PHONE_NUMBER in self.updateTypes

    @property
    def has_first_name_update(self) -> bool:
        return UserAccountUpdateType.FIRST_NAME in self.updateTypes

    @property
    def has_last_name_update(self) -> bool:
        return UserAccountUpdateType.LAST_NAME in self.updateTypes

    @property
    def has_account_has_same_info_update(self) -> bool:
        return UserAccountUpdateType.ACCOUNT_HAS_SAME_INFO in self.updateTypes

    @property
    def can_be_accepted(self) -> bool:
        return bool(
            self.status in (dms_models.GraphQLApplicationStates.draft, dms_models.GraphQLApplicationStates.on_going)
            and self.userId is not None
            and self.updateTypes
            and not self.updateTypes == [UserAccountUpdateType.ACCOUNT_HAS_SAME_INFO]
            and not (
                set(self.flags)
                & {
                    UserAccountUpdateFlag.MISSING_VALUE,
                    UserAccountUpdateFlag.INVALID_VALUE,
                }
            )
        )

    @property
    def can_be_corrected(self) -> bool:
        return bool(
            self.status in (dms_models.GraphQLApplicationStates.draft, dms_models.GraphQLApplicationStates.on_going)
            and not (set(self.flags) & {UserAccountUpdateFlag.WAITING_FOR_CORRECTION})
        )

    @property
    def can_be_refused(self) -> bool:
        return bool(
            self.status in (dms_models.GraphQLApplicationStates.draft, dms_models.GraphQLApplicationStates.on_going)
        )


class UserSession(PcObject, Base, Model):
    __tablename__ = "user_session"
    userId: int = sa.Column(sa.BigInteger, nullable=False)
    uuid: UUID = sa.Column(postgresql.UUID(as_uuid=True), unique=True, nullable=False)


class TrustedDevice(PcObject, Base, Model):
    __tablename__ = "trusted_device"

    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    user: sa_orm.Mapped[User] = sa_orm.relationship(User, foreign_keys=[userId], back_populates="trusted_devices")

    deviceId: str = sa.Column(sa.Text, nullable=False, index=True)

    source = sa.Column(sa.Text, nullable=True)
    os = sa.Column(sa.Text, nullable=True)
    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)


class LoginDeviceHistory(PcObject, Base, Model):
    __tablename__ = "login_device_history"

    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    user: sa_orm.Mapped[User] = sa_orm.relationship(User, foreign_keys=[userId], back_populates="login_device_history")

    deviceId: str = sa.Column(sa.Text, nullable=False, index=True)

    source = sa.Column(sa.Text, nullable=True)
    os = sa.Column(sa.Text, nullable=True)
    location = sa.Column(sa.Text, nullable=True)
    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)


class SingleSignOn(PcObject, Base, Model):
    __tablename__ = "single_sign_on"

    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    user: sa_orm.Mapped[User] = sa_orm.relationship(User, foreign_keys=[userId], back_populates="single_sign_ons")

    ssoProvider: str = sa.Column(sa.Text, nullable=False)
    ssoUserId: str = sa.Column(sa.Text, nullable=False)

    __table_args__ = (
        sa.UniqueConstraint(
            "ssoProvider",
            "userId",
            name="unique_user_per_sso_provider",
        ),
        sa.UniqueConstraint(
            "ssoProvider",
            "ssoUserId",
            name="unique_sso_user_per_sso_provider",
        ),
    )


class GdprUserDataExtract(PcObject, Base, Model):
    __tablename__ = "gdpr_user_data_extract"

    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)

    dateProcessed: datetime = sa.Column(sa.DateTime, nullable=True)

    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=False)
    user: sa_orm.Mapped[User] = sa_orm.relationship(User, foreign_keys=[userId])

    authorUserId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=False)
    authorUser: sa_orm.Mapped[sa_orm.Mapped[User]] = sa_orm.relationship(User, foreign_keys=[authorUserId])

    @hybrid_property
    def expirationDate(self) -> datetime:
        return self.dateCreated + timedelta(days=7)

    @expirationDate.expression  # type: ignore [no-redef]
    def expirationDate(cls):
        return cls.dateCreated + timedelta(days=7)

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expirationDate


class GdprUserAnonymization(PcObject, Base, Model):
    __tablename__ = "gdpr_user_anonymization"

    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())
    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=False)
    user: sa_orm.Mapped[sa_orm.Mapped[User]] = sa_orm.relationship(User, foreign_keys=[userId])


class UserTagCategoryMapping(PcObject, Base, Model):
    __tablename__ = "user_tag_category_mapping"

    tagId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user_tag.id", ondelete="CASCADE"), index=True, nullable=False)
    categoryId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("user_tag_category.id", ondelete="CASCADE"), index=True, nullable=False
    )

    __table_args__ = (sa.UniqueConstraint("tagId", "categoryId", name="unique_user_tag_category"),)


class UserTag(PcObject, Base, Model):
    """
    Tags on users (accounts) are only used in backoffice, set to help for filtering and analytics in metabase.
    There is currently no display or impact in mobile and web apps.
    """

    __tablename__ = "user_tag"

    name: str = sa.Column(sa.Text, nullable=False, unique=True)
    label: str = sa.Column(sa.Text)
    description: str = sa.Column(sa.Text)

    categories: sa_orm.Mapped[list["UserTagCategory"]] = sa_orm.relationship(
        "UserTagCategory", secondary=UserTagCategoryMapping.__table__
    )

    def __str__(self) -> str:
        return self.label or self.name


class UserTagCategory(PcObject, Base, Model):
    """
    Tag categories can be considered as "tags on tags", which aims at filtering tags depending on the project:
    The same UserTag can be used in one or several project.
    """

    __tablename__ = "user_tag_category"

    name: str = sa.Column(sa.Text, nullable=False, unique=True)
    label: str = sa.Column(sa.Text)

    def __str__(self) -> str:
        return self.label or self.name
