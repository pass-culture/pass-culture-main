import enum

import sqlalchemy as sa
import sqlalchemy.ext.hybrid as sa_hybrid
import sqlalchemy.orm as sa_orm
from sqlalchemy.orm import declarative_mixin
from sqlalchemy.sql.elements import BinaryExpression


class ValidationStatus(enum.Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    DELETED = "DELETED"
    CLOSED = "CLOSED"


@declarative_mixin
class ValidationStatusMixin:
    validationStatus: sa_orm.Mapped[ValidationStatus] = sa.Column(
        sa.Enum(ValidationStatus, create_constraint=False), nullable=False
    )

    @sa_hybrid.hybrid_property
    def isNew(self) -> bool:
        return self.validationStatus == ValidationStatus.NEW

    @isNew.expression  # type: ignore[no-redef]
    def isNew(cls) -> BinaryExpression:
        return cls.validationStatus == ValidationStatus.NEW

    @sa_hybrid.hybrid_property
    def isPending(self) -> bool:
        return self.validationStatus == ValidationStatus.PENDING

    @isPending.expression  # type: ignore[no-redef]
    def isPending(cls) -> BinaryExpression:
        return cls.validationStatus == ValidationStatus.PENDING

    @sa_hybrid.hybrid_property
    def isWaitingForValidation(self) -> bool:
        return self.validationStatus in (ValidationStatus.NEW, ValidationStatus.PENDING)

    @isWaitingForValidation.expression  # type: ignore[no-redef]
    def isWaitingForValidation(cls) -> BinaryExpression:
        return cls.validationStatus.in_([ValidationStatus.NEW, ValidationStatus.PENDING])

    @sa_hybrid.hybrid_property
    def isValidated(self) -> bool:
        return self.validationStatus == ValidationStatus.VALIDATED

    @isValidated.expression  # type: ignore[no-redef]
    def isValidated(cls) -> BinaryExpression:
        return cls.validationStatus == ValidationStatus.VALIDATED

    @sa_hybrid.hybrid_property
    def isRejected(self) -> bool:
        return self.validationStatus == ValidationStatus.REJECTED

    @isRejected.expression  # type: ignore[no-redef]
    def isRejected(cls) -> BinaryExpression:
        # sa.not_(isRejected) works only if we check None separately.
        return cls.validationStatus == ValidationStatus.REJECTED

    @sa_hybrid.hybrid_property
    def isDeleted(self) -> bool:
        return self.validationStatus == ValidationStatus.DELETED

    @isDeleted.expression  # type: ignore[no-redef]
    def isDeleted(cls) -> BinaryExpression:
        # sa.not_(isDeleted) works only if we check None separately.
        return cls.validationStatus == ValidationStatus.DELETED

    @sa_hybrid.hybrid_property
    def isClosed(self) -> bool:
        return self.validationStatus == ValidationStatus.CLOSED

    @isClosed.expression  # type: ignore[no-redef]
    def isClosed(cls) -> BinaryExpression:
        return cls.validationStatus == ValidationStatus.CLOSED
