from dataclasses import dataclass
from datetime import date
from datetime import datetime
from decimal import Decimal
import enum
from hashlib import md5
from typing import Optional

import bcrypt
from dateutil.relativedelta import relativedelta
from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import LargeBinary
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import backref
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from pcapi import settings
from pcapi.core.bookings.models import Booking
from pcapi.core.offers.models import Stock
from pcapi.core.users import constants
from pcapi.models.db import Model
from pcapi.models.db import db
from pcapi.models.deposit import Deposit
from pcapi.models.needs_validation_mixin import NeedsValidationMixin
from pcapi.models.pc_object import PcObject
from pcapi.models.user_offerer import UserOfferer
from pcapi.models.versioned_mixin import VersionedMixin


ALGORITHM_HS_256 = "HS256"

VOID_FIRST_NAME = ""
VOID_PUBLIC_NAME = "   "


class TokenType(enum.Enum):
    RESET_PASSWORD = "reset-password"
    EMAIL_VALIDATION = "email-validation"
    ID_CHECK = "id-check"


class Token(PcObject, Model):
    __tablename__ = "token"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    userId = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)

    user = relationship("User", foreign_keys=[userId], backref=backref("tokens", passive_deletes=True))

    value = Column(String, index=True, unique=True, nullable=False)

    type = Column(Enum(TokenType, create_constraint=False), nullable=False)

    creationDate = Column(DateTime, nullable=False, server_default=func.now())

    expirationDate = Column(DateTime, nullable=True)


def _hash_password_with_bcrypt(clear_text: str) -> bytes:
    return bcrypt.hashpw(clear_text.encode("utf-8"), bcrypt.gensalt())


def _check_password_with_bcrypt(clear_text: str, hashed: str) -> bool:
    return bcrypt.checkpw(clear_text.encode("utf-8"), hashed)


def _hash_password_with_md5(clear_text: str) -> bytes:
    if not settings.IS_DEV:
        raise RuntimeError("This password hasher should not be used outside tests.")
    return md5(clear_text.encode("utf-8")).hexdigest().encode("utf-8")


def _check_password_with_md5(clear_text: str, hashed: str) -> bool:
    if not settings.IS_DEV:
        raise RuntimeError("This password hasher should not be used outside tests.")
    # non constant-time comparison because it's test-only
    return _hash_password_with_md5(clear_text) == hashed


def hash_password(clear_text: str) -> bytes:
    hasher = _hash_password_with_md5 if settings.IS_DEV else _hash_password_with_bcrypt
    return hasher(clear_text)


def check_password(clear_text: str, hashed: str) -> bool:
    checker = _check_password_with_md5 if settings.IS_DEV else _check_password_with_bcrypt
    return checker(clear_text, hashed)


class User(PcObject, Model, NeedsValidationMixin, VersionedMixin):
    __tablename__ = "user"

    email = Column(String(120), nullable=False, unique=True)

    address = Column(Text, nullable=True)

    city = Column(String(100), nullable=True)

    clearTextPassword = None

    culturalSurveyId = Column(UUID(as_uuid=True), nullable=True)

    culturalSurveyFilledDate = Column(DateTime, nullable=True)

    dateCreated = Column(DateTime, nullable=False, default=datetime.utcnow)

    dateOfBirth = Column(DateTime, nullable=True)

    departementCode = Column(String(3), nullable=False)

    firstName = Column(String(128), nullable=True)

    isAdmin = Column(
        Boolean,
        CheckConstraint(
            '"isBeneficiary" IS FALSE OR "isAdmin" IS FALSE',
            name="check_admin_is_not_beneficiary",
        ),
        nullable=False,
        server_default=expression.false(),
        default=False,
    )

    lastName = Column(String(128), nullable=True)

    lastConnectionDate = Column(DateTime, nullable=True)

    needsToFillCulturalSurvey = Column(Boolean, server_default=expression.true(), default=True)

    notificationSubscriptions = Column(MutableDict.as_mutable(JSONB), nullable=True)

    offerers = relationship("Offerer", secondary="user_offerer")

    password = Column(LargeBinary(60), nullable=False)

    phoneNumber = Column(String(20), nullable=True)

    postalCode = Column(String(5), nullable=True)

    publicName = Column(String(255), nullable=False)

    resetPasswordToken = Column(String(10), unique=True)

    resetPasswordTokenValidityLimit = Column(DateTime)

    civility = Column(String(20), nullable=True)

    activity = Column(String(128), nullable=True)

    hasSeenTutorials = Column(Boolean, nullable=True)

    hasSeenProTutorials = Column(Boolean, nullable=False, server_default=expression.false())

    isEmailValidated = Column(Boolean, nullable=True, server_default=expression.false())

    isBeneficiary = Column(Boolean, nullable=False, server_default=expression.false())

    hasAllowedRecommendations = Column(Boolean, nullable=False, server_default=expression.false())

    # FIXME (dbaty, 2020-12-14): once v114 has been deployed, populate
    # existing rows with the empty string and add NOT NULL constraint.
    suspensionReason = Column(Text, nullable=True, default="")

    # FIXME (dbaty, 2020-12-14): once v114 has been deployed, populate
    # existing rows, remove this field and let the User model
    # use DeactivableMixin. We'll need to add a migration that adds a
    # NOT NULL constraint.
    isActive = Column(Boolean, nullable=True, server_default=expression.true(), default=True)

    def checkPassword(self, passwordToCheck):
        return check_password(passwordToCheck, self.password)

    def get_id(self):
        return str(self.id)

    def has_access(self, offerer_id):
        if self.isAdmin:
            return True

        return db.session.query(
            UserOfferer.query.filter(
                (UserOfferer.offererId == offerer_id)
                & (UserOfferer.userId == self.id)
                & (UserOfferer.validationToken.is_(None))
            ).exists()
        ).scalar()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def populate_from_dict(self, data):
        super().populate_from_dict(data)
        if data.__contains__("password") and data["password"]:
            self.setPassword(data["password"])

    def setPassword(self, newpass):
        self.clearTextPassword = newpass
        self.password = hash_password(newpass)
        self.resetPasswordToken = None
        self.resetPasswordTokenValidityLimit = None

    def get_not_cancelled_bookings(self) -> Booking:
        return (
            db.session.query(Booking)
            .with_parent(self)
            .filter_by(isCancelled=False)
            .options(joinedload(Booking.stock).joinedload(Stock.offer))
            .all()
        )

    def calculate_age(self) -> Optional[int]:
        if self.dateOfBirth is None:
            return None

        return relativedelta(date.today(), self.dateOfBirth.date()).years

    @property
    def expenses(self):
        from pcapi.core.users.api import user_expenses

        return user_expenses(self)

    @property
    def deposit(self) -> Optional[Deposit]:
        return self.deposits[0] if len(self.deposits) > 0 else None

    @property
    def deposit_expiration_date(self) -> Optional[datetime]:
        return self.deposit.expirationDate if self.deposit else None

    @property
    def deposit_version(self) -> Optional[int]:
        return self.deposit.version if self.deposit else None

    @property
    def real_wallet_balance(self):
        balance = db.session.query(func.get_wallet_balance(self.id, True)).scalar()
        # Balance can be negative if the user has booked in the past
        # but their deposit has expired. We don't want to expose a
        # negative number.
        return max(0, balance)

    @property
    def wallet_balance(self):
        balance = db.session.query(func.get_wallet_balance(self.id, False)).scalar()
        return max(0, balance)

    @property
    def wallet_is_activated(self):
        return len(self.deposits) > 0

    @property
    def hasPhysicalVenues(self):
        for offerer in self.offerers:
            if any(not venue.isVirtual for venue in offerer.managedVenues):
                return True

        return False

    @property
    def needsToSeeTutorials(self):
        return self.isBeneficiary and not self.hasSeenTutorials

    @property
    def hasOffers(self):
        return any(offerer.nOffers > 0 for offerer in self.offerers)

    @property
    def is_eligible(self) -> bool:
        age = self.calculate_age()
        return age is not None and age == constants.ELIGIBILITY_AGE


class ExpenseDomain(enum.Enum):
    ALL = "all"
    DIGITAL = "digital"
    PHYSICAL = "physical"


@dataclass
class Expense:
    domain: ExpenseDomain
    current: Decimal
    limit: Decimal
