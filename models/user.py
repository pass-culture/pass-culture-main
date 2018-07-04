"""User model"""
import bcrypt
from datetime import datetime
from flask import current_app as app
from sqlalchemy.sql import expression
import secrets
db = app.db


class User(app.model.PcObject,
           db.Model,
           app.model.HasThumbMixin,
           app.model.NeedsValidationMixin
           ):
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.Binary(60), nullable=False)

    publicName = db.Column(db.String(30), nullable=False)

    offerers = db.relationship(lambda: app.model.Offerer,
                               secondary='user_offerer')

    dateCreated = db.Column(db.DateTime,
                            nullable=False,
                            default=datetime.utcnow)

    clearTextPassword = None

    departementCode = db.Column(db.String(3), nullable=False)

    canBook =  db.Column(db.Boolean,
                         nullable=False,
                         server_default=expression.true(),
                         default=True)

    isAdmin =  db.Column(db.Boolean,
                         nullable=False,
                         server_default=expression.false(),
                         default=False)

    def checkPassword(self, passwordToCheck):
        return bcrypt.hashpw(passwordToCheck.encode('utf-8'), self.password) == self.password

    def errors(self):
        errors = super(User, self).errors()
        if self.id is None\
           and User.query.filter_by(email=self.email).count()>0:
            errors.addError('email', 'Un compte lié à cet email existe déjà')
        if self.publicName:
            errors.checkMinLength('publicName', self.publicName, 3)
        if self.email:
            errors.checkEmail('email', self.email)
#        if self.firstname:
#            errors.checkMinLength('firstname', self.firstname, 2)
#        if self.lastname:
#            errors.checkMinLength('lastname', self.lastname, 2)
        if self.clearTextPassword:
            errors.checkMinLength('password', self.clearTextPassword, 8)
        return errors

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
        RightsType = app.model.RightsType
        if rights == RightsType.editor:
            compatible_rights = [RightsType.editor, RightsType.admin]
        else:
            compatible_rights = [rights]
        return app.model.UserOfferer.query\
                  .filter((app.model.UserOfferer.offererId == offererId) &
                          (app.model.UserOfferer.rights.in_(compatible_rights)))\
                  .first() is not None


app.model.User = User
