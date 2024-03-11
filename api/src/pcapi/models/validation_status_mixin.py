import enum

import sqlalchemy as sqla
from sqlalchemy.orm import declarative_mixin
from sqlalchemy.sql.elements import BinaryExpression

from pcapi.utils.typing import hybrid_property


class ValidationStatus(enum.Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    DELETED = "DELETED"


@declarative_mixin
class ValidationStatusMixin:
    validationStatus: ValidationStatus = sqla.Column(
        sqla.Enum(ValidationStatus, create_constraint=False), nullable=False
    )

    @hybrid_property
    def isNew(self) -> bool:
        return self.validationStatus == ValidationStatus.NEW

    @isNew.expression
    def isNew(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.validationStatus == ValidationStatus.NEW

    @hybrid_property
    def isPending(self) -> bool:
        return self.validationStatus == ValidationStatus.PENDING

    @isPending.expression
    def isPending(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.validationStatus == ValidationStatus.PENDING

    @hybrid_property
    def isWaitingForValidation(self) -> bool:
        return self.validationStatus in (ValidationStatus.NEW, ValidationStatus.PENDING)

    @isWaitingForValidation.expression
    def isWaitingForValidation(cls) -> sqla.sql.ColumnElement[sqla.Boolean]:  # pylint: disable=no-self-argument
        return cls.validationStatus.in_([ValidationStatus.NEW, ValidationStatus.PENDING])

    @hybrid_property
    def isValidated(self) -> bool:
        return self.validationStatus == ValidationStatus.VALIDATED

    @isValidated.expression
    def isValidated(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.validationStatus == ValidationStatus.VALIDATED

    @hybrid_property
    def isRejected(self) -> bool:
        return self.validationStatus == ValidationStatus.REJECTED

    @isRejected.expression
    def isRejected(cls) -> bool:  # pylint: disable=no-self-argument
        # sqla.not_(isRejected) works only if we check None separately.
        return cls.validationStatus == ValidationStatus.REJECTED

    @sqla_hybrid.hybrid_property
    def isDeleted(self) -> bool:
        return self.validationStatus == ValidationStatus.DELETED

    @isDeleted.expression  # type: ignore [no-redef]
    def isDeleted(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        # sqla.not_(isDeleted) works only if we check None separately.
        return cls.validationStatus == ValidationStatus.DELETED
