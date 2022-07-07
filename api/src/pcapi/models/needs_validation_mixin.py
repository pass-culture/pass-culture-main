import secrets

import sqlalchemy as sqla
import sqlalchemy.ext.hybrid as sqla_hybrid
from sqlalchemy.orm import declarative_mixin


@declarative_mixin
class NeedsValidationMixin:
    validationToken = sqla.Column(sqla.String(27), unique=True, nullable=True)

    def generate_validation_token(self):  # type: ignore [no-untyped-def]
        self.validationToken = secrets.token_urlsafe(20)

    @sqla_hybrid.hybrid_property
    def isValidated(self):
        return self.validationToken is None

    @isValidated.expression  # type: ignore [no-redef]
    def isValidated(cls):  # pylint: disable=no-self-argument # type: ignore[no-redef]
        return cls.validationToken.is_(None)
