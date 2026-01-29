import datetime
import decimal
import enum
import logging
import typing
from dataclasses import dataclass

import psycopg2.extras
import sqlalchemy as sa
import sqlalchemy.event as sa_event
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext import mutable as sa_mutable
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.elements import Case
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.elements import UnaryExpression

import pcapi.core.bookings.constants as bookings_constants
from pcapi import settings
from pcapi.core.categories import models
from pcapi.core.categories import pro_categories
from pcapi.core.categories import subcategories
from pcapi.core.criteria.models import OfferCriterion
from pcapi.core.educational.models import ValidationRuleCollectiveOfferLink
from pcapi.core.educational.models import ValidationRuleCollectiveOfferTemplateLink
from pcapi.core.finance.models import CustomReimbursementRule
from pcapi.core.geography import models as geography_models
from pcapi.core.highlights.models import HighlightRequest
from pcapi.core.history.constants import ACTION_HISTORY_ORDER_BY
from pcapi.core.providers.models import Provider
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.accessibility_mixin import AccessibilityMixin
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.has_thumb_mixin import HasThumbMixin
from pcapi.models.offer_mixin import OfferStatus
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import ValidationMixin
from pcapi.models.pc_object import PcObject
from pcapi.models.soft_deletable_mixin import SoftDeletableMixin
from pcapi.utils import date as date_utils
from pcapi.utils import db as db_utils


logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    import flask_sqlalchemy

    from pcapi.core.artist.models import Artist
    from pcapi.core.artist.models import ArtistOfferLink
    from pcapi.core.bookings.models import Booking
    from pcapi.core.chronicles.models import Chronicle
    from pcapi.core.criteria.models import Criterion
    from pcapi.core.educational.models import CollectiveOffer
    from pcapi.core.educational.models import CollectiveOfferTemplate
    from pcapi.core.history.models import ActionHistory
    from pcapi.core.offerers import models as offerers_models
    from pcapi.core.offerers.models import OffererAddress
    from pcapi.core.offerers.models import Venue
    from pcapi.core.reactions.models import Reaction
    from pcapi.core.reminders.models import OfferReminder
    from pcapi.core.users.models import Favorite
    from pcapi.core.users.models import User


UNRELEASED_OR_UNAVAILABLE_BOOK_MARKER = "xxx"


class OfferExtraData(typing.TypedDict, total=False):
    artist: str | None
    author: str | None
    ean: str | None
    musicSubType: str | None
    musicType: str | None
    performer: str | None
    showSubType: str | None
    showType: str | None
    speaker: str | None
    stageDirector: str | None
    visa: str | None

    # allocine
    allocineId: int | None
    backlink: str | None
    cast: list[str] | None
    companies: list[dict] | None
    countries: list[str] | None
    credits: list[dict] | None
    diffusionVersion: str | None
    eidr: str | None
    genres: list[str] | None
    originalTitle: str | None
    posterUrl: str | None
    productionYear: int | None
    releaseDate: str | None
    certificate: str | None
    releases: list[dict] | None
    runtime: int | None
    synopsis: str | None
    theater: dict | None
    title: str | None
    type: str | None

    # titelive prior gtl (csr)
    bookFormat: str | None
    collection: str | None
    comic_series: str | None
    comment: str | None
    contenu_explicite: str | None
    date_parution: str | None
    dewey: str | None
    dispo: int | None
    dispo_label: str | None
    distributeur: str | None
    editeur: str | None
    music_label: str | None
    nb_galettes: str | None
    num_in_collection: str | None
    prix_livre: str | None
    prix_musique: str | None
    rayon: str | None  # this is csr_label, it should be stored as csr_id as titelive can update them
    top: str | None
    schoolbook: bool | None
    titelive_regroup: str | None

    # titelive after gtl
    csr_id: str | None
    gtl_id: str | None
    code_clil: str | None
    nb_pages: str | None
    langue: str | None
    langueiso: str | None


class ImageType(enum.Enum):
    POSTER = "poster"
    RECTO = "recto"
    VERSO = "verso"


class ProductMediation(PcObject, Model):
    __tablename__ = "product_mediation"

    dateModifiedAtLastProvider: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(
        sa.DateTime, nullable=True, default=date_utils.get_naive_utc_now
    )
    imageType: sa_orm.Mapped[ImageType] = sa_orm.mapped_column(
        db_utils.MagicEnum(ImageType, use_values=False), nullable=False
    )
    lastProviderId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("provider.id"), nullable=True
    )
    lastProvider: sa_orm.Mapped["Provider | None"] = sa_orm.relationship("Provider", foreign_keys=[lastProviderId])
    productId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("product.id", ondelete="CASCADE"), index=True, nullable=False
    )
    product: sa_orm.Mapped["Product"] = sa_orm.relationship(
        "Product",
        foreign_keys=[productId],
        back_populates="productMediations",
    )
    uuid: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False, unique=True)

    @property
    def url(self) -> str:
        return f"{settings.OBJECT_STORAGE_URL}/{settings.THUMBS_FOLDER_NAME}/{self.uuid}"


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
    thumb_path_component = "products"

    dateModifiedAtLastProvider: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(
        sa.DateTime, nullable=True, default=date_utils.get_naive_utc_now
    )
    description: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    durationMinutes: sa_orm.Mapped[int | None] = sa_orm.mapped_column(sa.Integer, nullable=True)
    extraData: sa_orm.Mapped[OfferExtraData | None] = sa_orm.mapped_column(
        "jsonData", sa_mutable.MutableDict.as_mutable(postgresql.JSONB), nullable=True
    )
    gcuCompatibilityType: sa_orm.Mapped[GcuCompatibilityType] = sa_orm.mapped_column(
        db_utils.MagicEnum(GcuCompatibilityType),
        nullable=False,
        default=GcuCompatibilityType.COMPATIBLE,
        server_default=GcuCompatibilityType.COMPATIBLE.value,
    )
    last_30_days_booking: sa_orm.Mapped[int | None] = sa_orm.mapped_column(sa.Integer, nullable=True)
    lastProviderId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("provider.id"), nullable=True
    )
    lastProvider: sa_orm.Mapped["Provider | None"] = sa_orm.relationship("Provider", foreign_keys=[lastProviderId])
    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(140), nullable=False)
    subcategoryId: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False, index=True)
    reactions: sa_orm.Mapped[list["Reaction"]] = sa_orm.relationship(
        "Reaction", foreign_keys="Reaction.productId", back_populates="product", uselist=True
    )
    chronicles: sa_orm.Mapped[list["Chronicle"]] = sa_orm.relationship(
        "Chronicle", back_populates="products", secondary="product_chronicle"
    )
    productMediations: sa_orm.Mapped[list[ProductMediation]] = sa_orm.relationship(
        "ProductMediation",
        back_populates="product",
        cascade="all, delete-orphan",
        foreign_keys="ProductMediation.productId",
        passive_deletes=True,
    )
    ean: sa_orm.Mapped[str | None] = sa_orm.mapped_column(
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

    artists: sa_orm.Mapped[list["Artist"]] = sa_orm.relationship(
        "Artist", back_populates="products", secondary="artist_product_link"
    )
    offers: sa_orm.Mapped[list["Offer"]] = sa_orm.relationship(
        "Offer", back_populates="product", order_by="Offer.id", foreign_keys="Offer.productId"
    )

    __table_args__ = (
        sa.Index(
            "product_allocineId_idx",
            sa.literal_column("(\"jsonData\" -> 'allocineId'::text)"),
            postgresql_where=sa.text("""(("jsonData" ->> 'allocineId'::text) IS NOT NULL)"""),
            unique=True,
        ),
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
            return {pm.imageType.value: pm.url for pm in self.productMediations if pm.imageType in ImageType}
        return {ImageType.RECTO.value: self.thumbUrl}

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


class Mediation(PcObject, Model, HasThumbMixin, DeactivableMixin):
    __tablename__ = "mediation"
    thumb_path_component = "mediations"

    authorId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    author: sa_orm.Mapped["User | None"] = sa_orm.relationship(
        "User", foreign_keys=[authorId], back_populates="mediations"
    )
    credit: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String(255), nullable=True)
    dateCreated: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now
    )
    dateModifiedAtLastProvider: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(
        sa.DateTime, nullable=True, default=date_utils.get_naive_utc_now
    )
    lastProviderId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("provider.id"), nullable=True
    )
    lastProvider: sa_orm.Mapped["Provider | None"] = sa_orm.relationship("Provider", foreign_keys=[lastProviderId])
    offerId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer.id"), index=True, nullable=False
    )
    offer: sa_orm.Mapped["Offer"] = sa_orm.relationship("Offer", foreign_keys=[offerId], back_populates="mediations")


class Stock(PcObject, Model, SoftDeletableMixin):
    __tablename__ = "stock"

    MAX_STOCK_QUANTITY = 1_000_000
    AUTOMATICALLY_USED_SUBCATEGORIES = [
        subcategories.CARTE_MUSEE.id,
        subcategories.ABO_BIBLIOTHEQUE.id,
        subcategories.ABO_MEDIATHEQUE.id,
    ]

    activationCodes: sa_orm.Mapped[list["ActivationCode"]] = sa_orm.relationship(
        "ActivationCode", foreign_keys="ActivationCode.stockId", back_populates="stock"
    )
    beginningDatetime: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)
    bookingLimitDatetime = sa_orm.mapped_column(sa.DateTime, nullable=True)
    dateCreated: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now, server_default=sa.func.now()
    )
    dateModified: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now
    )
    dnBookedQuantity: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, nullable=False, server_default=sa.text("0")
    )
    offerId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer.id"), index=True, nullable=False
    )
    offer: sa_orm.Mapped["Offer"] = sa_orm.relationship("Offer", foreign_keys=[offerId], back_populates="stocks")
    price: sa_orm.Mapped[decimal.Decimal] = sa_orm.mapped_column(
        sa.Numeric(10, 2),
        sa.CheckConstraint("price >= 0", name="check_price_is_not_negative"),
        index=True,
        nullable=False,
    )
    priceCategoryId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("price_category.id"), index=True, nullable=True
    )
    priceCategory: sa_orm.Mapped["PriceCategory | None"] = sa_orm.relationship(
        "PriceCategory", foreign_keys=[priceCategoryId], back_populates="stocks"
    )
    quantity: sa_orm.Mapped[int | None] = sa_orm.mapped_column(sa.Integer, nullable=True)
    features: sa_orm.Mapped[list[str]] = sa_orm.mapped_column(
        postgresql.ARRAY(sa.Text), nullable=False, server_default=sa.text("'{}'::text[]")
    )

    lastProviderId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("provider.id"), nullable=True
    )
    lastProvider: sa_orm.Mapped["Provider | None"] = sa_orm.relationship("Provider", foreign_keys=[lastProviderId])

    idAtProviders: sa_orm.Mapped[str | None] = sa_orm.mapped_column(
        sa.String(70),
        sa.CheckConstraint(
            '"lastProviderId" IS NULL OR "idAtProviders" IS NOT NULL',
            name="check_providable_with_provider_has_idatproviders",
        ),
        nullable=True,
    )

    dateModifiedAtLastProvider: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(
        sa.DateTime, nullable=True, default=date_utils.get_naive_utc_now
    )

    fieldsUpdated: sa_orm.Mapped[list[str]] = sa_orm.mapped_column(
        postgresql.ARRAY(sa.String(100)), nullable=False, default=[], server_default="{}"
    )

    bookings: sa_orm.Mapped[list["Booking"]] = sa_orm.relationship(
        "Booking", foreign_keys="Booking.stockId", back_populates="stock"
    )

    __table_args__ = (
        sa.Index(
            "ix_stock_beginningDatetime_partial", beginningDatetime, postgresql_where=beginningDatetime.is_not(None)
        ),
        sa.Index(
            "ix_stock_bookingLimitDatetime_partial",
            bookingLimitDatetime,
            postgresql_where=bookingLimitDatetime.is_not(None),
        ),
        # First step : Create a unique index on offerId/idAtProviders
        # Next step : Create a unicity constraint based on this index and to drop the unicity constraint on idAtProviders
        sa.Index("unique_ix_offer_id_id_at_providers", offerId, idAtProviders, unique=True),
        sa.Index("ix_stock_idAtProviders", idAtProviders),
        sa.Index(
            "ix_stock_bookability",
            "offerId",
            "beginningDatetime",
            "isSoftDeleted",
            "bookingLimitDatetime",
            "quantity",
            "dnBookedQuantity",
        ),
    )

    @property
    def isBookable(self) -> bool:
        return self._bookable and self.offer.isReleased

    @hybrid_property
    def _bookable(self) -> bool:
        return not self.isExpired and not self.isSoldOut

    @_bookable.inplace.expression
    @classmethod
    def _bookableExpression(cls) -> ColumnElement[bool]:
        return sa.and_(sa.not_(cls.isExpired), sa.not_(cls.isSoldOut))

    @property
    def is_forbidden_to_underage(self) -> bool:
        return (self.price > 0 and not self.offer.subcategory.is_bookable_by_underage_when_not_free) or (
            self.price == 0 and not self.offer.subcategory.is_bookable_by_underage_when_free
        )

    @hybrid_property
    def hasBookingLimitDatetimePassed(self) -> bool:
        return bool(self.bookingLimitDatetime and self.bookingLimitDatetime <= date_utils.get_naive_utc_now())

    @hasBookingLimitDatetimePassed.inplace.expression
    @classmethod
    def _hasBookingLimitDatetimePassedExpression(cls) -> ColumnElement[bool]:
        return sa.and_(cls.bookingLimitDatetime.is_not(None), cls.bookingLimitDatetime <= sa.func.now())

    @hybrid_property
    def remainingQuantity(self) -> int | typing.Literal["unlimited"]:
        return "unlimited" if self.quantity is None else self.quantity - self.dnBookedQuantity

    @remainingQuantity.inplace.expression
    @classmethod
    def _remainingQuantityExpression(cls) -> Case:
        return sa.case((cls.quantity.is_(None), None), else_=(cls.quantity - cls.dnBookedQuantity))

    @property
    def is_automatically_used(self) -> bool:
        return self.offer.subcategoryId in self.AUTOMATICALLY_USED_SUBCATEGORIES and not self.price

    @hybrid_property
    def isEventExpired(self) -> bool:
        return bool(self.beginningDatetime and self.beginningDatetime <= date_utils.get_naive_utc_now())

    @isEventExpired.inplace.expression
    @classmethod
    def _isEventExpiredExpression(cls) -> ColumnElement[bool]:
        return sa.and_(cls.beginningDatetime.is_not(None), cls.beginningDatetime <= sa.func.now())

    @hybrid_property
    def isExpired(self) -> bool:
        return self.isEventExpired or self.hasBookingLimitDatetimePassed

    @isExpired.inplace.expression
    @classmethod
    def _isExpiredExpression(cls) -> ColumnElement[bool]:
        return sa.or_(cls.isEventExpired, cls.hasBookingLimitDatetimePassed)

    @property
    def isEventDeletable(self) -> bool:
        if not self.beginningDatetime or self.offer.validation == OfferValidationStatus.DRAFT:
            return True
        limit_date_for_stock_deletion = self.beginningDatetime + bookings_constants.AUTO_USE_AFTER_EVENT_TIME_DELAY
        return limit_date_for_stock_deletion >= date_utils.get_naive_utc_now()

    @hybrid_property
    def isSoldOut(self) -> bool:
        return (
            self.isSoftDeleted
            or (self.beginningDatetime is not None and self.beginningDatetime <= date_utils.get_naive_utc_now())
            or (self.remainingQuantity != "unlimited" and self.remainingQuantity <= 0)
        )

    @isSoldOut.inplace.expression
    @classmethod
    def _isSoldOutExpression(cls) -> ColumnElement[bool]:
        return sa.or_(
            cls.isSoftDeleted,
            sa.and_(sa.not_(cls.beginningDatetime.is_(None)), cls.beginningDatetime <= sa.func.now()),
            sa.and_(
                sa.not_(cls.remainingQuantity.is_(None)),
                cls.remainingQuantity <= 0,
            ),
        )

    @classmethod
    def queryNotSoftDeleted(cls) -> sa_orm.Query:
        return db.session.query(Stock).filter_by(isSoftDeleted=False)

    @staticmethod
    def restize_internal_error(internal_error: sa_exc.InternalError) -> tuple[str, str]:
        if "check_stock" in str(internal_error.orig):
            if "quantity_too_low" in str(internal_error.orig):
                return ("quantity", "Le stock total ne peut être inférieur au nombre de réservations")
            if "bookingLimitDatetime_too_late" in str(internal_error.orig):
                return (
                    "bookingLimitDatetime",
                    "La date limite de réservation pour cette offre est postérieure à la date de début de l'évènement",
                )
            logger.error("Unexpected error in patch stocks: %s", internal_error)
        return PcObject.restize_internal_error(internal_error)

    @property
    def canHaveActivationCodes(self) -> bool:
        return self.offer.hasUrl

    @hybrid_property
    def remainingStock(self) -> int | None:
        if self.isBookable:
            return None if self.remainingQuantity == "unlimited" else self.remainingQuantity
        return 0

    @remainingStock.inplace.expression
    @classmethod
    def _remainingStockExpression(cls) -> Case:
        return sa.case((cls._bookable, cls.remainingQuantity), else_=0)


@sa.event.listens_for(Stock, "before_insert")
def before_insert(mapper: sa_orm.Mapper, configuration: sa.engine.Connection, self: Stock) -> None:
    if self.beginningDatetime and not self.bookingLimitDatetime:
        self.bookingLimitDatetime = self.beginningDatetime.replace(hour=23).replace(minute=59) - datetime.timedelta(
            days=3
        )


trig_stock_quantity_ddl = sa.DDL("""
    CREATE OR REPLACE FUNCTION check_stock()
    RETURNS TRIGGER AS $$
    BEGIN
      IF
       NOT NEW.quantity IS NULL
       AND
        (
         (
          SELECT SUM(booking.quantity)
          FROM booking
          WHERE "stockId"=NEW.id
          AND NOT booking.status = 'CANCELLED'
         ) > NEW.quantity
        )
      THEN
       RAISE EXCEPTION 'quantity_too_low'
       USING HINT = 'stock.quantity cannot be lower than number of bookings';
      END IF;

      IF NEW."bookingLimitDatetime" IS NOT NULL AND
        NEW."beginningDatetime" IS NOT NULL AND
         NEW."bookingLimitDatetime" > NEW."beginningDatetime" THEN

      RAISE EXCEPTION 'bookingLimitDatetime_too_late'
      USING HINT = 'bookingLimitDatetime after beginningDatetime';
      END IF;

      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS stock_update ON stock;
    CREATE CONSTRAINT TRIGGER stock_update AFTER INSERT OR UPDATE
    ON stock
    FOR EACH ROW EXECUTE PROCEDURE check_stock()
    """)

sa_event.listen(Stock.__table__, "after_create", trig_stock_quantity_ddl)

trig_update_date_ddl = sa.DDL("""
    CREATE OR REPLACE FUNCTION save_stock_modification_date()
    RETURNS TRIGGER AS $$
    BEGIN
      IF NEW.quantity != OLD.quantity THEN
        NEW."dateModified" = NOW();
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS stock_update_modification_date ON stock;

    CREATE TRIGGER stock_update_modification_date
    BEFORE UPDATE ON stock
    FOR EACH ROW
    EXECUTE PROCEDURE save_stock_modification_date()
    """)

sa_event.listen(Stock.__table__, "after_create", trig_update_date_ddl)


@dataclass
class OfferImage:
    url: str
    credit: str | None = None


class WithdrawalTypeEnum(enum.Enum):
    BY_EMAIL = "by_email"
    IN_APP = "in_app"
    NO_TICKET = "no_ticket"
    ON_SITE = "on_site"


class Weekday(enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class HeadlineOffer(PcObject, Model):
    __tablename__ = "headline_offer"

    offerId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), nullable=False, index=True, unique=False
    )
    offer: sa_orm.Mapped["Offer"] = sa_orm.relationship(
        "Offer", foreign_keys=[offerId], back_populates="headlineOffers"
    )
    venueId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id"), nullable=False, index=True, unique=False
    )
    venue: sa_orm.Mapped["Venue"] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="headlineOffers"
    )

    timespan: sa_orm.Mapped[psycopg2.extras.DateTimeRange] = sa_orm.mapped_column(postgresql.TSRANGE, nullable=False)

    __table_args__ = (
        # One Offer can have only one active Headline Offer at a time
        # To do so, we check that there are no overlaping HeadlineOffer for one Offer
        # If a timespan has no upper limit, it is the active headline offer for this offer (see property below)
        postgresql.ExcludeConstraint((offerId, "="), (timespan, "&&"), name="exclude_offer_timespan"),
        # Likewise, for now one venue can only have one active headline offer
        postgresql.ExcludeConstraint((venueId, "="), (timespan, "&&"), name="exclude_venue_timespan"),
    )

    def __init__(self, **kwargs: typing.Any) -> None:
        kwargs["timespan"] = db_utils.make_timerange(*kwargs["timespan"])
        super().__init__(**kwargs)

    @hybrid_property
    def isActive(self) -> bool:
        now = date_utils.get_naive_utc_now()
        has_images = self.offer.mediations or (self.offer.product.images if self.offer.product else None)
        if now in self.timespan and self.offer.status == OfferStatus.ACTIVE and has_images:
            return True
        return False

    @isActive.inplace.expression
    @classmethod
    def _isActiveExpression(cls) -> ColumnElement[bool]:
        offer_alias = sa_orm.aliased(Offer)  # avoids cartesian product
        return sa.and_(
            cls.timespan.contains(sa.cast(sa.func.now(), sa.TIMESTAMP)),
            offer_alias.id == cls.offerId,
            offer_alias.status == OfferStatus.ACTIVE,
            sa.or_(
                sa.exists().where(Mediation.offerId == offer_alias.id),
                sa.exists().where(ProductMediation.productId == offer_alias.productId),
            ),
        )


@sa.event.listens_for(HeadlineOffer, "after_insert")
def after_insert_headline_offer(
    _mapper: sa_orm.Mapper, connection: sa.engine.Connection, target: HeadlineOffer
) -> None:
    if not target.offer.productId:
        return

    now = date_utils.get_naive_utc_now()
    parsed_value = _parse_datetime_range(target.timespan)

    if now in parsed_value:
        _increment_product_headlines_count(connection, target.offer.productId, 1)


@sa.event.listens_for(HeadlineOffer.timespan, "set")
def on_set_timespan(
    target: HeadlineOffer,
    value: psycopg2.extras.DateTimeRange,
    old_value: psycopg2.extras.DateTimeRange,
    _initiator: sa_orm.AttributeEvents,
) -> None:
    # During object creation, old_value is not a DateTimeRange (it's the NO_VALUE symbol).
    # The after_insert event handles the count for new objects, so we can return early.
    if old_value is sa_orm.attributes.NO_VALUE:
        return

    if not target.offer.productId:
        return

    now = date_utils.get_naive_utc_now()
    parsed_value = _parse_datetime_range(value)

    is_active_before_update = now in old_value
    is_active_after_update = now in parsed_value

    if is_active_before_update and not is_active_after_update:
        _increment_product_headlines_count(db.session, target.offer.productId, -1)
    elif not is_active_before_update and is_active_after_update:
        _increment_product_headlines_count(db.session, target.offer.productId, 1)


def _parse_datetime_range(value: psycopg2.extras.DateTimeRange) -> psycopg2.extras.DateTimeRange:
    lower_bound = date_utils.get_naive_utc_from_iso_str(value.lower) if value.lower else None
    upper_bound = date_utils.get_naive_utc_from_iso_str(value.upper) if value.upper else None
    return psycopg2.extras.DateTimeRange(lower=lower_bound, upper=upper_bound)


@sa.event.listens_for(HeadlineOffer, "after_delete")
def after_delete_headline_offer(
    _mapper: sa_orm.Mapper, connection: sa.engine.Connection, target: HeadlineOffer
) -> None:
    # SQLAlchemy will not call this event if the object is deleted using a bulk delete
    # (e.g. db.session.execute(sa.delete(Chronicle).where(...)))
    if target.offer.productId:
        _increment_product_headlines_count(connection, target.offer.productId, -1)


def _increment_product_headlines_count(
    connection: sa.engine.Connection | sa_orm.scoped_session["flask_sqlalchemy.session.Session"],
    product_id: int,
    increment: int,
) -> None:
    connection.execute(
        sa.update(Product).where(Product.id == product_id).values(headlinesCount=Product.headlinesCount + increment)
    )


class ValidationRuleOfferLink(PcObject, Model):
    __tablename__ = "validation_rule_offer_link"
    ruleId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer_validation_rule.id", ondelete="CASCADE"), nullable=False
    )
    offerId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), index=True, nullable=False
    )


class OfferMetaData(PcObject, Model):
    __tablename__ = "offer_meta_data"
    offerId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), index=True, nullable=False, unique=True
    )
    offer: sa_orm.Mapped["Offer"] = sa_orm.relationship("Offer", foreign_keys=[offerId], back_populates="metaData")
    videoDuration: sa_orm.Mapped[int | None] = sa_orm.mapped_column(sa.BIGINT(), nullable=True)
    videoExternalId: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)
    videoThumbnailUrl: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)
    videoTitle: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)
    videoUrl: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)


class Offer(PcObject, Model, ValidationMixin, AccessibilityMixin):
    __tablename__ = "offer"

    MAX_STOCKS_PER_OFFER = 2_500
    MAX_PRICE_CATEGORIES_PER_OFFER = 50

    _isActive: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        "isActive", sa.Boolean, server_default=sa.true(), default=True, nullable=False
    )

    authorId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=True)
    author: sa_orm.Mapped["User | None"] = sa_orm.relationship("User", back_populates="offers", foreign_keys=[authorId])
    artistOfferLinks: sa_orm.Mapped[list["ArtistOfferLink"]] = sa_orm.relationship(
        "ArtistOfferLink", back_populates="offer", cascade="all, delete-orphan"
    )
    bookingContact: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String(120), nullable=True)
    bookingEmail: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String(120), nullable=True)
    compliance: sa_orm.Mapped["OfferCompliance | None"] = sa_orm.relationship(
        "OfferCompliance", foreign_keys="OfferCompliance.offerId", back_populates="offer", uselist=False
    )
    criteria: sa_orm.Mapped[list["Criterion"]] = sa_orm.relationship(
        "Criterion", back_populates="offers", secondary=OfferCriterion.__table__
    )
    dateCreated: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        db_utils.TimezonedDatetime, nullable=False, default=date_utils.get_naive_utc_now
    )
    dateModifiedAtLastProvider: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(
        db_utils.TimezonedDatetime, nullable=True, default=date_utils.get_naive_utc_now
    )
    dateUpdated: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(
        db_utils.TimezonedDatetime,
        nullable=True,
        default=date_utils.get_naive_utc_now,
        onupdate=date_utils.get_naive_utc_now,
    )

    finalizationDatetime: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(
        db_utils.TimezonedDatetime, nullable=True
    )
    publicationDatetime: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(
        db_utils.TimezonedDatetime, nullable=True
    )
    bookingAllowedDatetime: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(
        db_utils.TimezonedDatetime, nullable=True
    )

    _description: sa_orm.Mapped[str | None] = sa_orm.mapped_column("description", sa.Text, nullable=True)
    _durationMinutes: sa_orm.Mapped[int | None] = sa_orm.mapped_column("durationMinutes", sa.Integer, nullable=True)
    ean: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True, index=True)
    externalTicketOfficeUrl: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String, nullable=True)
    _extraData: sa_orm.Mapped[OfferExtraData | None] = sa_orm.mapped_column(
        "jsonData", sa_mutable.MutableDict.as_mutable(postgresql.JSONB)
    )
    fieldsUpdated: sa_orm.Mapped[list[str]] = sa_orm.mapped_column(
        postgresql.ARRAY(sa.String(100)), nullable=False, default=[], server_default="{}"
    )
    flaggingValidationRules: sa_orm.Mapped[list["OfferValidationRule"]] = sa_orm.relationship(
        "OfferValidationRule", secondary=ValidationRuleOfferLink.__table__, back_populates="offers"
    )

    lastProviderId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("provider.id"), nullable=True
    )
    lastProvider: sa_orm.Mapped["Provider|None"] = sa_orm.relationship("Provider", foreign_keys=[lastProviderId])
    idAtProvider: sa_orm.Mapped[str | None] = sa_orm.mapped_column(
        sa.Text,
        sa.CheckConstraint(
            '"lastProviderId" IS NULL OR "idAtProvider" IS NOT NULL',
            name="check_providable_with_provider_has_idatprovider",
        ),
        nullable=True,
    )
    isDuo: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, server_default=sa.false(), default=False, nullable=False
    )
    isNational: sa_orm.Mapped[bool] = sa_orm.mapped_column(sa.Boolean, default=False, nullable=False)
    lastValidationPrice: sa_orm.Mapped[decimal.Decimal | None] = sa_orm.mapped_column(sa.Numeric(10, 2), nullable=True)
    metaData: sa_orm.Mapped["OfferMetaData | None"] = sa_orm.relationship(
        "OfferMetaData", foreign_keys="OfferMetaData.offerId", back_populates="offer", uselist=False
    )
    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(140), nullable=False)
    priceCategories: sa_orm.Mapped[list["PriceCategory"]] = sa_orm.relationship(
        "PriceCategory",
        foreign_keys="PriceCategory.offerId",
        back_populates="offer",
        cascade="all, delete-orphan",
        single_parent=True,
    )
    productId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("product.id"), index=True, nullable=True
    )
    product: sa_orm.Mapped["Product | None"] = sa_orm.relationship(
        Product, foreign_keys=[productId], back_populates="offers"
    )
    rankingWeight: sa_orm.Mapped[int | None] = sa_orm.mapped_column(sa.Integer, nullable=True)
    subcategoryId: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False, index=True)
    url: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String(255), nullable=True)
    venueId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id"), nullable=False, index=True
    )
    venue: sa_orm.Mapped["Venue"] = sa_orm.relationship("Venue", foreign_keys=[venueId], back_populates="offers")
    withdrawalDelay: sa_orm.Mapped[int | None] = sa_orm.mapped_column(sa.BigInteger, nullable=True)
    withdrawalDetails: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    withdrawalType: sa_orm.Mapped[WithdrawalTypeEnum | None] = sa_orm.mapped_column(
        db_utils.MagicEnum(WithdrawalTypeEnum, use_values=False), nullable=True
    )
    offererAddressId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offerer_address.id"), nullable=True
    )
    offererAddress: sa_orm.Mapped["OffererAddress | None"] = sa_orm.relationship(
        "OffererAddress", foreign_keys=[offererAddressId], uselist=False
    )
    reactions: sa_orm.Mapped[list["Reaction"]] = sa_orm.relationship(
        "Reaction",
        foreign_keys="Reaction.offerId",
        back_populates="offer",
        uselist=True,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    chronicles: sa_orm.Mapped[list["Chronicle"]] = sa_orm.relationship(
        "Chronicle", back_populates="offers", secondary="offer_chronicle"
    )
    headlineOffers: sa_orm.Mapped[list["HeadlineOffer"]] = sa_orm.relationship(
        "HeadlineOffer",
        foreign_keys="HeadlineOffer.offerId",
        back_populates="offer",
        uselist=True,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    openingHours: sa_orm.Mapped[list["offerers_models.OpeningHours"]] = sa_orm.relationship(
        "OpeningHours", foreign_keys="OpeningHours.offerId", back_populates="offer", passive_deletes=True
    )
    highlight_requests: sa_orm.Mapped[list[HighlightRequest]] = sa_orm.relationship(
        HighlightRequest, foreign_keys="HighlightRequest.offerId", back_populates="offer"
    )

    custom_reimbursement_rules: sa_orm.Mapped[list["CustomReimbursementRule"]] = sa_orm.relationship(
        "CustomReimbursementRule", back_populates="offer"
    )
    mediations: sa_orm.Mapped[list["Mediation"]] = sa_orm.relationship(
        "Mediation", foreign_keys="Mediation.offerId", back_populates="offer"
    )
    reports: sa_orm.Mapped[list["OfferReport"]] = sa_orm.relationship(
        "OfferReport", foreign_keys="OfferReport.offerId", back_populates="offer"
    )
    stocks: sa_orm.Mapped[list["Stock"]] = sa_orm.relationship(
        "Stock", foreign_keys="Stock.offerId", back_populates="offer"
    )
    favorites: sa_orm.Mapped[list["Favorite"]] = sa_orm.relationship(
        "Favorite", foreign_keys="Favorite.offerId", back_populates="offer"
    )

    offer_reminders: sa_orm.Mapped[list["OfferReminder"]] = sa_orm.relationship(
        "OfferReminder", foreign_keys="OfferReminder.offerId", back_populates="offer"
    )

    isNonFreeOffer: sa_orm.Mapped["bool"] = sa_orm.query_expression()
    bookingsCount: sa_orm.Mapped["int"] = sa_orm.query_expression()
    hasPendingBookings: sa_orm.Mapped["bool"] = sa_orm.query_expression()
    chroniclesCount: sa_orm.Mapped["int"] = sa_orm.query_expression()
    likesCount: sa_orm.Mapped["int"] = sa_orm.query_expression()

    @declared_attr.directive
    def __table_args__(cls) -> tuple:
        parent_args: list = []

        # Retrieves indexes from parent mixins defined in __table_args__
        for base_class in cls.__mro__:
            try:
                parent_args += super(base_class, cls).__table_args__
            except (AttributeError, TypeError):
                pass

        parent_args += [
            sa.UniqueConstraint("idAtProvider", "venueId", name="unique_idAtProvider_venueId"),
            sa.CheckConstraint("ean ~ '^\\d{13}$'", name="check_ean_validity"),
            sa.Index("idx_offer_trgm_name", "name", postgresql_using="gin"),
            sa.Index("offer_idAtProvider", "idAtProvider"),
            sa.Index("offer_visa_idx", cls._extraData["visa"].astext),  # type: ignore [index, union-attr]
            sa.Index("offer_authorId_idx", "authorId", postgresql_using="btree"),
            sa.Index("ix_offer_lastProviderId", "lastProviderId", postgresql_where='"lastProviderId" IS NOT NULL'),
            sa.Index(
                "ix_offer_publicationDatetime",
                "publicationDatetime",
                postgresql_where='"publicationDatetime" IS NOT NULL',
            ),
            sa.Index(
                "ix_offer_bookingAllowedDatetime",
                "bookingAllowedDatetime",
                postgresql_where='"bookingAllowedDatetime" IS NOT NULL',
            ),
            sa.Index(
                "ix_offer_offererAddressId", "offererAddressId", postgresql_where='"offererAddressId" IS NOT NULL'
            ),
            sa.Index("ix_offer_venueId_subcategoryId", "venueId", "subcategoryId"),
        ]

        return tuple(parent_args)

    @property
    def extraData(self) -> OfferExtraData | None:
        if self.product:
            return self.product.extraData
        return self._extraData

    @extraData.setter
    def extraData(self, value: OfferExtraData) -> None:
        if not value:
            self._extraData = value
            return
        if self.product:
            logger.error("No extraData should be set on an offer with a product")
            self._extraData = {}
        else:
            self._extraData = value

    @property
    def description(self) -> str | None:
        if self.product:
            return self.product.description
        return self._description

    @description.setter
    def description(self, value: str | None) -> None:
        if not value:
            self._description = None
            return
        if self.product:
            logger.error("No description should be set on an offer with a product")
            self._description = None
        else:
            self._description = value

    @property
    def durationMinutes(self) -> int | None:
        if self.product:
            return self.product.durationMinutes
        return self._durationMinutes

    @durationMinutes.setter
    def durationMinutes(self, value: int | None) -> None:
        if not value:
            self._durationMinutes = None
            return
        if self.product:
            logger.error("No durationMinutes should be set on an offer with a product")
            self._durationMinutes = None
        else:
            self._durationMinutes = value

    @property
    def isEducational(self) -> bool:
        return False

    @hybrid_property
    def isSoldOut(self) -> bool:
        for stock in self.stocks:
            if (
                not stock.isSoftDeleted
                and (stock.beginningDatetime is None or stock.beginningDatetime > date_utils.get_naive_utc_now())
                and (stock.remainingQuantity == "unlimited" or stock.remainingQuantity > 0)
            ):
                return False
        return True

    @isSoldOut.inplace.expression
    @classmethod
    def _isSoldOutExpression(cls) -> ColumnElement[bool]:
        return ~sa.exists().where(Stock.offerId == cls.id).where(Stock.isSoftDeleted.is_(False)).where(
            sa.or_(Stock.beginningDatetime > sa.func.now(), Stock.beginningDatetime.is_(None))
        ).where(sa.or_(Stock.remainingQuantity.is_(None), Stock.remainingQuantity > 0))

    @property
    def activeMediation(self) -> Mediation | None:
        sorted_by_date_desc = sorted(self.mediations, key=lambda m: m.dateCreated, reverse=True)
        only_active = list(filter(lambda m: m.isActive, sorted_by_date_desc))
        return only_active[0] if only_active else None

    @hybrid_property
    def canExpire(self) -> bool:
        return self.subcategoryId in subcategories.EXPIRABLE_SUBCATEGORIES

    @canExpire.inplace.expression
    @classmethod
    def _canExpireExpression(cls) -> BinaryExpression:
        return cls.subcategoryId.in_(subcategories.EXPIRABLE_SUBCATEGORIES)

    @hybrid_property
    def isReleased(self) -> bool:
        offerer = self.venue.managingOfferer
        return self._released and offerer.isActive and offerer.isValidated

    @isReleased.inplace.expression
    @classmethod
    def _isReleasedExpression(cls) -> ColumnElement[bool]:
        from pcapi.core.offerers import models as offerers_models

        # explicit join on Venue then Offerer
        return sa.and_(
            cls._released,
            offerers_models.Offerer.isActive,
            offerers_models.Offerer.isValidated,
        )

    @hybrid_property
    def _released(self) -> bool:
        now = datetime.datetime.now(datetime.UTC)
        return self.validation == OfferValidationStatus.APPROVED and (
            self.publicationDatetime is not None and self.publicationDatetime <= now
        )

    @_released.inplace.expression
    @classmethod
    def _releasedExpression(cls) -> ColumnElement[bool]:
        return sa.and_(
            cls.validation == OfferValidationStatus.APPROVED,
            cls.publicationDatetime != None,
            cls.publicationDatetime <= sa.func.now(),
        )

    @hybrid_property
    def isPermanent(self) -> bool:
        return self.subcategoryId in subcategories.PERMANENT_SUBCATEGORIES

    @isPermanent.inplace.expression
    @classmethod
    def _isPermanentExpression(cls) -> BinaryExpression:
        return cls.subcategoryId.in_(subcategories.PERMANENT_SUBCATEGORIES)

    @hybrid_property
    def isEvent(self) -> bool:
        return self.subcategory.is_event

    @isEvent.inplace.expression
    @classmethod
    def _isEventExpression(cls) -> BinaryExpression:
        return cls.subcategoryId.in_(subcategories.EVENT_SUBCATEGORIES)

    @property
    def canBeEvent(self) -> bool:
        return self.subcategory.is_event

    @property
    def isEventLinkedToTicketingService(self) -> bool:
        return self.isEvent and self.withdrawalType == WithdrawalTypeEnum.IN_APP

    @property
    def isThing(self) -> bool:
        return not self.subcategory.is_event

    @hybrid_property
    def hasUrl(self) -> bool:
        return self.url is not None and self.url != ""

    @hasUrl.inplace.expression
    @classmethod
    def _hasUrlExpression(cls) -> ColumnElement[bool]:
        return sa.and_(cls.url.is_not(None), cls.url != "")

    @property
    def isDigital(self) -> bool:
        return self.subcategory.online_offline_platform == models.OnlineOfflinePlatformChoices.ONLINE.value

    @property
    def isEditable(self) -> bool:
        """This property is used by the pro frontend, to display the Edit button in the Offers list"""
        if not self.isFromProvider:
            return True
        return self.isFromAllocine

    @property
    def isFromProvider(self) -> bool:
        return self.lastProviderId is not None

    @property
    def isFromAllocine(self) -> bool:
        return self.lastProvider is not None and self.lastProvider.isAllocine

    @property
    def isFromCinemaProvider(self) -> bool:
        return self.lastProvider is not None and self.lastProvider.isCinemaProvider

    @property
    def isBookable(self) -> bool:
        for stock in self.stocks:
            if stock.isBookable:
                return True
        return False

    @hybrid_property
    def is_eligible_for_search(self) -> bool:
        return self.is_released_and_bookable

    @is_eligible_for_search.inplace.expression
    @classmethod
    def _is_eligible_for_search_expression(cls) -> ColumnElement[bool]:
        return sa.and_(cls._released, Stock._bookable)

    @hybrid_property
    def is_released_and_bookable(self) -> bool:
        return self.isReleased and self.isBookable

    @is_released_and_bookable.inplace.expression
    @classmethod
    def _is_released_and_bookable_expression(cls) -> ColumnElement[bool]:
        return sa.and_(cls._released, Stock._bookable)

    @hybrid_property
    def is_offer_released_with_bookable_stock(self) -> bool:
        return self.isReleased and self.isBookable

    @is_offer_released_with_bookable_stock.inplace.expression
    @classmethod
    def _is_offer_released_with_bookable_stock_expression(cls) -> ColumnElement[bool]:
        return sa.and_(cls._released, sa.exists().where(Stock.offerId == cls.id).where(Stock._bookable))

    @hybrid_property
    def hasBookingLimitDatetimesPassed(self) -> bool:
        if self.activeStocks:
            return all(stock.hasBookingLimitDatetimePassed for stock in self.activeStocks)
        return False

    @hasBookingLimitDatetimesPassed.inplace.expression
    @classmethod
    def _hasBookingLimitDatetimesPassedExpression(cls) -> ColumnElement[bool]:
        return sa.and_(
            sa.exists().where(Stock.offerId == cls.id).where(Stock.isSoftDeleted.is_(False)),
            ~sa.exists()
            .where(Stock.offerId == cls.id)
            .where(Stock.isSoftDeleted.is_(False))
            .where(Stock.hasBookingLimitDatetimePassed.is_(False)),
        )

    @property
    def metadataFirstBeginningDatetime(self) -> datetime.datetime | None:
        stocks_with_date = [stock.beginningDatetime for stock in self.stocks if stock.beginningDatetime is not None]
        return min(stocks_with_date) if stocks_with_date else None

    @property
    def activeStocks(self) -> list[Stock]:
        return [stock for stock in self.stocks if not stock.isSoftDeleted]

    @property
    def hasStocks(self) -> bool:
        return any(not stock.isSoftDeleted for stock in self.stocks)

    @property
    def bookableStocks(self) -> list[Stock]:
        return [stock for stock in self.stocks if stock.isBookable]

    @property
    def searchableStocks(self) -> list[Stock]:
        now = datetime.datetime.now(datetime.UTC)
        if (
            self.publicationDatetime
            and self.publicationDatetime <= now
            and self.bookingAllowedDatetime
            and self.bookingAllowedDatetime > now
        ):
            return self.stocks
        return self.bookableStocks

    @property
    def is_forbidden_to_underage(self) -> bool:
        return all(stock.is_forbidden_to_underage for stock in self.bookableStocks)

    @property
    def subcategory(self) -> subcategories.Subcategory:
        if self.subcategoryId not in subcategories.ALL_SUBCATEGORIES_DICT:
            raise ValueError(f"Unexpected subcategoryId (v2) '{self.subcategoryId}' for offer {self.id}")
        return subcategories.ALL_SUBCATEGORIES_DICT[self.subcategoryId]

    @property
    def category(self) -> pro_categories.Category:
        return self.subcategory.category

    @property
    def categoryId(self) -> str:  # used in validation rule, do not remove
        return self.subcategory.category.id

    @property
    def images(self) -> dict[str, OfferImage] | None:
        activeMediation = self.activeMediation
        if activeMediation:
            url = activeMediation.thumbUrl
            if url:
                return {ImageType.RECTO.value: OfferImage(url, activeMediation.credit)}

        if not self.product:
            return None

        product_images = self.product.images
        if not product_images:
            return None

        images: dict[str, OfferImage] = {}

        for image_type in ImageType:
            if image := product_images.get(image_type.value):
                images[image_type.value] = OfferImage(image, credit=None)

        return images or None

    @property
    def image(self) -> OfferImage | None:
        if self.images:
            return (
                self.images.get(ImageType.POSTER.value)
                or self.images.get(ImageType.RECTO.value)
                or self.images.get(ImageType.VERSO.value)
            )
        return None

    @property
    def thumbUrl(self) -> str | None:
        return self.image.url if self.image else None

    @property
    def min_price(self) -> decimal.Decimal | None:
        available_stocks = [stock.price for stock in self.stocks]
        if len(available_stocks) > 0:
            return min(available_stocks)

        return None

    @property
    def max_price(self) -> decimal.Decimal:
        try:
            return max(stock.price for stock in self.stocks if not stock.isSoftDeleted)
        except ValueError:  # if no non-deleted stocks
            return decimal.Decimal(0)

    @property
    def showSubType(self) -> str | None:  # used in validation rule, do not remove
        if self.extraData:
            return self.extraData.get("showSubType")
        return None

    @property
    def visibleText(self) -> str:  # used in validation rule, do not remove
        return f"{self.name} {self.description}"

    @hybrid_property
    def status(self) -> OfferStatus:
        if self.validation == OfferValidationStatus.REJECTED:
            return OfferStatus.REJECTED

        if self.validation == OfferValidationStatus.PENDING:
            return OfferStatus.PENDING

        if self.validation == OfferValidationStatus.DRAFT:
            return OfferStatus.DRAFT

        now_utc = datetime.datetime.now(datetime.UTC)

        if not self.publicationDatetime:
            return OfferStatus.INACTIVE

        if now_utc < self.publicationDatetime:
            return OfferStatus.SCHEDULED

        if self.bookingAllowedDatetime and now_utc < self.bookingAllowedDatetime:
            return OfferStatus.PUBLISHED

        if self.validation == OfferValidationStatus.APPROVED:
            if self.hasBookingLimitDatetimesPassed:
                return OfferStatus.EXPIRED
            if self.isSoldOut:
                return OfferStatus.SOLD_OUT

        return OfferStatus.ACTIVE

    @status.inplace.expression
    @classmethod
    def _status(cls) -> Case:
        cases = [
            (cls.validation == OfferValidationStatus.REJECTED.name, OfferStatus.REJECTED.name),
            (cls.validation == OfferValidationStatus.PENDING.name, OfferStatus.PENDING.name),
            (cls.validation == OfferValidationStatus.DRAFT.name, OfferStatus.DRAFT.name),
            (cls.publicationDatetime.is_(None), OfferStatus.INACTIVE.name),
            (cls.publicationDatetime > sa.func.now(), OfferStatus.SCHEDULED.name),
            (
                cls.bookingAllowedDatetime.is_not(None) & (cls.bookingAllowedDatetime > sa.func.now()),
                OfferStatus.PUBLISHED.name,
            ),
            (cls.hasBookingLimitDatetimesPassed.is_(True), OfferStatus.EXPIRED.name),
            (cls.isSoldOut.is_(True), OfferStatus.SOLD_OUT.name),
        ]

        return sa.case(*cases, else_=OfferStatus.ACTIVE.name)

    @property
    def publicationDate(self) -> datetime.datetime | None:
        # TODO(jbaudet) 2025-05: remove this property. which used the now
        # deleted future offer table. Use `publicationDatetime` instead.
        return self.publicationDatetime

    @property
    def fullAddress(self) -> str | None:
        if self.offererAddress is None:
            return None
        label = self.offererAddress.label
        if not label and self.offererAddress.addressId == self.venue.offererAddress.addressId:
            label = self.venue.common_name
        if not label:
            return self.offererAddress.address.fullAddress
        return f"{label} - {self.offererAddress.address.fullAddress}"

    @hybrid_property
    def is_headline_offer(self) -> bool:
        return any(headline_offer.isActive for headline_offer in self.headlineOffers)

    @is_headline_offer.inplace.expression
    @classmethod
    def _is_headline_offer_expression(cls) -> UnaryExpression:
        headline_offer_alias = sa_orm.aliased(HeadlineOffer)
        return sa.exists().where(headline_offer_alias.offerId == cls.id, headline_offer_alias.isActive)

    @hybrid_property
    def isActive(self) -> bool:
        if self.publicationDatetime is None:
            return False

        # publicationDatetime loaded from the DB won't be timezone-aware
        # (unfortunately). However, a fresh offer object might have a
        # timezone-aware publicationDatetime (built from python code
        # that could have used a timezone-aware datetime object).
        now = datetime.datetime.now(datetime.timezone.utc)
        now = now.replace(tzinfo=None) if self.publicationDatetime.tzinfo is None else now
        return self.publicationDatetime <= now

    @isActive.inplace.expression
    @classmethod
    def _isActiveExpression(cls) -> ColumnElement[bool]:
        return sa.and_(
            cls.publicationDatetime != None,
            cls.publicationDatetime <= sa.func.now(),
        )

    @property
    def address(self) -> geography_models.Address | None:
        return self.offererAddress.address if self.offererAddress else None


class ActivationCode(PcObject, Model):
    __tablename__ = "activation_code"

    bookingId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("booking.id"), index=True, nullable=True
    )
    booking: sa_orm.Mapped["Booking | None"] = sa_orm.relationship(
        "Booking", foreign_keys=[bookingId], back_populates="activationCode"
    )
    code: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)
    expirationDate: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(
        sa.DateTime, nullable=True, default=None
    )
    stockId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("stock.id"), index=True, nullable=False
    )
    stock: sa_orm.Mapped["Stock"] = sa_orm.relationship(
        "Stock", foreign_keys=[stockId], back_populates="activationCodes"
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "stockId",
            "code",
            name="unique_code_in_stock",
        ),
    )


class OfferValidationRuleOperator(enum.Enum):
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL_TO = ">="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL_TO = "<="
    IN = "in"
    NOT_IN = "not in"
    CONTAINS = "contains"
    CONTAINS_EXACTLY = "contains-exact"
    INTERSECTS = "intersects"
    NOT_INTERSECTS = "not intersects"


class OfferValidationModel(enum.Enum):
    OFFER = "Offer"
    COLLECTIVE_OFFER = "CollectiveOffer"
    COLLECTIVE_OFFER_TEMPLATE = "CollectiveOfferTemplate"
    STOCK = "Stock"
    COLLECTIVE_STOCK = "CollectiveStock"
    VENUE = "Venue"
    OFFERER = "Offerer"


class OfferValidationAttribute(enum.Enum):
    CLASS_NAME = "class_name"
    NAME = "name"
    DESCRIPTION = "description"
    ID = "id"
    CATEGORY_ID = "categoryId"
    SUBCATEGORY_ID = "subcategoryId"
    WITHDRAWAL_DETAILS = "withdrawalDetails"
    MAX_PRICE = "max_price"
    PRICE = "price"
    PRICE_DETAIL = "priceDetail"
    SHOW_SUB_TYPE = "showSubType"
    TEXT = "visibleText"
    FORMATS = "formats"
    AUTHOR = "extraData.author"
    PUBLISHER = "extraData.editeur"


class OfferValidationSubRuleField(enum.Enum):
    OFFER_TYPE = {
        "model": None,
        "attribute": OfferValidationAttribute.CLASS_NAME,
    }
    MAX_PRICE_OFFER = {
        "model": OfferValidationModel.OFFER,
        "attribute": OfferValidationAttribute.MAX_PRICE,
    }
    PRICE_COLLECTIVE_STOCK = {
        "model": OfferValidationModel.COLLECTIVE_STOCK,
        "attribute": OfferValidationAttribute.PRICE,
    }
    PRICE_DETAIL_COLLECTIVE_STOCK = {
        "model": OfferValidationModel.COLLECTIVE_STOCK,
        "attribute": OfferValidationAttribute.PRICE_DETAIL,
    }
    PRICE_DETAIL_COLLECTIVE_OFFER_TEMPLATE = {
        "model": OfferValidationModel.COLLECTIVE_OFFER_TEMPLATE,
        "attribute": OfferValidationAttribute.PRICE_DETAIL,
    }
    WITHDRAWAL_DETAILS_OFFER = {
        "model": OfferValidationModel.OFFER,
        "attribute": OfferValidationAttribute.WITHDRAWAL_DETAILS,
    }
    TEXT_OFFER = {
        "model": OfferValidationModel.OFFER,
        "attribute": OfferValidationAttribute.TEXT,
    }
    TEXT_COLLECTIVE_OFFER = {
        "model": OfferValidationModel.COLLECTIVE_OFFER,
        "attribute": OfferValidationAttribute.TEXT,
    }
    TEXT_COLLECTIVE_OFFER_TEMPLATE = {
        "model": OfferValidationModel.COLLECTIVE_OFFER_TEMPLATE,
        "attribute": OfferValidationAttribute.TEXT,
    }
    NAME_OFFER = {
        "model": OfferValidationModel.OFFER,
        "attribute": OfferValidationAttribute.NAME,
    }
    NAME_COLLECTIVE_OFFER = {
        "model": OfferValidationModel.COLLECTIVE_OFFER,
        "attribute": OfferValidationAttribute.NAME,
    }
    NAME_COLLECTIVE_OFFER_TEMPLATE = {
        "model": OfferValidationModel.COLLECTIVE_OFFER_TEMPLATE,
        "attribute": OfferValidationAttribute.NAME,
    }
    DESCRIPTION_OFFER = {
        "model": OfferValidationModel.OFFER,
        "attribute": OfferValidationAttribute.DESCRIPTION,
    }
    DESCRIPTION_COLLECTIVE_OFFER = {
        "model": OfferValidationModel.COLLECTIVE_OFFER,
        "attribute": OfferValidationAttribute.DESCRIPTION,
    }
    DESCRIPTION_COLLECTIVE_OFFER_TEMPLATE = {
        "model": OfferValidationModel.COLLECTIVE_OFFER_TEMPLATE,
        "attribute": OfferValidationAttribute.DESCRIPTION,
    }
    SUBCATEGORY_OFFER = {
        "model": OfferValidationModel.OFFER,
        "attribute": OfferValidationAttribute.SUBCATEGORY_ID,
    }
    CATEGORY_OFFER = {
        "model": OfferValidationModel.OFFER,
        "attribute": OfferValidationAttribute.CATEGORY_ID,
    }
    FORMATS_COLLECTIVE_OFFER = {
        "model": OfferValidationModel.COLLECTIVE_OFFER,
        "attribute": OfferValidationAttribute.FORMATS,
    }
    FORMATS_COLLECTIVE_OFFER_TEMPLATE = {
        "model": OfferValidationModel.COLLECTIVE_OFFER_TEMPLATE,
        "attribute": OfferValidationAttribute.FORMATS,
    }
    SHOW_SUB_TYPE_OFFER = {
        "model": OfferValidationModel.OFFER,
        "attribute": OfferValidationAttribute.SHOW_SUB_TYPE,
    }
    ID_VENUE = {
        "model": OfferValidationModel.VENUE,
        "attribute": OfferValidationAttribute.ID,
    }
    ID_OFFERER = {
        "model": OfferValidationModel.OFFERER,
        "attribute": OfferValidationAttribute.ID,
    }
    AUTHOR_OFFER = {
        "model": OfferValidationModel.OFFER,
        "attribute": OfferValidationAttribute.AUTHOR,
    }
    PUBLISHER_OFFER = {
        "model": OfferValidationModel.OFFER,
        "attribute": OfferValidationAttribute.PUBLISHER,
    }


class OfferValidationSubRule(PcObject, Model):
    __tablename__ = "offer_validation_sub_rule"

    validationRuleId = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer_validation_rule.id"), index=True, nullable=False
    )
    validationRule: sa_orm.Mapped["OfferValidationRule"] = sa_orm.relationship(
        "OfferValidationRule",
        foreign_keys=[validationRuleId],
        back_populates="subRules",
        order_by="OfferValidationSubRule.id.asc()",
    )
    model: sa_orm.Mapped[OfferValidationModel | None] = sa_orm.mapped_column(
        sa.Enum(OfferValidationModel), nullable=True
    )
    attribute: sa_orm.Mapped[OfferValidationAttribute] = sa_orm.mapped_column(
        sa.Enum(OfferValidationAttribute), nullable=False
    )
    operator: sa_orm.Mapped[OfferValidationRuleOperator] = sa_orm.mapped_column(
        sa.Enum(OfferValidationRuleOperator), nullable=False
    )
    comparated: sa_orm.Mapped[dict] = sa_orm.mapped_column(
        "comparated", MutableDict.as_mutable(postgresql.json.JSONB), nullable=False
    )
    __table_args__ = (
        sa.CheckConstraint(
            "(model IS NULL AND attribute = 'CLASS_NAME') OR (model IS NOT NULL AND attribute != 'CLASS_NAME')",
            name="check_not_model_and_attribute_class_or_vice_versa",
        ),
    )


class OfferValidationRule(PcObject, Model, DeactivableMixin):
    __tablename__ = "offer_validation_rule"
    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)
    offers: sa_orm.Mapped[list["Offer"]] = sa_orm.relationship(
        "Offer", secondary=ValidationRuleOfferLink.__table__, back_populates="flaggingValidationRules"
    )
    collectiveOffers: sa_orm.Mapped[list["CollectiveOffer"]] = sa_orm.relationship(
        "CollectiveOffer",
        secondary=ValidationRuleCollectiveOfferLink.__table__,
        back_populates="flaggingValidationRules",
    )
    collectiveOfferTemplates: sa_orm.Mapped[list["CollectiveOfferTemplate"]] = sa_orm.relationship(
        "CollectiveOfferTemplate",
        secondary=ValidationRuleCollectiveOfferTemplateLink.__table__,
        back_populates="flaggingValidationRules",
    )
    action_history: sa_orm.Mapped[list["ActionHistory"]] = sa_orm.relationship(
        "ActionHistory",
        foreign_keys="ActionHistory.ruleId",
        back_populates="rule",
        order_by=ACTION_HISTORY_ORDER_BY,
        passive_deletes=True,
    )

    subRules: sa_orm.Mapped[list["OfferValidationSubRule"]] = sa_orm.relationship(
        "OfferValidationSubRule",
        foreign_keys="OfferValidationSubRule.validationRuleId",
        back_populates="validationRule",
    )


class OfferPriceLimitationRule(PcObject, Model):
    __tablename__ = "offer_price_limitation_rule"
    subcategoryId: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False, unique=True)
    rate: sa_orm.Mapped[decimal.Decimal] = sa_orm.mapped_column(sa.Numeric(5, 4), nullable=False)


@dataclass
class ReasonMeta:
    description: str
    title: str


class Reason(enum.Enum):
    """
    Describe possible reason codes to used when reporting an offer.

    The whole meta part is only consumed by the api client, it has no meaning
    inside the whole API code.

    Note: when adding a new enum symbol, do not forget to update the meta method.
    """

    IMPROPER = "IMPROPER"
    PRICE_TOO_HIGH = "PRICE_TOO_HIGH"
    INAPPROPRIATE = "INAPPROPRIATE"
    OTHER = "OTHER"

    @staticmethod
    def get_meta(value: str) -> ReasonMeta:
        return Reason.get_full_meta()[value]

    @staticmethod
    def get_full_meta() -> dict[str, ReasonMeta]:
        return {
            "IMPROPER": ReasonMeta(
                title="La description est non conforme",
                description="La date ne correspond pas, mauvaise description...",
            ),
            "PRICE_TOO_HIGH": ReasonMeta(title="Le tarif est trop élevé", description="comparé à l'offre publique"),
            "INAPPROPRIATE": ReasonMeta(
                title="Le contenu est inapproprié", description="violence, incitation à la haine, nudité..."
            ),
            "OTHER": ReasonMeta(title="Autre", description=""),
        }


# if the reason is != OTHER, there should be no customReasonContent,
# and if reason = OTHER, the customReasonContent cannot be NULL or "".
OFFER_REPORT_CUSTOM_REASONS_CONSTRAINT = """
(offer_report."customReasonContent" IS NULL AND offer_report.reason != 'OTHER')
OR (
    (offer_report."customReasonContent" IS NOT NULL OR trim(both ' ' from offer_report."customReasonContent") = '')
    AND offer_report.reason = 'OTHER'
)
"""


class OfferReport(PcObject, Model):
    __tablename__ = "offer_report"

    userId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=False
    )
    user: sa_orm.Mapped["User"] = sa_orm.relationship("User", foreign_keys=[userId], back_populates="reported_offers")
    offerId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer.id"), index=True, nullable=False
    )
    offer: sa_orm.Mapped["Offer"] = sa_orm.relationship("Offer", foreign_keys=[offerId], back_populates="reports")
    reason: sa_orm.Mapped[Reason] = sa_orm.mapped_column(
        sa.Enum(Reason, create_constraint=False), nullable=False, index=True
    )
    reportedAt: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, server_default=sa.func.now()
    )
    # If the reason code is OTHER, save the user's custom reason
    customReasonContent: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)

    __table_args__ = (
        sa.UniqueConstraint(
            "userId",
            "offerId",
            name="unique_offer_per_user",
        ),
        sa.CheckConstraint(
            OFFER_REPORT_CUSTOM_REASONS_CONSTRAINT,
            name="custom_reason_null_only_if_reason_is_other",
        ),
    )

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}#{self.id} userId={self.userId}, offerId={self.offerId}, when={self.reportedAt}"
        )


class BookMacroSection(PcObject, Model):
    __tablename__ = "book_macro_section"

    macroSection: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)
    section: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)

    __table_args__ = (sa.Index("book_macro_section_section_idx", sa.func.lower(section), unique=True),)


class PriceCategoryLabel(PcObject, Model):
    __tablename__ = "price_category_label"
    label: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text(), nullable=False)
    priceCategories: sa_orm.Mapped[list["PriceCategory"]] = sa_orm.relationship(
        "PriceCategory", foreign_keys="PriceCategory.priceCategoryLabelId", back_populates="priceCategoryLabel"
    )
    venueId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), index=True, nullable=False
    )
    venue: sa_orm.Mapped["Venue"] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="priceCategoriesLabel"
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "label",
            "venueId",
            name="unique_label_venue",
        ),
    )


class PriceCategory(PcObject, Model):
    __tablename__ = "price_category"
    offerId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), index=True, nullable=False
    )
    offer: sa_orm.Mapped["Offer"] = sa_orm.relationship(
        "Offer", foreign_keys=[offerId], back_populates="priceCategories"
    )
    price: sa_orm.Mapped[decimal.Decimal] = sa_orm.mapped_column(
        sa.Numeric(10, 2), sa.CheckConstraint("price >= 0", name="check_price_is_not_negative"), nullable=False
    )
    priceCategoryLabelId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("price_category_label.id"), index=True, nullable=False
    )
    priceCategoryLabel: sa_orm.Mapped["PriceCategoryLabel"] = sa_orm.relationship(
        "PriceCategoryLabel", foreign_keys=[priceCategoryLabelId], back_populates="priceCategories"
    )
    stocks: sa_orm.Mapped[list["Stock"]] = sa_orm.relationship(
        "Stock", foreign_keys="Stock.priceCategoryId", back_populates="priceCategory", cascade="all"
    )
    idAtProvider = sa_orm.mapped_column(sa.Text, nullable=True)

    __table_args__ = (
        sa.UniqueConstraint(
            "offerId",
            "idAtProvider",
            name="unique_offer_id_id_at_provider",
        ),
    )

    @property
    def label(self) -> str:
        return self.priceCategoryLabel.label


class TiteliveGtlType(enum.Enum):
    BOOK = "book"
    MUSIC = "music"


class TiteliveGtlMapping(PcObject, Model):
    __tablename__ = "titelive_gtl_mapping"

    gtlType: sa_orm.Mapped[TiteliveGtlType] = sa_orm.mapped_column(sa.Enum(TiteliveGtlType), nullable=False)
    gtlId: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True, unique=False, index=True)
    gtlLabelLevel1: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True, unique=False)
    gtlLabelLevel2: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True, unique=False)
    gtlLabelLevel3: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True, unique=False)
    gtlLabelLevel4: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True, unique=False)

    __table_args__ = (sa.Index("gtl_type_idx", gtlType, postgresql_using="hash"),)


@dataclass
class Movie:
    allocine_id: str | None
    description: str | None
    duration: int | None
    poster_url: str | None
    visa: str | None
    title: str
    extra_data: OfferExtraData | None


class ComplianceValidationStatusPrediction(enum.Enum):
    APPROVED = "approved"
    REJECTED = "rejected"


class OfferCompliance(PcObject, Model):
    __tablename__ = "offer_compliance"

    offerId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), index=True, nullable=False, unique=True
    )
    offer: sa_orm.Mapped["Offer"] = sa_orm.relationship("Offer", foreign_keys=[offerId], back_populates="compliance")
    # Compliance_score is a score between 0 and 100. Keep it small with a smallint
    compliance_score: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.SmallInteger, nullable=False)
    compliance_reasons: sa_orm.Mapped[list[str]] = sa_orm.mapped_column(
        MutableList.as_mutable(postgresql.ARRAY(sa.String)), nullable=False
    )
    validation_status_prediction: sa_orm.Mapped[ComplianceValidationStatusPrediction | None] = sa_orm.mapped_column(
        db_utils.MagicEnum(ComplianceValidationStatusPrediction), nullable=True
    )
    validation_status_prediction_reason: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
