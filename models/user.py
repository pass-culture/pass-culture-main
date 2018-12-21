"""User model"""
from datetime import datetime
from decimal import Decimal

import bcrypt
from sqlalchemy import Binary, Boolean, Column, DateTime, String, func, CheckConstraint
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from models.db import Model, db
from models.has_thumb_mixin import HasThumbMixin
from models.needs_validation_mixin import NeedsValidationMixin
from models.pc_object import PcObject
from models.user_offerer import UserOfferer, RightsType


class User(PcObject,
           Model,
           HasThumbMixin,
           NeedsValidationMixin
           ):
    email = Column(String(120), nullable=False, unique=True)
    password = Column(Binary(60), nullable=False)

    publicName = Column(String(30), nullable=False)

    offerers = relationship('Offerer',
                            secondary='user_offerer')

    dateCreated = Column(DateTime,
                         nullable=False,
                         default=datetime.utcnow)

    clearTextPassword = None

    departementCode = Column(String(3), nullable=False)

    canBookFreeOffers = Column(Boolean,
                               nullable=False,
                               server_default=expression.true(),
                               default=True)

    dateOfBirth = Column(DateTime,
                         nullable=True)

    isAdmin = Column(Boolean,
                     CheckConstraint('("canBookFreeOffers" IS FALSE AND "isAdmin" IS TRUE)'
                                     + 'OR ("isAdmin" IS FALSE)',
                                     name='check_admin_cannot_book_free_offers'),
                     nullable=False,
                     server_default=expression.false(),
                     default=False)

    resetPasswordToken = Column(String(10), unique=True)

    resetPasswordTokenValidityLimit = Column(DateTime)

    firstName = Column(String(35), nullable=True)

    lastName = Column(String(35), nullable=True)

    postalCode = Column(String(5), nullable=True)

    phoneNumber = Column(String(20), nullable=True)

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

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def populateFromDict(self, dct):
        super(User, self).populateFromDict(dct)
        if dct.__contains__('password') and dct['password']:
            self.setPassword(dct['password'])

    def setPassword(self, newpass):
        self.clearTextPassword = newpass
        self.password = bcrypt.hashpw(newpass.encode('utf-8'),
                                      bcrypt.gensalt())
        self.resetPasswordToken = None
        self.resetPasswordTokenValidityLimit = None

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

    @property
    def wallet_balance(self):
        return db.session.query(func.get_wallet_balance(self.id, False)).scalar()

    @property
    def real_wallet_balance(self):
        return db.session.query(func.get_wallet_balance(self.id, True)).scalar()

    @property
    def wallet_is_activated(self):
        return len(self.deposits) > 0


class WalletBalances:
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
