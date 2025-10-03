import enum

import sqlalchemy as sa
import sqlalchemy.ext.hybrid as sa_hybrid
import sqlalchemy.orm as sa_orm
from sqlalchemy.sql.elements import ColumnElement


class ValidationStatus(enum.Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    DELETED = "DELETED"
    CLOSED = "CLOSED"


@sa_orm.declarative_mixin
class ValidationStatusMixin:
    validationStatus: sa_orm.Mapped[ValidationStatus] = sa_orm.mapped_column(
        sa.Enum(ValidationStatus, create_constraint=False), nullable=False
    )

    @sa_hybrid.hybrid_property
    def isNew(self) -> bool:
        return self.validationStatus == ValidationStatus.NEW

    @isNew.inplace.expression
    @classmethod
    def _isNewExpression(cls) -> ColumnElement[bool]:
        return cls.validationStatus == ValidationStatus.NEW

    @sa_hybrid.hybrid_property
    def isPending(self) -> bool:
        return self.validationStatus == ValidationStatus.PENDING

    @isPending.inplace.expression
    @classmethod
    def _isPendingExpression(cls) -> ColumnElement[bool]:
        return cls.validationStatus == ValidationStatus.PENDING

    @sa_hybrid.hybrid_property
    def isWaitingForValidation(self) -> bool:
        return self.validationStatus in (ValidationStatus.NEW, ValidationStatus.PENDING)

    @isWaitingForValidation.inplace.expression
    @classmethod
    def _isWaitingForValidationExpression(cls) -> ColumnElement[bool]:
        return cls.validationStatus.in_([ValidationStatus.NEW, ValidationStatus.PENDING])

    @sa_hybrid.hybrid_property
    def isValidated(self) -> bool:
        return self.validationStatus == ValidationStatus.VALIDATED

    @isValidated.inplace.expression
    @classmethod
    def _isValidatedExpression(cls) -> ColumnElement[bool]:
        return cls.validationStatus == ValidationStatus.VALIDATED

    @sa_hybrid.hybrid_property
    def isRejected(self) -> bool:
        return self.validationStatus == ValidationStatus.REJECTED

    @isRejected.inplace.expression
    @classmethod
    def _isRejectedExpression(cls) -> ColumnElement[bool]:
        # sa.not_(isRejected) works only if we check None separately.
        return cls.validationStatus == ValidationStatus.REJECTED

    @sa_hybrid.hybrid_property
    def isDeleted(self) -> bool:
        return self.validationStatus == ValidationStatus.DELETED

    @isDeleted.inplace.expression
    @classmethod
    def _isDeletedExpression(cls) -> ColumnElement[bool]:
        # sa.not_(isDeleted) works only if we check None separately.
        return cls.validationStatus == ValidationStatus.DELETED

    @sa_hybrid.hybrid_property
    def isClosed(self) -> bool:
        return self.validationStatus == ValidationStatus.CLOSED

    @isClosed.inplace.expression
    @classmethod
    def _isClosedExpression(cls) -> ColumnElement[bool]:
        return cls.validationStatus == ValidationStatus.CLOSED
