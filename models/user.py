from datetime import datetime
from decimal import Decimal
import bcrypt
from sqlalchemy import Binary, \
    Boolean, \
    CheckConstraint, \
    Column, \
    func, \
    DateTime, \
    String, \
    BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from models.versioned_mixin import VersionedMixin
from models.db import Model, db
from models.needs_validation_mixin import NeedsValidationMixin
from models.pc_object import PcObject
from models.user_offerer import UserOfferer, RightsType


class User(PcObject,
           Model,
           NeedsValidationMixin,
           VersionedMixin
           ):
    email = Column(String(120), nullable=False, unique=True)

    canBookFreeOffers = Column(Boolean,
                               nullable=False,
                               server_default=expression.true(),
                               default=True)

    clearTextPassword = None

    culturalSurveyId = Column(UUID(as_uuid=True), nullable=True)

    dateCreated = Column(DateTime,
                         nullable=False,
                         default=datetime.utcnow)

    dateOfBirth = Column(DateTime,
                         nullable=True)

    demarcheSimplifieeApplicationId = Column(BigInteger, nullable=True)

    departementCode = Column(String(3), nullable=False)

    firstName = Column(String(35), nullable=True)

    isAdmin = Column(Boolean,
                     CheckConstraint('("canBookFreeOffers" IS FALSE AND "isAdmin" IS TRUE)'
                                     + 'OR ("isAdmin" IS FALSE)',
                                     name='check_admin_cannot_book_free_offers'),
                     nullable=False,
                     server_default=expression.false(),
                     default=False)

    lastName = Column(String(35), nullable=True)

    needsToFillCulturalSurvey = Column(Boolean, default=True)

    offerers = relationship('Offerer',
                            secondary='user_offerer')

    password = Column(Binary(60), nullable=False)

    phoneNumber = Column(String(20), nullable=True)

    postalCode = Column(String(5), nullable=True)

    publicName = Column(String(30), nullable=False)

    resetPasswordToken = Column(String(10), unique=True)

    resetPasswordTokenValidityLimit = Column(DateTime)

    def checkPassword(self, passwordToCheck):
        return bcrypt.hashpw(passwordToCheck.encode('utf-8'), self.password) == self.password

    def errors(self):
        api_errors = super(User, self).errors()

        user_count = 0
        try:
            user_count = User.query.filter_by(email=self.email).count()
        except IntegrityError as ie:
            if self.id is None:
                api_errors.addError('email', 'Un compte lié à cet email existe déjà')

        if self.id is None and user_count > 0:
            api_errors.addError('email', 'Un compte lié à cet email existe déjà')
        if self.publicName:
            api_errors.checkMinLength('publicName', self.publicName, 3)
        if self.email:
            api_errors.checkEmail('email', self.email)

        if self.isAdmin and self.canBookFreeOffers:
            api_errors.addError('canBookFreeOffers', 'Admin ne peut pas booker')
        if self.clearTextPassword:
            api_errors.checkMinLength('password', self.clearTextPassword, 8)

        return api_errors

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
        super(User, self).populate_from_dict(data)
        if data.__contains__('password') and data['password']:
            self.setPassword(data['password'])

    def setPassword(self, newpass):
        self.clearTextPassword = newpass
        self.password = bcrypt.hashpw(newpass.encode('utf-8'), bcrypt.gensalt())
        self.resetPasswordToken = None
        self.resetPasswordTokenValidityLimit = None

    @property
    def real_wallet_balance(self):
        return db.session.query(func.get_wallet_balance(self.id, True)).scalar()

    @property
    def wallet_balance(self):
        return db.session.query(func.get_wallet_balance(self.id, False)).scalar()

    @property
    def wallet_is_activated(self):
        return len(self.deposits) > 0


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
