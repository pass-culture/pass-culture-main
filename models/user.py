"""User model"""
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship
from sqlalchemy import Binary, Boolean, Column, DateTime, String, func, CheckConstraint
import bcrypt

from models import Deposit, Booking
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

    isAdmin = Column(Boolean,
                     CheckConstraint('("canBookFreeOffers" IS FALSE AND "isAdmin" IS TRUE)'
                                     + 'OR ("isAdmin" IS FALSE)',
                                     name='check_admin_cannot_book_free_offers'),
                     nullable=False,
                     server_default=expression.false(),
                     default=False)

    def checkPassword(self, passwordToCheck):
        return bcrypt.hashpw(passwordToCheck.encode('utf-8'), self.password) == self.password

    def errors(self):
        api_errors = PcObject.errors(self)

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
#        if self.firstname:
#            api_errors.checkMinLength('firstname', self.firstname, 2)
#        if self.lastname:
#            api_errors.checkMinLength('lastname', self.lastname, 2)
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

    def hasRights(self, rights, offererId):
        if self.isAdmin:
            return True
        if rights == RightsType.editor:
            compatible_rights = [RightsType.editor, RightsType.admin]
        else:
            compatible_rights = [rights]
        return UserOfferer.query\
                  .filter((UserOfferer.offererId == offererId) &
                          (UserOfferer.rights.in_(compatible_rights)))\
                  .first() is not None

    @property
    def wallet_balance(self):
        return db.session.query(func.get_wallet_balance(self.id)).scalar()
