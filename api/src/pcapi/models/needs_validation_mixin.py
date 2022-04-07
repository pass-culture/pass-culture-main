""" needs validation mixin """
import secrets

from sqlalchemy import Column
from sqlalchemy import String


class NeedsValidationMixin:
    validationToken = Column(String(27), unique=True, nullable=True)

    def generate_validation_token(self):  # type: ignore [no-untyped-def]
        self.validationToken = secrets.token_urlsafe(20)

    @property
    def isValidated(self):  # type: ignore [no-untyped-def]
        return self.validationToken is None
