""" needs validation mixin """
import secrets

from sqlalchemy import Column, String


class NeedsValidationMixin(object):
    validationToken = Column(String(27),
                             unique=True,
                             nullable=True)

    def generate_validation_token(self):
        self.validationToken = secrets.token_urlsafe(20)

    @property
    def queryValidated(self):
        return self.query.filter(NeedsValidationMixin.validationToken == None)

    @property
    def isValidated(self):
        return self.validationToken is None
