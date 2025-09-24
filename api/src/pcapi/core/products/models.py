import datetime
import enum
import logging
import typing
from dataclasses import dataclass

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext import mutable as sa_mutable
from sqlalchemy.ext.hybrid import hybrid_property

from pcapi import settings
from pcapi.core.categories import subcategories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers.models import Provider
from pcapi.models import Model
from pcapi.models.has_thumb_mixin import HasThumbMixin
from pcapi.models.pc_object import PcObject
from pcapi.utils import db as db_utils


if typing.TYPE_CHECKING:
    from pcapi.core.reactions.models import Reaction

logger = logging.getLogger(__name__)

UNRELEASED_OR_UNAVAILABLE_BOOK_MARKER = "xxx"


class ProductMediation(PcObject, Model):
    __tablename__ = "product_mediation"

    dateModifiedAtLastProvider = sa_orm.mapped_column(sa.DateTime, nullable=True, default=datetime.datetime.utcnow)
    imageType: sa_orm.Mapped[offers_models.ImageType] = sa_orm.mapped_column(
        db_utils.MagicEnum(offers_models.ImageType, use_values=False), nullable=False
    )
    lastProviderId = sa_orm.mapped_column(sa.BigInteger, sa.ForeignKey("provider.id"), nullable=True)
    lastProvider: sa_orm.Mapped["Provider|None"] = sa_orm.relationship("Provider", foreign_keys=[lastProviderId])
    productId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("product.id", ondelete="CASCADE"), index=True, nullable=False
    )
    uuid: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False, unique=True)

    @property
    def url(self) -> str:
        return f"{settings.OBJECT_STORAGE_URL}/{settings.THUMBS_FOLDER_NAME}/{self.uuid}"


@dataclass
class Movie:
    allocine_id: str | None
    description: str | None
    duration: int | None
    poster_url: str | None
    visa: str | None
    title: str
    extra_data: offers_models.OfferExtraData | None


class GcuCompatibilityType(enum.Enum):
    COMPATIBLE = "COMPATIBLE"
    PROVIDER_INCOMPATIBLE = "PROVIDER_INCOMPATIBLE"
    FRAUD_INCOMPATIBLE = "FRAUD_INCOMPATIBLE"


class ProductIdentifierType(enum.Enum):
    ALLOCINE_ID = "ALLOCINE_ID"
    EAN = "EAN"
    VISA = "VISA"


class Product(PcObject, Model, HasThumbMixin):
    __tablename__ = "product"

    dateModifiedAtLastProvider = sa_orm.mapped_column(sa.DateTime, nullable=True, default=datetime.datetime.utcnow)
    description: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    durationMinutes = sa_orm.mapped_column(sa.Integer, nullable=True)
    extraData: sa_orm.Mapped[offers_models.OfferExtraData | None] = sa_orm.mapped_column(
        "jsonData", sa_mutable.MutableDict.as_mutable(postgresql.JSONB)
    )
    gcuCompatibilityType = sa_orm.mapped_column(
        db_utils.MagicEnum(GcuCompatibilityType),
        nullable=False,
        default=GcuCompatibilityType.COMPATIBLE,
        server_default=GcuCompatibilityType.COMPATIBLE.value,
    )
    last_30_days_booking = sa_orm.mapped_column(sa.Integer, nullable=True)
    lastProviderId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("provider.id"), nullable=True
    )
    lastProvider: sa_orm.Mapped["Provider|None"] = sa_orm.relationship("Provider", foreign_keys=[lastProviderId])
    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(140), nullable=False)
    subcategoryId: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False, index=True)
    thumb_path_component = "products"
    reactions: sa_orm.Mapped[list["Reaction"]] = sa_orm.relationship("Reaction", back_populates="product", uselist=True)
    productMediations: sa_orm.Mapped[list[ProductMediation]] = sa_orm.relationship(
        "ProductMediation",
        backref="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    ean = sa_orm.mapped_column(
        sa.Text, sa.CheckConstraint("ean ~ '^\\d{13}$'", name="check_ean_validity"), nullable=True
    )

    chroniclesCount: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger,
        sa.CheckConstraint('"chroniclesCount" >= 0', name="check_chronicles_count_is_positive"),
        nullable=False,
        server_default=sa.text("0"),
    )
    headlinesCount: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger,
        sa.CheckConstraint('"headlinesCount" >= 0', name="check_headlines_count_is_positive"),
        nullable=False,
        server_default=sa.text("0"),
    )
    likesCount: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger,
        sa.CheckConstraint('"likesCount" >= 0', name="check_likes_count_is_positive"),
        nullable=False,
        server_default=sa.text("0"),
    )

    __table_args__ = (
        sa.Index("product_allocineId_idx", extraData["allocineId"].cast(sa.Text), unique=True),
        sa.Index(
            "ix_product_visa",
            extraData["visa"].astext,
            postgresql_where=sa.text("""(("jsonData" ->> 'visa'::text) IS NOT NULL)"""),
            unique=True,
        ),
        sa.Index("unique_ix_product_ean", ean, unique=True),
        sa.Index("idx_product_trgm_name", name, postgresql_using="gin"),
    )

    @property
    def subcategory(self) -> subcategories.Subcategory:
        if self.subcategoryId not in subcategories.ALL_SUBCATEGORIES_DICT:
            raise ValueError(f"Unexpected subcategoryId '{self.subcategoryId}' for product {self.id}")
        return subcategories.ALL_SUBCATEGORIES_DICT[self.subcategoryId]

    @property
    def isGcuCompatible(self) -> bool:
        return self.gcuCompatibilityType == GcuCompatibilityType.COMPATIBLE

    @hybrid_property
    def can_be_synchronized(self) -> bool:
        return (self.gcuCompatibilityType == GcuCompatibilityType.COMPATIBLE) & (
            self.name != UNRELEASED_OR_UNAVAILABLE_BOOK_MARKER
        )

    @hybrid_property
    def images(self) -> dict[str, str | None]:
        if self.productMediations:
            return {
                pm.imageType.value: pm.url for pm in self.productMediations if pm.imageType in offers_models.ImageType
            }
        return {offers_models.ImageType.RECTO.value: self.thumbUrl}

    @property
    def identifierType(self) -> ProductIdentifierType:
        # We first check if the product has an EAN.
        # Then, we check for allocineId before visa because a product can have both,
        # but allocineId is much more common and generally more reliable than visa.
        # Therefore, we prioritize allocineId over visa for identifying the product.
        if self.ean:
            return ProductIdentifierType.EAN
        elif self.extraData and self.extraData.get("allocineId"):
            return ProductIdentifierType.ALLOCINE_ID
        elif self.extraData and self.extraData.get("visa"):
            return ProductIdentifierType.VISA
        else:
            raise ValueError()
