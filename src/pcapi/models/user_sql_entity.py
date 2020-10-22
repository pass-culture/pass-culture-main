from datetime import datetime
from decimal import Decimal
from hashlib import md5

import bcrypt
from sqlalchemy import LargeBinary, \
    Boolean, \
    CheckConstraint, \
    Column, \
    func, \
    DateTime, \
    String, \
    Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, joinedload
from sqlalchemy.sql import expression

from pcapi.domain.expenses import get_expenses
from pcapi.core.bookings.models import Booking
from pcapi.models.db import Model, db
from pcapi.models.deposit import Deposit
from pcapi.models.needs_validation_mixin import NeedsValidationMixin
from pcapi.models.pc_object import PcObject
from pcapi.models.stock_sql_entity import StockSQLEntity
from pcapi.models.user_offerer import UserOfferer, RightsType
from pcapi.models.versioned_mixin import VersionedMixin
from pcapi.utils.config import IS_DEV



def _hash_password_with_bcrypt(clear_text: str) -> bytes:
    return bcrypt.hashpw(clear_text.encode('utf-8'), bcrypt.gensalt())


def _check_password_with_bcrypt(clear_text: str, hashed: str) -> bool:
    return bcrypt.checkpw(clear_text.encode('utf-8'), hashed)


def _hash_password_with_md5(clear_text: str) -> bytes:
    if not IS_DEV:
        raise RuntimeError("This password hasher should not be used outside tests.")
    return md5(clear_text.encode('utf-8')).hexdigest().encode('utf-8')


def _check_password_with_md5(clear_text: str, hashed: str) -> bool:
    if not IS_DEV:
        raise RuntimeError("This password hasher should not be used outside tests.")
    # non constant-time comparison because it's test-only
    return _hash_password_with_md5(clear_text) == hashed


def hash_password(clear_text: str) -> bytes:
    hasher = _hash_password_with_md5 if IS_DEV else _hash_password_with_bcrypt
    return hasher(clear_text)


def check_password(clear_text: str, hashed: str) -> bool:
    checker = _check_password_with_md5 if IS_DEV else _check_password_with_bcrypt
    return checker(clear_text, hashed)


class UserSQLEntity(PcObject,
                    Model,
                    NeedsValidationMixin,
                    VersionedMixin
                    ):
    __tablename__ = 'user'

    email = Column(String(120), nullable=False, unique=True)

    address = Column(Text, nullable=True)

    canBookFreeOffers = Column(Boolean,
                               nullable=False,
                               server_default=expression.true(),
                               default=True)

    city = Column(String(100), nullable=True)

    clearTextPassword = None

    culturalSurveyId = Column(UUID(as_uuid=True), nullable=True)

    culturalSurveyFilledDate = Column(DateTime, nullable=True)

    dateCreated = Column(DateTime,
                         nullable=False,
                         default=datetime.utcnow)

    dateOfBirth = Column(DateTime,
                         nullable=True)

    departementCode = Column(String(3), nullable=False)

    firstName = Column(String(128), nullable=True)

    isAdmin = Column(Boolean,
                     CheckConstraint('("canBookFreeOffers" IS FALSE AND "isAdmin" IS TRUE)'
                                     + 'OR ("isAdmin" IS FALSE)',
                                     name='check_admin_cannot_book_free_offers'),
                     nullable=False,
                     server_default=expression.false(),
                     default=False)

    lastName = Column(String(128), nullable=True)

    lastConnectionDate = Column(DateTime, nullable=True)

    needsToFillCulturalSurvey = Column(Boolean,
                                       server_default=expression.true(),
                                       default=True)

    offerers = relationship('Offerer',
                            secondary='user_offerer')

    password = Column(LargeBinary(60), nullable=False)

    phoneNumber = Column(String(20), nullable=True)

    postalCode = Column(String(5), nullable=True)

    publicName = Column(String(255), nullable=False)

    resetPasswordToken = Column(String(10), unique=True)

    resetPasswordTokenValidityLimit = Column(DateTime)

    civility = Column(String(20), nullable=True)

    activity = Column(String(128), nullable=True)

    hasSeenTutorials = Column(Boolean, nullable=True)

    def checkPassword(self, passwordToCheck):
        return check_password(passwordToCheck, self.password)

    def get_id(self):
        return str(self.id)

    def hasRights(self, rights, offerer_id):
        if self.isAdmin:
            return True

        if rights == RightsType.editor:
            compatible_rights = [RightsType.editor, RightsType.admin]
        else:
            compatible_rights = [rights]

        user_offerer = UserOfferer.query.filter(
            (UserOfferer.offererId == offerer_id)
            & (UserOfferer.userId == self.id)
            & (UserOfferer.validationToken.is_(None))
            & (UserOfferer.rights.in_(compatible_rights))
        ).first()
        return user_offerer is not None

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def populate_from_dict(self, data):
        super(UserSQLEntity, self).populate_from_dict(data)
        if data.__contains__('password') and data['password']:
            self.setPassword(data['password'])

    def setPassword(self, newpass):
        self.clearTextPassword = newpass
        self.password = hash_password(newpass)
        self.resetPasswordToken = None
        self.resetPasswordTokenValidityLimit = None

    def bookings_query(self):
        return db.session.query(Booking).with_parent(self)

    @property
    def expenses(self):
        bookings = self.bookings_query().options(
            joinedload(Booking.stock).
            joinedload(StockSQLEntity.offer)).all()
        return get_expenses(bookings)

    @property
    def real_wallet_balance(self):
        return db.session.query(func.get_wallet_balance(self.id, True)).scalar()

    @property
    def wallet_balance(self):
        return db.session.query(func.get_wallet_balance(self.id, False)).scalar()

    @property
    def wallet_is_activated(self):
        return len(self.deposits) > 0

    @property
    def wallet_date_created(self):
        result = Deposit.query.filter_by(userId=self.id).first()
        if result is not None:
            return result.dateCreated
        return None

    @property
    def hasPhysicalVenues(self):
        for offerer in self.offerers:
            if any([not venue.isVirtual for venue in offerer.managedVenues]):
                return True

        return False

    @property
    def needsToSeeTutorials(self):
        return self.canBookFreeOffers and not self.hasSeenTutorials

    @property
    def hasOffers(self):
        return any([offerer.nOffers > 0 for offerer in self.offerers])


class WalletBalance:
    CSV_HEADER = [
        'ID de l\'utilisateur',
        'Solde théorique',
        'Solde réel'
    ]

    def __init__(self, user_id: int, current_wallet_balance: Decimal, real_wallet_balance: Decimal):
        self.user_id = user_id
        self.current_balance = current_wallet_balance
        self.real_balance = real_wallet_balance

    def as_csv_row(self):
        return [
            self.user_id,
            self.current_balance,
            self.real_balance
        ]
