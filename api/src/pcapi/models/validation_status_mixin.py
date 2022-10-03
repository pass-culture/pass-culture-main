import enum

import sqlalchemy as sqla
import sqlalchemy.ext.hybrid as sqla_hybrid
from sqlalchemy.orm import declarative_mixin
from sqlalchemy.sql.elements import BinaryExpression


class ValidationStatus(enum.Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"


@declarative_mixin
class ValidationStatusMixin:
    validationStatus = sqla.Column(sqla.Enum(ValidationStatus, create_constraint=False), nullable=True)

    @sqla_hybrid.hybrid_property
    def isValidated(self) -> bool:
        return self.validationStatus == ValidationStatus.VALIDATED

    @isValidated.expression  # type: ignore [no-redef]
    def isValidated(cls) -> BinaryExpression:  # pylint: disable=no-self-argument # type: ignore[no-redef]
        return cls.validationStatus == ValidationStatus.VALIDATED
