import enum
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr
import sqlalchemy.orm as sa_orm


if TYPE_CHECKING:
    from pcapi.core.users.models import User


class OfferStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    EXPIRED = "EXPIRED"
    REJECTED = "REJECTED"
    SOLD_OUT = "SOLD_OUT"
    INACTIVE = "INACTIVE"
    DRAFT = "DRAFT"


class CollectiveOfferStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    EXPIRED = "EXPIRED"
    REJECTED = "REJECTED"
    SOLD_OUT = "SOLD_OUT"
    INACTIVE = "INACTIVE"
    DRAFT = "DRAFT"
    ARCHIVED = "ARCHIVED"


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


@sa_orm.declarative_mixin
class ValidationMixin:
    lastValidationDate = sa.Column(sa.DateTime, nullable=True)

    lastValidationType = sa.Column(sa.Enum(OfferValidationType, name="validation_type"), nullable=True)

    validation: sa_orm.Mapped[OfferValidationStatus] = sa.Column(
        sa.Enum(OfferValidationStatus, name="validation_status"),
        nullable=False,
        default=OfferValidationStatus.APPROVED,
        server_default="APPROVED",
        index=True,
    )

    @property
    def isApproved(self) -> bool:
        return self.validation == OfferValidationStatus.APPROVED

    @declared_attr
    def lastValidationAuthorUserId(self) -> sa_orm.Mapped[int | None]:
        return sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)

    @declared_attr
    def lastValidationAuthor(self) -> sa_orm.Mapped["User | None"]:
        return sa_orm.relationship("User", foreign_keys=[self.lastValidationAuthorUserId])

    @declared_attr
    def __table_args__(self):
        return (
            sa.Index(
                f"idx_{self.__tablename__}_lastValidationAuthorUserId",
                self.lastValidationAuthorUserId,
                postgresql_where=self.lastValidationAuthorUserId.is_not(None),
            ),
        )
