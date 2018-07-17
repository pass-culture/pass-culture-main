import secrets

import sqlalchemy as db

from models.needs_validation_mixin import NeedsValidationMixin


class NeedsValidationMixin(object):
    validationToken = db.Column(db.String(27),
                                unique=True,
                                nullable=True)

    def generate_validation_token(self):
        self.validationToken = secrets.token_urlsafe(20)

    @property
    def queryValidated(self):
        return self.query.filter(NeedsValidationMixin.validationToken == None)

    @property
    def isValidated(self):
        return (self.validationToken is None)
