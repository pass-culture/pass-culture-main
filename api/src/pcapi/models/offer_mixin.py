import enum
from typing import TYPE_CHECKING

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.ext.declarative import declared_attr


if TYPE_CHECKING:
    from pcapi.core.users.models import User


class OfferStatus(str, enum.Enum):
    # validation statuses
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    # offer lifecycle statuses
    INACTIVE = "INACTIVE"
    SCHEDULED = "SCHEDULED"  # not yet published
    PUBLISHED = "PUBLISHED"  # published but not yet bookable
    ACTIVE = "ACTIVE"  # published & bookable
    # stock lifecycle related statuses
    SOLD_OUT = "SOLD_OUT"  # no more stock available
    EXPIRED = "EXPIRED"  # stocks booking limit datetime has passed


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
    lastValidationDate = sa_orm.mapped_column(sa.DateTime, nullable=True)

    lastValidationType = sa_orm.mapped_column(sa.Enum(OfferValidationType, name="validation_type"), nullable=True)

    validation: sa_orm.Mapped[OfferValidationStatus] = sa_orm.mapped_column(
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
    def lastValidationAuthorUserId(cls) -> sa_orm.Mapped[int | None]:
        return sa_orm.mapped_column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)

    @declared_attr
    def lastValidationAuthor(cls) -> sa_orm.Mapped["User | None"]:
        return sa_orm.relationship("User", foreign_keys=[cls.lastValidationAuthorUserId])  # type: ignore [list-item]

    @declared_attr.directive
    def __table_args__(cls) -> tuple:
        table_name = getattr(cls, "__tablename__", "")  # to help mypy
        return (
            sa.Index(
                f"idx_{table_name}_lastValidationAuthorUserId",
                "lastValidationAuthorUserId",
                postgresql_where='"lastValidationAuthorUserId IS NOT NULL"',
            ),
        )
