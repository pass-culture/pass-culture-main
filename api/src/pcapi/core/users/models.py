import copy
from dataclasses import asdict
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from decimal import Decimal
import enum
from operator import attrgetter
import typing
from typing import Optional

import flask
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
from pcapi.core.users.exceptions import InvalidUserRoleException
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.needs_validation_mixin import NeedsValidationMixin
from pcapi.models.pc_object import PcObject
from pcapi.utils import crypto


if typing.TYPE_CHECKING:
    from pcapi.core.payments.models import Deposit
    from pcapi.core.payments.models import DepositType


VOID_FIRST_NAME = ""
VOID_PUBLIC_NAME = "   "


class TokenType(enum.Enum):
    RESET_PASSWORD = "reset-password"
    EMAIL_VALIDATION = "email-validation"
    PHONE_VALIDATION = "phone-validation"


class PhoneValidationStatusType(enum.Enum):
    BLOCKED_TOO_MANY_CODE_SENDINGS = "blocked-too-many-code-sendings"
    BLOCKED_TOO_MANY_CODE_VERIFICATION_TRIES = "blocked-too-many-code-verification-tries"
    VALIDATED = "validated"


class Token(PcObject, Model):
    __tablename__ = "token"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    userId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)

    user = orm.relationship("User", foreign_keys=[userId], backref=orm.backref("tokens", passive_deletes=True))

    value = sa.Column(sa.String, index=True, unique=True, nullable=False)

    type = sa.Column(sa.Enum(TokenType, create_constraint=False), nullable=False)

    creationDate = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    expirationDate = sa.Column(sa.DateTime, nullable=True)

    isUsed = sa.Column(sa.Boolean, nullable=False, server_default=expression.false(), default=False)


class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    BENEFICIARY = "BENEFICIARY"
    PRO = "PRO"
    # TODO(bcalvez) : remove this role as soon as we get a proper identification mecanism in F.A.
    JOUVE = "JOUVE"
    UNDERAGE_BENEFICIARY = "UNDERAGE_BENEFICIARY"


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


class SubscriptionState(enum.Enum):
    account_created = "account_created"
    beneficiary_15_17 = "beneficiary_15_17"
    beneficiary_18 = "beneficiary_18"
    email_validated = "email_validated"
    identity_check_ko = "identity_check_ko"
    identity_check_pending = "identity_check_pending"
    identity_check_validated = "identity_check_validated"
    phone_validated = "phone_validated"
    phone_validation_ko = "phone_validation_ko"
    profile_completed = "profile_completed"
    rejected_by_admin = "rejected_by_admin"
    user_profiling_ko = "user_profiling_ko"
    user_profiling_validated = "user_profiling_validated"


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
    M: str = "M"
    F: str = "F"
    NULL: str = "NULL"


class User(PcObject, Model, NeedsValidationMixin):
    __tablename__ = "user"

    activity = sa.Column(sa.String(128), nullable=True)
    address = sa.Column(sa.Text, nullable=True)
    city = sa.Column(sa.String(100), nullable=True)
    civility = sa.Column(sa.String(20), nullable=True)
    clearTextPassword = None
    comment = sa.Column(sa.Text(), nullable=True)
    culturalSurveyFilledDate = sa.Column(sa.DateTime, nullable=True)
    culturalSurveyId = sa.Column(postgresql.UUID(as_uuid=True), nullable=True)
    dateCreated = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)
    dateOfBirth = sa.Column(sa.DateTime, nullable=True)
    departementCode = sa.Column(sa.String(3), nullable=True)
    email = sa.Column(sa.String(120), nullable=False, unique=True)
    externalIds = sa.Column(postgresql.json.JSONB, nullable=True, default={}, server_default="{}")
    extraData = sa.Column(MutableDict.as_mutable(postgresql.json.JSONB), nullable=True, default={}, server_default="{}")
    firstName = sa.Column(sa.String(128), nullable=True)
    gender = sa.Column(sa.Enum(GenderEnum, create_constraint=False), nullable=True)
    hasSeenTutorials = sa.Column(sa.Boolean, nullable=True)
    hasSeenProTutorials = sa.Column(sa.Boolean, nullable=False, server_default=expression.false())
    idPieceNumber = sa.Column(sa.String, nullable=True, unique=True)
    ineHash = sa.Column(sa.Text, nullable=True, unique=True)

    # FIXME (dbaty, 2020-12-14): once v114 has been deployed, populate
    # existing rows, remove this field and let the User model
    # use DeactivableMixin. We'll need to add a migration that adds a
    # NOT NULL constraint.
    isActive = sa.Column(sa.Boolean, nullable=True, server_default=expression.true(), default=True)
    isEmailValidated = sa.Column(sa.Boolean, nullable=True, server_default=expression.false())
    lastConnectionDate = sa.Column(sa.DateTime, nullable=True)
    lastName = sa.Column(sa.String(128), nullable=True)
    married_name = sa.Column(sa.String(128), nullable=True)
    needsToFillCulturalSurvey = sa.Column(sa.Boolean, server_default=expression.true(), default=True)
    notificationSubscriptions = sa.Column(
        MutableDict.as_mutable(postgresql.json.JSONB),
        nullable=True,
        default=asdict(NotificationSubscriptions()),
        server_default="""{"marketing_push": true, "marketing_email": true}""",
    )
    offerers = orm.relationship("Offerer", secondary="user_offerer")
    password = sa.Column(sa.LargeBinary(60), nullable=False)
    phoneNumber = sa.Column(sa.String(20), nullable=True)
    phoneValidationStatus = sa.Column(sa.Enum(PhoneValidationStatusType, create_constraint=False), nullable=True)
    postalCode = sa.Column(sa.String(5), nullable=True)
    publicName = sa.Column(sa.String(255), nullable=False)
    recreditAmountToShow = sa.Column(sa.Numeric(10, 2), nullable=True)
    roles = sa.Column(
        MutableList.as_mutable(postgresql.ARRAY(sa.Enum(UserRole, native_enum=False, create_constraint=False))),
        nullable=False,
        server_default="{}",
    )
    schoolType = sa.Column(sa.Enum(SchoolTypeEnum, create_constraint=False), nullable=True)
    subscriptionState = sa.Column(sa.Enum(SubscriptionState, create_constraint=False), nullable=True)

    def _add_role(self, role: UserRole) -> None:
        if self.roles is None:
            self.roles = []
        if self.roles and role in self.roles:
            return

        current_roles = copy.deepcopy(self.roles) if self.roles else []
        updated_roles = current_roles + [role]

        if UserRole.BENEFICIARY in updated_roles and UserRole.ADMIN in updated_roles:
            raise InvalidUserRoleException("User can't have both ADMIN and BENEFICIARY role")

        self.roles = updated_roles

    def add_admin_role(self) -> None:
        if self.is_beneficiary:  # pylint: disable=using-constant-test
            raise InvalidUserRoleException("User can't have both ADMIN and BENEFICIARY role")

        self._add_role(UserRole.ADMIN)

    def add_beneficiary_role(self) -> None:
        if self.has_admin_role:  # pylint: disable=using-constant-test
            raise InvalidUserRoleException("User can't have both ADMIN and BENEFICIARY role")
        self._add_role(UserRole.BENEFICIARY)

    def add_pro_role(self) -> None:
        self._add_role(UserRole.PRO)

    def add_underage_beneficiary_role(self) -> None:
        if self.has_admin_role:  # pylint: disable=using-constant-test
            raise InvalidUserRoleException("User can't have both ADMIN and BENEFICIARY role")
        self._add_role(UserRole.UNDERAGE_BENEFICIARY)

    def checkPassword(self, passwordToCheck):
        return crypto.check_password(passwordToCheck, self.password)

    def get_notification_subscriptions(self) -> NotificationSubscriptions:
        return NotificationSubscriptions(**self.notificationSubscriptions or {})

    def has_access(self, offerer_id: int) -> bool:
        # FIXME (dbaty, 2021-11-26): consider moving to a function in `core.users.api`?
        from pcapi.models.user_offerer import UserOfferer

        if self.has_admin_role:  # pylint: disable=using-constant-test
            return True
        return db.session.query(
            UserOfferer.query.filter(
                (UserOfferer.offererId == offerer_id)
                & (UserOfferer.userId == self.id)
                & (UserOfferer.validationToken.is_(None))
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
        return self.isActive

    @property
    def is_anonymous(self) -> bool:  # required by flask-login
        return False

    def get_id(self):  # required by flask-login
        return str(self.id)

    def is_super_admin(self) -> bool:
        if settings.IS_PROD:
            return self.email in settings.SUPER_ADMIN_EMAIL_ADDRESSES
        return self.has_admin_role

    def populate_from_dict(self, data):
        super().populate_from_dict(data)
        if data.__contains__("password") and data["password"]:
            self.setPassword(data["password"])

    def remove_admin_role(self) -> None:
        if self.has_admin_role:  # pylint: disable=using-constant-test
            self.roles.remove(UserRole.ADMIN)

    def remove_underage_beneficiary_role(self) -> None:
        if self.has_underage_beneficiary_role:  # pylint: disable=using-constant-test
            self.roles.remove(UserRole.UNDERAGE_BENEFICIARY)

    def remove_beneficiary_role(self) -> None:
        if self.has_beneficiary_role:  # pylint: disable=using-constant-test
            self.roles.remove(UserRole.BENEFICIARY)

    def remove_pro_role(self) -> None:
        if self.has_pro_role:  # pylint: disable=using-constant-test
            self.roles.remove(UserRole.PRO)

    def setPassword(self, newpass):
        self.clearTextPassword = newpass
        self.password = crypto.hash_password(newpass)

    @property
    def age(self) -> Optional[int]:
        return users_utils.get_age_from_birth_date(self.dateOfBirth.date()) if self.dateOfBirth is not None else None

    @property
    def deposit(self) -> Optional["Deposit"]:
        if len(self.deposits) == 0:
            return None
        return sorted(self.deposits, key=attrgetter("expirationDate"), reverse=True)[0]

    @property
    def deposit_activation_date(self) -> Optional[datetime]:
        return self.deposit.dateCreated if self.deposit else None

    @property
    def deposit_expiration_date(self) -> Optional[datetime]:
        return self.deposit.expirationDate if self.deposit else None

    @property
    def deposit_type(self) -> Optional["DepositType"]:
        return self.deposit.type if self.deposit else None

    @property
    def deposit_version(self) -> Optional[int]:
        return self.deposit.version if self.deposit else None

    @property
    def eligibility(self) -> Optional[EligibilityType]:
        from pcapi.core.users import api as users_api

        return users_api.get_eligibility_at_date(self.dateOfBirth, datetime.now())

    @property
    def has_active_deposit(self):
        return self.deposit.expirationDate > datetime.utcnow() if self.deposit else False

    @property
    def hasPhysicalVenues(self):
        for offerer in self.offerers:
            if any(not venue.isVirtual for venue in offerer.managedVenues):
                return True

        return False

    @property
    def is_eligible(self) -> bool:
        return self.eligibility is not None

    @property
    def latest_birthday(self) -> date:
        return _get_latest_birthday(self.dateOfBirth.date())

    @property
    def needsToSeeTutorials(self):
        return self.is_beneficiary and not self.hasSeenTutorials

    @property
    def real_wallet_balance(self):
        balance = db.session.query(sa.func.get_wallet_balance(self.id, True)).scalar()
        # Balance can be negative if the user has booked in the past
        # but their deposit has expired. We don't want to expose a
        # negative number.
        return max(0, balance)

    @property
    def wallet_balance(self):
        balance = db.session.query(sa.func.get_wallet_balance(self.id, False)).scalar()
        return max(0, balance)

    @property
    def suspension_reason(self) -> Optional[str]:
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
    def suspension_date(self) -> Optional[datetime]:
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

    @hybrid_property
    def is_beneficiary(self):
        return self.has_beneficiary_role or self.has_underage_beneficiary_role

    @is_beneficiary.expression
    def is_beneficiary(cls):  # pylint: disable=no-self-argument
        return expression.or_(
            cls.roles.contains([UserRole.BENEFICIARY]), cls.roles.contains([UserRole.UNDERAGE_BENEFICIARY])
        )

    @hybrid_property
    def is_phone_validated(self):
        return self.phoneValidationStatus == PhoneValidationStatusType.VALIDATED

    @is_phone_validated.expression
    def is_phone_validated(cls):  # pylint: disable=no-self-argument
        return cls.phoneValidationStatus == PhoneValidationStatusType.VALIDATED

    @hybrid_property
    def has_admin_role(self) -> bool:
        return UserRole.ADMIN in self.roles if self.roles else False

    @has_admin_role.expression
    def has_admin_role(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.roles.contains([UserRole.ADMIN])

    @hybrid_property
    def has_beneficiary_role(self) -> bool:
        return UserRole.BENEFICIARY in self.roles if self.roles else False

    @has_beneficiary_role.expression
    def has_beneficiary_role(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.roles.contains([UserRole.BENEFICIARY])

    @hybrid_property
    def has_pro_role(self) -> bool:
        return UserRole.PRO in self.roles if self.roles else False

    @has_pro_role.expression
    def has_pro_role(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.roles.contains([UserRole.PRO])

    @hybrid_property
    def has_underage_beneficiary_role(self) -> bool:
        return UserRole.UNDERAGE_BENEFICIARY in self.roles if self.roles else False

    @has_underage_beneficiary_role.expression
    def has_underage_beneficiary_role(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.roles.contains([UserRole.UNDERAGE_BENEFICIARY])

    @classmethod
    def init_subscription_state_machine(cls, obj, *args, **kwargs) -> None:
        from pcapi.core.subscription import transitions as subscription_transitions

        if not kwargs:
            if isinstance(args[-1], dict):
                kwargs = args[-1]

        initial_state = obj.subscriptionState or kwargs.get("subscriptionState", SubscriptionState.account_created)

        if not hasattr(flask.g, "subscription_machine"):
            subscription_transitions.install_machine()

        flask.g.subscription_machine.add_model(obj, initial_state)

        setattr(
            obj,
            "_subscriptionStateMachine",
            flask.g.subscription_machine,
        )

    @classmethod
    def remove_subscription_state_machine(cls, target, attrs):
        # avoid trying to remove the object multiple times from the machine
        if attrs is None:
            try:
                flask.g.subscription_machine.remove_model(target)
            except Exception:  # pylint: disable=broad-except
                pass


sa.event.listen(User, "init", User.init_subscription_state_machine)
sa.event.listen(User, "load", User.init_subscription_state_machine)

sa.event.listen(User, "expire", User.remove_subscription_state_machine)


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
    digital: Optional[Credit] = None
    physical: Optional[Credit] = None


class Favorite(PcObject, Model):
    __tablename__ = "favorite"

    userId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=False)

    user = orm.relationship("User", foreign_keys=[userId], backref="favorites")

    offerId = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id"), index=True, nullable=False)

    offer = orm.relationship("Offer", foreign_keys=[offerId], backref="favorites")

    mediationId = sa.Column(sa.BigInteger, sa.ForeignKey("mediation.id"), index=True, nullable=True)

    mediation = orm.relationship("Mediation", foreign_keys=[mediationId], backref="favorites")

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


class UserEmailHistory(PcObject, Model):
    __tablename__ = "user_email_history"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    userId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="SET NULL"), index=True, nullable=True)
    user = orm.relationship("User", foreign_keys=[userId], backref=orm.backref("email_history", passive_deletes=True))

    oldUserEmail = sa.Column(sa.String(120), nullable=False, unique=False, index=True)
    oldDomainEmail = sa.Column(sa.String(120), nullable=False, unique=False, index=True)

    newUserEmail = sa.Column(sa.String(120), nullable=False, unique=False, index=True)
    newDomainEmail = sa.Column(sa.String(120), nullable=False, unique=False, index=True)

    creationDate = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

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
    def build_update_request(cls, user: User, new_email: str) -> "UserEmailHistory":
        return cls._build(user, new_email, event_type=EmailHistoryEventTypeEnum.UPDATE_REQUEST)

    @classmethod
    def build_validation(cls, user: User, new_email: str, admin: bool) -> "UserEmailHistory":
        if admin:
            return cls._build(user, new_email, event_type=EmailHistoryEventTypeEnum.ADMIN_VALIDATION)
        return cls._build(user, new_email, event_type=EmailHistoryEventTypeEnum.VALIDATION)

    @hybrid_property
    def oldEmail(self) -> str:
        return f"{self.oldUserEmail}@{self.oldDomainEmail}"

    @oldEmail.expression
    def oldEmail(cls):  # pylint: disable=no-self-argument # type: ignore[no-redef]
        return func.concat(cls.oldUserEmail, "@", cls.oldDomainEmail)

    @hybrid_property
    def newEmail(self) -> str:
        return f"{self.newUserEmail}@{self.newDomainEmail}"

    @newEmail.expression
    def newEmail(cls):  # pylint: disable=no-self-argument # type: ignore[no-redef]
        return func.concat(cls.newUserEmail, "@", cls.newDomainEmail)


class UserSuspension(PcObject, Model):
    __tablename__ = "user_suspension"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    userId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)
    user = orm.relationship(
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
    actorUser = orm.relationship("User", foreign_keys=[actorUserId])

    # Reason is filled in only when suspended but could be useful also when unsuspended for support traceability
    reasonCode = sa.Column(sa.Enum(SuspensionReason), nullable=True)
