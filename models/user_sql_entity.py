from datetime import datetime
from decimal import Decimal

import bcrypt
from sqlalchemy import Binary, \
    Boolean, \
    CheckConstraint, \
    Column, \
    func, \
    DateTime, \
    String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from domain.expenses import get_expenses
from models.db import Model, db
from models.deposit import Deposit
from models.needs_validation_mixin import NeedsValidationMixin
from models.pc_object import PcObject
from models.user_offerer import UserOfferer, RightsType
from models.versioned_mixin import VersionedMixin


class UserSQLEntity(PcObject,
                    Model,
                    NeedsValidationMixin,
                    VersionedMixin
                    ):
    __tablename__ = 'user'

    email = Column(String(120), nullable=False, unique=True)

    address = Column(String(200), nullable=True)

    canBookFreeOffers = Column(Boolean,
                               nullable=False,
                               server_default=expression.true(),
                               default=True)

    city = Column(String(50), nullable=True)

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

    needsToFillCulturalSurvey = Column(Boolean,
                                       server_default=expression.true(),
                                       default=True)

    offerers = relationship('Offerer',
                            secondary='user_offerer')

    password = Column(Binary(60), nullable=False)

    phoneNumber = Column(String(20), nullable=True)

    postalCode = Column(String(5), nullable=True)

    publicName = Column(String(255), nullable=False)

    resetPasswordToken = Column(String(10), unique=True)

    resetPasswordTokenValidityLimit = Column(DateTime)

    civility = Column(String(20), nullable=True)

    activity = Column(String(128), nullable=True)

    hasSeenTutorials = Column(Boolean, nullable=True)

    def checkPassword(self, passwordToCheck):
        return bcrypt.hashpw(passwordToCheck.encode('utf-8'), self.password) == self.password

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
        self.password = bcrypt.hashpw(newpass.encode('utf-8'), bcrypt.gensalt())
        self.resetPasswordToken = None
        self.resetPasswordTokenValidityLimit = None

    @property
    def expenses(self):
        return get_expenses(self.userBookings)

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
        return self.canBookFreeOffers and self.hasSeenTutorials is False

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
