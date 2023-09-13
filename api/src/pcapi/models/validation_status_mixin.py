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
    validationStatus: ValidationStatus = sqla.Column(
        sqla.Enum(ValidationStatus, create_constraint=False), nullable=False
    )

    @sqla_hybrid.hybrid_property
    def isNew(self) -> bool:
        return self.validationStatus == ValidationStatus.NEW

    @isNew.expression  # type: ignore [no-redef]
    def isNew(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.validationStatus == ValidationStatus.NEW

    @sqla_hybrid.hybrid_property
    def isPending(self) -> bool:
        return self.validationStatus == ValidationStatus.PENDING

    @isPending.expression  # type: ignore [no-redef]
    def isPending(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.validationStatus == ValidationStatus.PENDING

    @sqla_hybrid.hybrid_property
    def isWaitingForValidation(self) -> bool:
        return self.validationStatus in (ValidationStatus.NEW, ValidationStatus.PENDING)

    @isWaitingForValidation.expression  # type: ignore [no-redef]
    def isWaitingForValidation(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.validationStatus.in_([ValidationStatus.NEW, ValidationStatus.PENDING])

    @sqla_hybrid.hybrid_property
    def isValidated(self) -> bool:
        return self.validationStatus == ValidationStatus.VALIDATED

    @isValidated.expression  # type: ignore [no-redef]
    def isValidated(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.validationStatus == ValidationStatus.VALIDATED

    @sqla_hybrid.hybrid_property
    def isRejected(self) -> bool:
        return self.validationStatus == ValidationStatus.REJECTED

    @isRejected.expression  # type: ignore [no-redef]
    def isRejected(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        # sqla.not_(isRejected) works only if we check None separately.
        return cls.validationStatus == ValidationStatus.REJECTED
