from __future__ import annotations  # to type models before their declaration

from dataclasses import asdict
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from decimal import Decimal
import enum
from operator import attrgetter
import typing
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.sql import expression
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.elements import BooleanClauseList
from sqlalchemy.sql.functions import func

from pcapi import settings
from pcapi.core.finance.enum import DepositType
from pcapi.core.geography.models import IrisFrance
from pcapi.core.users import constants
from pcapi.core.users import utils as users_utils
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.needs_validation_mixin import NeedsValidationMixin
from pcapi.models.pc_object import PcObject
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.utils import crypto
from pcapi.utils.phone_number import ParsedPhoneNumber


if typing.TYPE_CHECKING:
    from pcapi.core.finance.models import Deposit
    from pcapi.core.offerers.models import UserOfferer
    from pcapi.core.offers.models import Mediation
    from pcapi.core.offers.models import Offer
    from pcapi.core.permissions.models import BackOfficeUserProfile


VOID_FIRST_NAME = ""


class TokenType(enum.Enum):
    RESET_PASSWORD = "reset-password"


class PhoneValidationStatusType(enum.Enum):
    SKIPPED_BY_SUPPORT = "skipped-by-support"
    UNVALIDATED = "unvalidated"
    VALIDATED = "validated"


@dataclass
class TokenExtraData:
    phone_number: str | None


class Token(PcObject, Base, Model):
    __tablename__ = "token"

    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)

    user: orm.Mapped["User"] = orm.relationship(
        "User", foreign_keys=[userId], backref=orm.backref("tokens", passive_deletes=True)
    )

    value: str = sa.Column(sa.String, index=True, unique=True, nullable=False)

    type: TokenType = sa.Column(sa.Enum(TokenType, create_constraint=False), nullable=False)

    creationDate: datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    expirationDate = sa.Column(sa.DateTime, nullable=True)

    isUsed: bool = sa.Column(sa.Boolean, nullable=False, server_default=expression.false(), default=False)

    extraData: dict = sa.Column(MutableDict.as_mutable(postgresql.JSONB), nullable=True)

    def get_extra_data(self) -> TokenExtraData | None:
        return TokenExtraData(**self.extraData) if self.extraData else None


class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    ANONYMIZED = "ANONYMIZED"
    BENEFICIARY = "BENEFICIARY"
    PRO = "PRO"
    NON_ATTACHED_PRO = "NON_ATTACHED_PRO"
    UNDERAGE_BENEFICIARY = "UNDERAGE_BENEFICIARY"
    TEST = "TEST"  # used to mark imported test users on staging


class EligibilityType(enum.Enum):
    UNDERAGE = "underage"
    AGE18 = "age-18"


@dataclass
class NotificationSubscriptions:
    marketing_push: bool = True
    marketing_email: bool = True


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
    M: str = "M."
    F: str = "Mme"


class AccountState(enum.Enum):
    ACTIVE = "ACTIVE"
    ANONYMIZED = "ANONYMIZED"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    SUSPENDED_UPON_USER_REQUEST = "SUSPENDED_UPON_USER_REQUEST"
    SUSPICIOUS_LOGIN_REPORTED_BY_USER = "SUSPICIOUS_LOGIN_REPORTED_BY_USER"
    DELETED = "DELETED"

    @property
    def is_deleted(self) -> bool:
        return self == AccountState.DELETED


class User(PcObject, Base, Model, NeedsValidationMixin, DeactivableMixin):
    __tablename__ = "user"

    activity = sa.Column(sa.String(128), nullable=True)
    address = sa.Column(sa.Text, nullable=True)
    city = sa.Column(sa.String(100), nullable=True)
    civility = sa.Column(sa.Text, nullable=True)
    clearTextPassword = None
    comment = sa.Column(sa.Text(), nullable=True)
    culturalSurveyFilledDate = sa.Column(sa.DateTime, nullable=True)
    # culturalSurveyId is obsolete. the column is kept for backward compatibility with the existing data
    culturalSurveyId = sa.Column(postgresql.UUID(as_uuid=True), nullable=True)
    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)
    dateOfBirth = sa.Column(sa.DateTime, nullable=True)  # declared at signup
    departementCode = sa.Column(sa.String(3), nullable=True)
    email: str = sa.Column(sa.String(120), nullable=False, unique=True)
    externalIds = sa.Column(postgresql.json.JSONB, nullable=True, default={}, server_default="{}")
    extraData: dict = sa.Column(
        MutableDict.as_mutable(postgresql.json.JSONB), nullable=True, default={}, server_default="{}"
    )
    firstName = sa.Column(sa.String(128), nullable=True)
    hasSeenProTutorials: bool = sa.Column(sa.Boolean, nullable=False, server_default=expression.false())
    hasSeenProRgs: bool = sa.Column(sa.Boolean, nullable=False, server_default=expression.false())
    idPieceNumber = sa.Column(sa.String, nullable=True, unique=True)
    ineHash = sa.Column(sa.String, nullable=True, unique=True)
    irisFranceId = sa.Column(sa.BigInteger, sa.ForeignKey("iris_france.id"), index=True, nullable=True)
    irisFrance: sa.orm.Mapped[IrisFrance] = orm.relationship(IrisFrance, foreign_keys=[irisFranceId])
    isEmailValidated = sa.Column(sa.Boolean, nullable=True, server_default=expression.false())
    lastConnectionDate = sa.Column(sa.DateTime, nullable=True)
    lastName = sa.Column(sa.String(128), nullable=True)
    married_name = sa.Column(sa.String(128), nullable=True)
    needsToFillCulturalSurvey = sa.Column(sa.Boolean, server_default=expression.true(), default=True)
    notificationSubscriptions: dict = sa.Column(
        MutableDict.as_mutable(postgresql.json.JSONB),
        nullable=True,
        default=asdict(NotificationSubscriptions()),
        server_default="""{"marketing_push": true, "marketing_email": true}""",
    )
    password: bytes = sa.Column(sa.LargeBinary(60), nullable=True)
    _phoneNumber = sa.Column(sa.String(20), nullable=True, index=True, name="phoneNumber")
    phoneValidationStatus = sa.Column(sa.Enum(PhoneValidationStatusType, create_constraint=False), nullable=True)
    postalCode = sa.Column(sa.String(5), nullable=True)
    recreditAmountToShow = sa.Column(sa.Numeric(10, 2), nullable=True)
    UserOfferers: list["UserOfferer"] = orm.relationship("UserOfferer", back_populates="user")
    roles: list[UserRole] = sa.Column(
        MutableList.as_mutable(postgresql.ARRAY(sa.Enum(UserRole, native_enum=False, create_constraint=False))),
        nullable=False,
        server_default="{}",
    )
    schoolType = sa.Column(sa.Enum(SchoolTypeEnum, create_constraint=False), nullable=True)
    trusted_devices: list["TrustedDevice"] = orm.relationship("TrustedDevice", back_populates="user")
    login_device_history: list["LoginDeviceHistory"] = orm.relationship("LoginDeviceHistory", back_populates="user")
    single_sign_ons: list["SingleSignOn"] = orm.relationship("SingleSignOn", back_populates="user")
    validatedBirthDate = sa.Column(sa.Date, nullable=True)  # validated by an Identity Provider
    backoffice_profile: orm.Mapped["BackOfficeUserProfile"] = orm.relationship(
        "BackOfficeUserProfile", uselist=False, back_populates="user"
    )
    sa.Index("ix_user_validatedBirthDate", validatedBirthDate)
    pro_flags: UserProFlags = orm.relationship("UserProFlags", back_populates="user", uselist=False)

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
            msg = "User can't have roles " + " and ".join(r.value for r in updated_roles)
            raise InvalidUserRoleException(msg)

        self.roles = updated_roles

    def add_admin_role(self) -> None:
        self._add_role(UserRole.ADMIN)

    def add_beneficiary_role(self) -> None:
        self.remove_underage_beneficiary_role()
        self._add_role(UserRole.BENEFICIARY)

    def add_pro_role(self) -> None:
        self.remove_non_attached_pro_role()
        self._add_role(UserRole.PRO)

    def add_non_attached_pro_role(self) -> None:
        self.remove_pro_role()
        self._add_role(UserRole.NON_ATTACHED_PRO)

    def add_underage_beneficiary_role(self) -> None:
        from pcapi.core.users.exceptions import InvalidUserRoleException

        if self.has_admin_role:
            raise InvalidUserRoleException("User can't have both ADMIN and BENEFICIARY role")
        self._add_role(UserRole.UNDERAGE_BENEFICIARY)

    def add_test_role(self) -> None:
        self._add_role(UserRole.TEST)

    def replace_roles_by_anonymized_role(self) -> None:
        self.roles = [UserRole.ANONYMIZED]

    def checkPassword(self, passwordToCheck: str) -> bool:
        return crypto.check_password(passwordToCheck, self.password)

    def get_notification_subscriptions(self) -> NotificationSubscriptions:
        return NotificationSubscriptions(**self.notificationSubscriptions or {})

    def has_access(self, offerer_id: int) -> bool:
        # FIXME (dbaty, 2021-11-26): consider moving to a function in `core.users.api`?
        from pcapi.core.offerers.models import UserOfferer

        if self.has_admin_role:
            return True
        return db.session.query(
            UserOfferer.query.filter(
                UserOfferer.offererId == offerer_id,
                UserOfferer.userId == self.id,
                UserOfferer.isValidated,
            ).exists()
        ).scalar()

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

    def is_super_admin(self) -> bool:
        if settings.IS_PROD:
            return self.email in settings.SUPER_ADMIN_EMAIL_ADDRESSES
        return self.has_admin_role

    def populate_from_dict(self, data: dict, skipped_keys: typing.Iterable[str] = ()) -> None:
        super().populate_from_dict(data, skipped_keys=skipped_keys)
        if data.get("password"):
            self.setPassword(data["password"])

    def remove_admin_role(self) -> None:
        if self.has_admin_role:
            self.roles.remove(UserRole.ADMIN)

    def remove_underage_beneficiary_role(self) -> None:
        if self.has_underage_beneficiary_role:
            self.roles.remove(UserRole.UNDERAGE_BENEFICIARY)

    def remove_beneficiary_role(self) -> None:
        if self.has_beneficiary_role:
            self.roles.remove(UserRole.BENEFICIARY)

    def remove_pro_role(self) -> None:
        if self.has_pro_role:
            self.roles.remove(UserRole.PRO)

    def remove_non_attached_pro_role(self) -> None:
        if self.has_non_attached_pro_role:
            self.roles.remove(UserRole.NON_ATTACHED_PRO)

    def setPassword(self, newpass: str) -> None:
        self.clearTextPassword = newpass
        self.password = crypto.hash_password(newpass)

    @property
    def age(self) -> int | None:
        return users_utils.get_age_from_birth_date(self.birth_date) if self.birth_date else None

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

    @birth_date.expression  # type: ignore [no-redef]
    def birth_date(cls) -> date | None:  # pylint: disable=no-self-argument
        return sa.case(
            [
                (cls.validatedBirthDate.is_not(None), cls.validatedBirthDate),
                (cls.dateOfBirth.is_not(None), sa.cast(cls.dateOfBirth, sa.Date)),
            ],
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
    def received_pass_15_17(self) -> bool:
        return DepositType.GRANT_15_17 in [deposit.type for deposit in self.deposits]

    @property
    def received_pass_18(self) -> bool:
        return DepositType.GRANT_18 in [deposit.type for deposit in self.deposits]

    @property
    def deposit_version(self) -> int | None:
        return self.deposit.version if self.deposit else None

    @property
    def eligibility(self) -> EligibilityType | None:
        from pcapi.core.fraud import api as fraud_api

        return fraud_api.decide_eligibility(self, self.birth_date, datetime.utcnow())

    @hybrid_property
    def full_name(self) -> str:
        # full_name is used for display and should never be empty, which would be confused with no user.
        # We use the email as a fallback because it is the most human-readable way to identify a single user
        return (f"{self.firstName or ''} {self.lastName or ''}".strip()) or self.email

    @full_name.expression  # type: ignore [no-redef]
    def full_name(cls) -> str:  # pylint: disable=no-self-argument
        return sa.func.coalesce(
            sa.func.nullif(
                sa.func.trim(
                    sa.func.concat(
                        sa.case([(cls.firstName.is_not(None), cls.firstName)], else_=""),
                        " ",
                        sa.case([(cls.lastName.is_not(None), cls.lastName)], else_=""),
                    )
                ),
                "",
            ),
            cls.email,
        )

    @property
    def has_active_deposit(self) -> bool:
        return self.deposit.expirationDate > datetime.utcnow() if self.deposit else False  # type: ignore [operator]

    @property
    def hasPhysicalVenues(self) -> bool:
        for user_offerer in self.UserOfferers:
            if any(not venue.isVirtual for venue in user_offerer.offerer.managedVenues):
                return True

        return False

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

    @property
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

    @property
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
                if self.suspension_reason == constants.SuspensionReason.DELETED:
                    return AccountState.DELETED
                if self.suspension_reason == constants.SuspensionReason.UPON_USER_REQUEST:
                    return AccountState.SUSPENDED_UPON_USER_REQUEST
                if self.suspension_reason == constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER:
                    return AccountState.SUSPICIOUS_LOGIN_REPORTED_BY_USER

                return AccountState.SUSPENDED

        return AccountState.INACTIVE

    @property
    def is_account_deleted(self) -> bool:
        return self.account_state == AccountState.DELETED

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
        return self.has_beneficiary_role or self.has_underage_beneficiary_role

    @is_beneficiary.expression  # type: ignore [no-redef]
    def is_beneficiary(cls) -> BooleanClauseList:  # pylint: disable=no-self-argument
        return expression.or_(
            cls.roles.contains([UserRole.BENEFICIARY]), cls.roles.contains([UserRole.UNDERAGE_BENEFICIARY])
        )

    @property
    def has_remaining_credit(self) -> bool:
        today = datetime.combine(date.today(), datetime.min.time())
        return (
            self.deposit is not None
            and (self.deposit.expirationDate is None or self.deposit.expirationDate > today)
            and self.wallet_balance > 0
        )

    @hybrid_property
    def phoneNumber(self) -> str | None:
        return self._phoneNumber

    @phoneNumber.setter  # type: ignore [no-redef]
    def phoneNumber(self, value: str | None) -> None:
        if not value:
            self._phoneNumber = None
        else:
            self._phoneNumber = ParsedPhoneNumber(value).phone_number

    @phoneNumber.expression  # type: ignore [no-redef]
    def phoneNumber(cls) -> str | None:  # pylint: disable=no-self-argument
        return cls._phoneNumber

    @hybrid_property
    def is_phone_validated(self) -> bool:
        return self.phoneValidationStatus == PhoneValidationStatusType.VALIDATED

    @is_phone_validated.expression  # type: ignore [no-redef]
    def is_phone_validated(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.phoneValidationStatus == PhoneValidationStatusType.VALIDATED

    @hybrid_property
    def is_phone_validation_skipped(self) -> bool:
        return self.phoneValidationStatus == PhoneValidationStatusType.SKIPPED_BY_SUPPORT

    @is_phone_validation_skipped.expression  # type: ignore [no-redef]
    def is_phone_validation_skipped(cls):  # pylint: disable=no-self-argument
        return cls.phoneValidationStatus == PhoneValidationStatusType.SKIPPED_BY_SUPPORT

    @hybrid_property
    def has_admin_role(self) -> bool:
        return UserRole.ADMIN in self.roles

    @has_admin_role.expression  # type: ignore [no-redef]
    def has_admin_role(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.roles.contains([UserRole.ADMIN])

    @hybrid_property
    def has_beneficiary_role(self) -> bool:
        return UserRole.BENEFICIARY in self.roles

    @has_beneficiary_role.expression  # type: ignore [no-redef]
    def has_beneficiary_role(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.roles.contains([UserRole.BENEFICIARY])

    @hybrid_property
    def has_pro_role(self) -> bool:
        return UserRole.PRO in self.roles

    @has_pro_role.expression  # type: ignore [no-redef]
    def has_pro_role(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.roles.contains([UserRole.PRO])

    @hybrid_property
    def has_non_attached_pro_role(self) -> bool:
        return UserRole.NON_ATTACHED_PRO in self.roles

    @has_non_attached_pro_role.expression  # type: ignore [no-redef]
    def has_non_attached_pro_role(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.roles.contains([UserRole.NON_ATTACHED_PRO])

    @hybrid_property
    def has_underage_beneficiary_role(self) -> bool:
        return UserRole.UNDERAGE_BENEFICIARY in self.roles

    @has_underage_beneficiary_role.expression  # type: ignore [no-redef]
    def has_underage_beneficiary_role(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.roles.contains([UserRole.UNDERAGE_BENEFICIARY])

    @hybrid_property
    def has_test_role(self) -> bool:
        return UserRole.TEST in self.roles

    @has_test_role.expression  # type: ignore [no-redef]
    def has_test_role(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.roles.contains([UserRole.TEST])


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

    user: orm.Mapped["User"] = orm.relationship("User", foreign_keys=[userId], backref="favorites")

    offerId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id"), index=True, nullable=False)

    offer: orm.Mapped["Offer"] = orm.relationship("Offer", foreign_keys=[offerId], backref="favorites")

    mediationId = sa.Column(sa.BigInteger, sa.ForeignKey("mediation.id"), index=True, nullable=True)

    mediation: orm.Mapped["Mediation"] = orm.relationship("Mediation", foreign_keys=[mediationId], backref="favorites")

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
    VALIDATION = "VALIDATION"
    ADMIN_VALIDATION = "ADMIN_VALIDATION"
    ADMIN_UPDATE_REQUEST = "ADMIN_UPDATE_REQUEST"
    ADMIN_UPDATE = "ADMIN_UPDATE"


class UserEmailHistory(PcObject, Base, Model):
    __tablename__ = "user_email_history"

    userId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="SET NULL"), index=True, nullable=True)
    user: sa.orm.Mapped["User"] = orm.relationship(
        "User", foreign_keys=[userId], backref=orm.backref("email_history", passive_deletes=True)
    )

    oldUserEmail: str = sa.Column(sa.String(120), nullable=False, unique=False, index=True)
    oldDomainEmail: str = sa.Column(sa.String(120), nullable=False, unique=False, index=True)

    newUserEmail: str = sa.Column(sa.String(120), nullable=False, unique=False, index=True)
    newDomainEmail: str = sa.Column(sa.String(120), nullable=False, unique=False, index=True)

    creationDate: datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    eventType: EmailHistoryEventTypeEnum = sa.Column(sa.Enum(EmailHistoryEventTypeEnum), nullable=False)

    @classmethod
    def _build(
        cls,
        user: User,
        new_email: str,
        event_type: EmailHistoryEventTypeEnum,
    ) -> "UserEmailHistory":
        old_user_email, old_domain_email = split_email(user.email)
        new_user_email, new_domain_email = split_email(new_email)
        return cls(
            user=user,
            oldUserEmail=old_user_email,
            oldDomainEmail=old_domain_email,
            newUserEmail=new_user_email,
            newDomainEmail=new_domain_email,
            eventType=event_type,
        )

    @classmethod
    def build_update_request(cls, user: User, new_email: str, by_admin: bool = False) -> "UserEmailHistory":
        if by_admin:
            return cls._build(user, new_email, event_type=EmailHistoryEventTypeEnum.ADMIN_UPDATE_REQUEST)
        return cls._build(user, new_email, event_type=EmailHistoryEventTypeEnum.UPDATE_REQUEST)

    @classmethod
    def build_confirmation(cls, user: User, new_email: str) -> "UserEmailHistory":
        return cls._build(user, new_email, event_type=EmailHistoryEventTypeEnum.CONFIRMATION)

    @classmethod
    def build_cancellation(cls, user: User, new_email: str) -> "UserEmailHistory":
        return cls._build(user, new_email, event_type=EmailHistoryEventTypeEnum.CANCELLATION)

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

    @oldEmail.expression  # type: ignore [no-redef]
    def oldEmail(cls):  # pylint: disable=no-self-argument
        return func.concat(cls.oldUserEmail, "@", cls.oldDomainEmail)

    @hybrid_property
    def newEmail(self) -> str:
        return f"{self.newUserEmail}@{self.newDomainEmail}"

    @newEmail.expression  # type: ignore [no-redef]
    def newEmail(cls):  # pylint: disable=no-self-argument
        return func.concat(cls.newUserEmail, "@", cls.newDomainEmail)


class UserSession(PcObject, Base, Model):
    userId: int = sa.Column(sa.BigInteger, nullable=False)
    uuid: UUID = sa.Column(postgresql.UUID(as_uuid=True), unique=True, nullable=False)


class UserProFlags(PcObject, Base, Model):
    __tablename__ = "user_pro_flags"

    firebase: dict = sa.Column(
        MutableDict.as_mutable(postgresql.json.JSONB), nullable=True, default={}, server_default="{}"
    )
    userId: int = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    user: User = orm.relationship(User, foreign_keys=[userId], back_populates="pro_flags", uselist=False)


class TrustedDevice(PcObject, Base, Model):
    __tablename__ = "trusted_device"

    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    user: User = orm.relationship(User, foreign_keys=[userId], back_populates="trusted_devices")

    deviceId: str = sa.Column(sa.Text, nullable=False, index=True)

    source = sa.Column(sa.Text, nullable=True)
    os = sa.Column(sa.Text, nullable=True)
    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)


class LoginDeviceHistory(PcObject, Base, Model):
    __tablename__ = "login_device_history"

    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    user: User = orm.relationship(User, foreign_keys=[userId], back_populates="login_device_history")

    deviceId: str = sa.Column(sa.Text, nullable=False, index=True)

    source = sa.Column(sa.Text, nullable=True)
    os = sa.Column(sa.Text, nullable=True)
    location = sa.Column(sa.Text, nullable=True)
    dateCreated: datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)


class SingleSignOn(PcObject, Base, Model):
    __tablename__ = "single_sign_on"

    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    user: User = orm.relationship(User, foreign_keys=[userId], back_populates="single_sign_ons")

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
