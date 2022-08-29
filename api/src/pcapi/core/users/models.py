import copy
from dataclasses import asdict
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from decimal import Decimal
import enum
from operator import attrgetter
import typing

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.sql import expression
from sqlalchemy.sql.functions import func

from pcapi import settings
from pcapi.core.users import utils as users_utils
from pcapi.core.users.constants import SuspensionEventType
from pcapi.core.users.constants import SuspensionReason
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.needs_validation_mixin import NeedsValidationMixin
from pcapi.models.pc_object import PcObject
from pcapi.utils import crypto
from pcapi.utils.phone_number import ParsedPhoneNumber


if typing.TYPE_CHECKING:
    from pcapi.core.offerers.models import UserOfferer
    from pcapi.core.payments.models import Deposit
    from pcapi.core.payments.models import DepositType


VOID_FIRST_NAME = ""
VOID_PUBLIC_NAME = "   "


class TokenType(enum.Enum):
    RESET_PASSWORD = "reset-password"
    EMAIL_VALIDATION = "email-validation"
    PHONE_VALIDATION = "phone-validation"


class PhoneValidationStatusType(enum.Enum):
    SKIPPED_BY_SUPPORT = "skipped-by-support"
    UNVALIDATED = "unvalidated"
    VALIDATED = "validated"


@dataclass
class TokenExtraData:
    phone_number: str | None


class Token(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    __tablename__ = "token"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    userId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)

    user = orm.relationship("User", foreign_keys=[userId], backref=orm.backref("tokens", passive_deletes=True))  # type: ignore [misc]

    value = sa.Column(sa.String, index=True, unique=True, nullable=False)

    type = sa.Column(sa.Enum(TokenType, create_constraint=False), nullable=False)

    creationDate = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    expirationDate = sa.Column(sa.DateTime, nullable=True)

    isUsed = sa.Column(sa.Boolean, nullable=False, server_default=expression.false(), default=False)

    extraData = sa.Column(MutableDict.as_mutable(postgresql.JSONB), nullable=True)  # type: ignore [misc]

    def get_extra_data(self) -> TokenExtraData | None:
        return TokenExtraData(**self.extraData) if self.extraData else None


class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    BENEFICIARY = "BENEFICIARY"
    PRO = "PRO"
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
def _get_latest_birthday(birth_date: date) -> date:
    """
    Calculates the latest birthday of a given person.
    :param birth_date: The person's birthday.
    :return: The latest birthday's date.
    """

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
    UNEMPLOYED = "Chômeur"


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
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    SUSPENDED_UPON_USER_REQUEST = "SUSPENDED_UPON_USER_REQUEST"
    DELETED = "DELETED"

    @property
    def is_deleted(self) -> bool:
        return self == AccountState.DELETED


class User(PcObject, Base, Model, NeedsValidationMixin, DeactivableMixin):  # type: ignore [valid-type, misc]
    __tablename__ = "user"

    activity = sa.Column(sa.String(128), nullable=True)
    address = sa.Column(sa.Text, nullable=True)
    city = sa.Column(sa.String(100), nullable=True)
    civility = sa.Column(sa.Text, nullable=True)
    clearTextPassword = None
    comment = sa.Column(sa.Text(), nullable=True)
    culturalSurveyFilledDate = sa.Column(sa.DateTime, nullable=True)
    culturalSurveyId = sa.Column(postgresql.UUID(as_uuid=True), nullable=True)  # type: ignore [misc]
    dateCreated = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)
    dateOfBirth = sa.Column(sa.DateTime, nullable=True)
    departementCode = sa.Column(sa.String(3), nullable=True)
    email: str = sa.Column(sa.String(120), nullable=False, unique=True)
    externalIds = sa.Column(postgresql.json.JSONB, nullable=True, default={}, server_default="{}")
    extraData = sa.Column(MutableDict.as_mutable(postgresql.json.JSONB), nullable=True, default={}, server_default="{}")  # type: ignore [misc]
    firstName = sa.Column(sa.String(128), nullable=True)
    sa.Index("idx_user_trgm_first_name", firstName, postgresql_using="gin")
    hasSeenProTutorials = sa.Column(sa.Boolean, nullable=False, server_default=expression.false())
    hasSeenProRgs = sa.Column(sa.Boolean, nullable=False, server_default=expression.false())
    idPieceNumber = sa.Column(sa.String, nullable=True, unique=True)
    ineHash = sa.Column(sa.Text, nullable=True, unique=True)
    isEmailValidated = sa.Column(sa.Boolean, nullable=True, server_default=expression.false())
    lastConnectionDate = sa.Column(sa.DateTime, nullable=True)
    lastName = sa.Column(sa.String(128), nullable=True)
    sa.Index("idx_user_trgm_last_name", lastName, postgresql_using="gin")
    married_name = sa.Column(sa.String(128), nullable=True)
    needsToFillCulturalSurvey = sa.Column(sa.Boolean, server_default=expression.true(), default=True)
    notificationSubscriptions = sa.Column(  # type: ignore [misc]
        MutableDict.as_mutable(postgresql.json.JSONB),
        nullable=True,
        default=asdict(NotificationSubscriptions()),
        server_default="""{"marketing_push": true, "marketing_email": true}""",
    )
    password = sa.Column(sa.LargeBinary(60), nullable=False)
    _phoneNumber = sa.Column(sa.String(20), nullable=True, index=True, name="phoneNumber")
    phoneValidationStatus = sa.Column(sa.Enum(PhoneValidationStatusType, create_constraint=False), nullable=True)
    postalCode = sa.Column(sa.String(5), nullable=True)
    publicName: str = sa.Column(sa.String(255), nullable=False)
    recreditAmountToShow = sa.Column(sa.Numeric(10, 2), nullable=True)
    UserOfferers: list["UserOfferer"] = orm.relationship("UserOfferer", back_populates="user")
    roles = sa.Column(  # type: ignore [misc]
        MutableList.as_mutable(postgresql.ARRAY(sa.Enum(UserRole, native_enum=False, create_constraint=False))),
        nullable=False,
        server_default="{}",
    )
    schoolType = sa.Column(sa.Enum(SchoolTypeEnum, create_constraint=False), nullable=True)

    def _add_role(self, role: UserRole) -> None:
        from pcapi.core.users.exceptions import InvalidUserRoleException

        if self.roles is None:
            self.roles = []
        if self.roles and role in self.roles:
            return

        current_roles = copy.deepcopy(self.roles) if self.roles else []
        updated_roles = current_roles + [role]  # type: ignore [operator]

        if UserRole.BENEFICIARY in updated_roles and UserRole.ADMIN in updated_roles:
            raise InvalidUserRoleException("User can't have both ADMIN and BENEFICIARY role")

        self.roles = updated_roles

    def add_admin_role(self) -> None:
        from pcapi.core.users.exceptions import InvalidUserRoleException

        if self.is_beneficiary:
            raise InvalidUserRoleException("User can't have both ADMIN and BENEFICIARY role")

        self._add_role(UserRole.ADMIN)

    def add_beneficiary_role(self) -> None:
        from pcapi.core.users.exceptions import InvalidUserRoleException

        if self.has_admin_role:
            raise InvalidUserRoleException("User can't have both ADMIN and BENEFICIARY role")
        self._add_role(UserRole.BENEFICIARY)

    def add_pro_role(self) -> None:
        self._add_role(UserRole.PRO)

    def add_underage_beneficiary_role(self) -> None:
        from pcapi.core.users.exceptions import InvalidUserRoleException

        if self.has_admin_role:
            raise InvalidUserRoleException("User can't have both ADMIN and BENEFICIARY role")
        self._add_role(UserRole.UNDERAGE_BENEFICIARY)

    def add_test_role(self) -> None:
        self._add_role(UserRole.TEST)

    def checkPassword(self, passwordToCheck):  # type: ignore [no-untyped-def]
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

    def has_enabled_push_notifications(self) -> bool:
        subscriptions = self.get_notification_subscriptions()
        return subscriptions.marketing_push

    @property
    def is_authenticated(self) -> bool:  # required by flask-login
        return True

    @property
    def is_active(self) -> bool:  # required by flask-login
        return self.isActive  # type: ignore [return-value]

    @property
    def is_anonymous(self) -> bool:  # required by flask-login
        return False

    def get_id(self):  # type: ignore [no-untyped-def] # required by flask-login
        return str(self.id)

    def is_super_admin(self) -> bool:
        if settings.IS_PROD:
            return self.email in settings.SUPER_ADMIN_EMAIL_ADDRESSES
        return self.has_admin_role  # type: ignore [return-value]

    def populate_from_dict(self, data):  # type: ignore [no-untyped-def]
        super().populate_from_dict(data)
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

    def setPassword(self, newpass):  # type: ignore [no-untyped-def]
        self.clearTextPassword = newpass
        self.password = crypto.hash_password(newpass)

    @property
    def age(self) -> int | None:
        return users_utils.get_age_from_birth_date(self.dateOfBirth.date()) if self.dateOfBirth is not None else None

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
    def deposit_version(self) -> int | None:
        return self.deposit.version if self.deposit else None

    @property
    def eligibility(self) -> EligibilityType | None:
        from pcapi.core.fraud import api as fraud_api

        return fraud_api.decide_eligibility(self, self.dateOfBirth, datetime.utcnow())

    @property
    def has_active_deposit(self):  # type: ignore [no-untyped-def]
        return self.deposit.expirationDate > datetime.utcnow() if self.deposit else False

    @property
    def hasPhysicalVenues(self):  # type: ignore [no-untyped-def]
        for user_offerer in self.UserOfferers:
            if any(not venue.isVirtual for venue in user_offerer.offerer.managedVenues):
                return True

        return False

    @property
    def is_eligible(self) -> bool:
        return self.eligibility is not None

    @property
    def latest_birthday(self) -> date:
        return _get_latest_birthday(self.dateOfBirth.date())  # type: ignore [union-attr]

    @property
    def real_wallet_balance(self):  # type: ignore [no-untyped-def]
        balance = db.session.query(sa.func.get_wallet_balance(self.id, True)).scalar()
        # Balance can be negative if the user has booked in the past
        # but their deposit has expired. We don't want to expose a
        # negative number.
        return max(0, balance)

    @property
    def wallet_balance(self):  # type: ignore [no-untyped-def]
        balance = db.session.query(sa.func.get_wallet_balance(self.id, False)).scalar()
        return max(0, balance)

    @property
    def suspension_reason(self) -> str | None:
        """
        Reason for the active suspension.
        suspension_history is sorted by ascending date so the last item is the most recent (see UserSuspension).
        """
        if (
            not self.isActive
            and self.suspension_history
            and self.suspension_history[-1].eventType == SuspensionEventType.SUSPENDED
        ):
            return self.suspension_history[-1].reasonCode
        return None

    @property
    def suspension_date(self) -> datetime | None:
        """
        Date and time when the inactive account was suspended for the last time.
        suspension_history is sorted by ascending date so the last item is the most recent (see UserSuspension).
        """
        if (
            not self.isActive
            and self.suspension_history
            and self.suspension_history[-1].eventType == SuspensionEventType.SUSPENDED
        ):
            return self.suspension_history[-1].eventDate
        return None

    @property
    def account_state(self) -> AccountState:
        if self.isActive:
            return AccountState.ACTIVE

        if self.suspension_history:
            suspension_event = self.suspension_history[-1]

            if suspension_event.eventType == SuspensionEventType.SUSPENDED:

                if suspension_event.reasonCode == SuspensionReason.DELETED:
                    return AccountState.DELETED
                if suspension_event.reasonCode == SuspensionReason.UPON_USER_REQUEST:
                    return AccountState.SUSPENDED_UPON_USER_REQUEST

                return AccountState.SUSPENDED

        return AccountState.INACTIVE

    @property
    def is_account_deleted(self) -> bool:
        return self.account_state == AccountState.DELETED

    @property
    def is_account_suspended_upon_user_request(self) -> bool:
        return self.account_state == AccountState.SUSPENDED_UPON_USER_REQUEST

    @hybrid_property
    def is_beneficiary(self) -> bool:
        return self.has_beneficiary_role or self.has_underage_beneficiary_role

    @is_beneficiary.expression  # type: ignore [no-redef]
    def is_beneficiary(cls):  # pylint: disable=no-self-argument
        return expression.or_(
            cls.roles.contains([UserRole.BENEFICIARY]), cls.roles.contains([UserRole.UNDERAGE_BENEFICIARY])
        )

    @hybrid_property
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
    def is_phone_validated(cls):  # pylint: disable=no-self-argument
        return cls.phoneValidationStatus == PhoneValidationStatusType.VALIDATED

    @hybrid_property
    def is_phone_validation_skipped(self):
        return self.phoneValidationStatus == PhoneValidationStatusType.SKIPPED_BY_SUPPORT

    @is_phone_validation_skipped.expression  # type: ignore [no-redef]
    def is_phone_validation_skipped(cls):  # pylint: disable=no-self-argument
        return cls.phoneValidationStatus == PhoneValidationStatusType.SKIPPED_BY_SUPPORT

    @hybrid_property
    def has_admin_role(self) -> bool:
        return UserRole.ADMIN in self.roles if self.roles else False

    @has_admin_role.expression  # type: ignore [no-redef]
    def has_admin_role(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.roles.contains([UserRole.ADMIN])

    @hybrid_property
    def has_beneficiary_role(self) -> bool:
        return UserRole.BENEFICIARY in self.roles if self.roles else False

    @has_beneficiary_role.expression  # type: ignore [no-redef]
    def has_beneficiary_role(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.roles.contains([UserRole.BENEFICIARY])

    @hybrid_property
    def has_pro_role(self) -> bool:
        return UserRole.PRO in self.roles if self.roles else False

    @has_pro_role.expression  # type: ignore [no-redef]
    def has_pro_role(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.roles.contains([UserRole.PRO])

    @hybrid_property
    def has_underage_beneficiary_role(self) -> bool:
        return UserRole.UNDERAGE_BENEFICIARY in self.roles if self.roles else False

    @has_underage_beneficiary_role.expression  # type: ignore [no-redef]
    def has_underage_beneficiary_role(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.roles.contains([UserRole.UNDERAGE_BENEFICIARY])

    @hybrid_property
    def has_test_role(self) -> bool:
        return UserRole.TEST in self.roles if self.roles else False

    @has_test_role.expression  # type: ignore [no-redef]
    def has_test_role(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.roles.contains([UserRole.TEST])


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


class Favorite(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    __tablename__ = "favorite"

    userId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=False)

    user = orm.relationship("User", foreign_keys=[userId], backref="favorites")  # type: ignore [misc]

    offerId = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id"), index=True, nullable=False)

    offer = orm.relationship("Offer", foreign_keys=[offerId], backref="favorites")  # type: ignore [misc]

    mediationId = sa.Column(sa.BigInteger, sa.ForeignKey("mediation.id"), index=True, nullable=True)

    mediation = orm.relationship("Mediation", foreign_keys=[mediationId], backref="favorites")  # type: ignore [misc]

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
    VALIDATION = "VALIDATION"
    ADMIN_VALIDATION = "ADMIN_VALIDATION"
    ADMIN_UPDATE_REQUEST = "ADMIN_UPDATE_REQUEST"


class UserEmailHistory(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    __tablename__ = "user_email_history"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    userId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="SET NULL"), index=True, nullable=True)
    user = orm.relationship("User", foreign_keys=[userId], backref=orm.backref("email_history", passive_deletes=True))  # type: ignore [misc]

    oldUserEmail: str = sa.Column(sa.String(120), nullable=False, unique=False, index=True)
    oldDomainEmail: str = sa.Column(sa.String(120), nullable=False, unique=False, index=True)

    newUserEmail: str = sa.Column(sa.String(120), nullable=False, unique=False, index=True)
    newDomainEmail: str = sa.Column(sa.String(120), nullable=False, unique=False, index=True)

    creationDate: datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    eventType = sa.Column(sa.Enum(EmailHistoryEventTypeEnum), nullable=False)

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
    def build_update_request(cls, user: User, new_email: str, admin: bool = False) -> "UserEmailHistory":
        if admin:
            return cls._build(user, new_email, event_type=EmailHistoryEventTypeEnum.ADMIN_UPDATE_REQUEST)
        return cls._build(user, new_email, event_type=EmailHistoryEventTypeEnum.UPDATE_REQUEST)

    @classmethod
    def build_validation(cls, user: User, new_email: str, admin: bool) -> "UserEmailHistory":
        if admin:
            return cls._build(user, new_email, event_type=EmailHistoryEventTypeEnum.ADMIN_VALIDATION)
        return cls._build(user, new_email, event_type=EmailHistoryEventTypeEnum.VALIDATION)

    @hybrid_property
    def oldEmail(self) -> str:
        return f"{self.oldUserEmail}@{self.oldDomainEmail}"

    @oldEmail.expression  # type: ignore [no-redef]
    def oldEmail(cls):  # pylint: disable=no-self-argument # type: ignore[no-redef]
        return func.concat(cls.oldUserEmail, "@", cls.oldDomainEmail)

    @hybrid_property
    def newEmail(self) -> str:
        return f"{self.newUserEmail}@{self.newDomainEmail}"

    @newEmail.expression  # type: ignore [no-redef]
    def newEmail(cls):  # pylint: disable=no-self-argument # type: ignore[no-redef]
        return func.concat(cls.newUserEmail, "@", cls.newDomainEmail)


class UserSuspension(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    __tablename__ = "user_suspension"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    userId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)
    user = orm.relationship(  # type: ignore [misc]
        "User",
        foreign_keys=[userId],
        backref=orm.backref(
            "suspension_history", order_by="UserSuspension.eventDate.asc().nullsfirst()", passive_deletes=True
        ),
    )

    eventType = sa.Column(sa.Enum(SuspensionEventType), nullable=False)

    # nullable because of old suspensions without date migrated here; but mandatory for new actions
    eventDate = sa.Column(sa.DateTime, nullable=True, server_default=sa.func.now())

    # Super-admin or the user himself who initiated the suspension event on user account
    # nullable because of old suspensions without author migrated here; but mandatory for new actions
    actorUserId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    actorUser = orm.relationship("User", foreign_keys=[actorUserId])  # type: ignore [misc]

    # Reason is filled in only when suspended but could be useful also when unsuspended for support traceability
    reasonCode = sa.Column(sa.Enum(SuspensionReason), nullable=True)
