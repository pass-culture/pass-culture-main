from flask import current_app as app
import re

from models.api_errors import ApiErrors

db = app.db

# TODO: turn this into a custom type "Adress" ?


class HasAddressMixin(object):
    address = db.Column(db.String(200), nullable=False)

    postalCode = db.Column(db.String(6), nullable=False)

    city = db.Column(db.String(50), nullable=False)

    def errors(self):
        errors = ApiErrors()
        if self.postalCode is not None\
           and not re.match('^\d[AB0-9]\d{3,4}$', self.postalCode):
            errors.addError('postalCode', 'Ce code postal est invalide')
        return errors

HasAddressMixin = HasAddressMixin
