import enum

import sqlalchemy as sa
from sqlalchemy.orm import declarative_mixin


class OfferStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    EXPIRED = "EXPIRED"
    REJECTED = "REJECTED"
    SOLD_OUT = "SOLD_OUT"
    INACTIVE = "INACTIVE"
    DRAFT = "DRAFT"


class OfferValidationStatus(enum.Enum):
    APPROVED = "APPROVED"
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    REJECTED = "REJECTED"


class OfferValidationType(enum.Enum):
    """
    How the last validation status was set:
    automatically by code at API call or manually from backoffice by pass Culture team.
    """

    AUTO = "AUTO"
    MANUAL = "MANUAL"
    CGU_INCOMPATIBLE_PRODUCT = "CGU_INCOMPATIBLE_PRODUCT"


@declarative_mixin
class ValidationMixin:
    lastValidationDate = sa.Column(sa.DateTime, index=True, nullable=True)

    lastValidationType = sa.Column(sa.Enum(OfferValidationType, name="validation_type"), nullable=True)

    validation: OfferValidationStatus = sa.Column(
        sa.Enum(OfferValidationStatus, name="validation_status"),
        nullable=False,
        default=OfferValidationStatus.APPROVED,
        server_default="APPROVED",
        index=True,
    )

    @property
    def isApproved(self) -> bool:
        return self.validation == OfferValidationStatus.APPROVED
