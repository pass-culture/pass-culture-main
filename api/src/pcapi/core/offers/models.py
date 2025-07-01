import datetime
import decimal
import enum
import logging
import typing
from dataclasses import dataclass

import psycopg2.extras
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext import mutable as sa_mutable
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.elements import BooleanClauseList
from sqlalchemy.sql.elements import Case
from sqlalchemy.sql.elements import UnaryExpression

import pcapi.core.bookings.constants as bookings_constants
from pcapi import settings
from pcapi.core.categories import pro_categories
from pcapi.core.categories import subcategories
from pcapi.core.criteria.models import OfferCriterion
from pcapi.core.educational.models import ValidationRuleCollectiveOfferLink
from pcapi.core.educational.models import ValidationRuleCollectiveOfferTemplateLink
from pcapi.core.providers.models import VenueProvider
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.accessibility_mixin import AccessibilityMixin
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.feature import FeatureToggle
from pcapi.models.has_thumb_mixin import HasThumbMixin
from pcapi.models.offer_mixin import OfferStatus
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import ValidationMixin
from pcapi.models.pc_object import BaseQuery
from pcapi.models.pc_object import PcObject
from pcapi.models.soft_deletable_mixin import SoftDeletableMixin
from pcapi.utils import db as db_utils


logger = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    from pcapi.core.bookings.models import Booking
    from pcapi.core.criteria.models import Criterion
    from pcapi.core.educational.models import CollectiveOffer
    from pcapi.core.educational.models import CollectiveOfferTemplate
    from pcapi.core.offerers.models import OffererAddress
    from pcapi.core.offerers.models import Venue
    from pcapi.core.providers.models import Provider
    from pcapi.core.reactions.models import Reaction
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
    dispo: str | None
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


class ProductMediation(PcObject, Base, Model):
    __tablename__ = "product_mediation"

    dateModifiedAtLastProvider = sa.Column(sa.DateTime, nullable=True, default=datetime.datetime.utcnow)
    imageType: sa_orm.Mapped[ImageType] = sa.Column(sa.Enum(ImageType), nullable=False)
    lastProviderId = sa.Column(sa.BigInteger, sa.ForeignKey("provider.id"), nullable=True)
    lastProvider: sa_orm.Mapped["Provider|None"] = sa_orm.relationship("Provider", foreign_keys=[lastProviderId])
    productId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("product.id", ondelete="CASCADE"), index=True, nullable=False
    )
    uuid: str = sa.Column(sa.Text, nullable=False, unique=True)

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


class Product(PcObject, Base, Model, HasThumbMixin):
    __tablename__ = "product"

    dateModifiedAtLastProvider = sa.Column(sa.DateTime, nullable=True, default=datetime.datetime.utcnow)
    description = sa.Column(sa.Text, nullable=True)
    durationMinutes = sa.Column(sa.Integer, nullable=True)
    extraData: OfferExtraData | None = sa.Column("jsonData", sa_mutable.MutableDict.as_mutable(postgresql.JSONB))
    gcuCompatibilityType = sa.Column(
        db_utils.MagicEnum(GcuCompatibilityType),
        nullable=False,
        default=GcuCompatibilityType.COMPATIBLE,
        server_default=GcuCompatibilityType.COMPATIBLE.value,
    )
    last_30_days_booking = sa.Column(sa.Integer, nullable=True)
    lastProviderId: int = sa.Column(sa.BigInteger, sa.ForeignKey("provider.id"), nullable=True)
    lastProvider: sa_orm.Mapped["Provider|None"] = sa_orm.relationship("Provider", foreign_keys=[lastProviderId])
    name: str = sa.Column(sa.String(140), nullable=False)
    subcategoryId: str = sa.Column(sa.Text, nullable=False, index=True)
    thumb_path_component = "products"
    reactions: sa_orm.Mapped[list["Reaction"]] = sa_orm.relationship("Reaction", back_populates="product", uselist=True)
    productMediations: sa_orm.Mapped[list[ProductMediation]] = sa_orm.relationship(
        "ProductMediation",
        backref="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    ean = sa.Column(sa.Text, sa.CheckConstraint("ean ~ '^\\d{13}$'", name="check_ean_validity"), nullable=True)

    chroniclesCount: int | None = sa.Column(
        sa.BigInteger,
        sa.CheckConstraint('"chroniclesCount" >= 0', name="check_chronicles_count_is_positive"),
        nullable=False,
        server_default=sa.text("0"),
    )
    headlinesCount: int | None = sa.Column(
        sa.BigInteger,
        sa.CheckConstraint('"headlinesCount" >= 0', name="check_headlines_count_is_positive"),
        nullable=False,
        server_default=sa.text("0"),
    )
    likesCount: int | None = sa.Column(
        sa.BigInteger,
        sa.CheckConstraint('"likesCount" >= 0', name="check_likes_count_is_positive"),
        nullable=False,
        server_default=sa.text("0"),
    )

    sa.Index("product_allocineId_idx", extraData["allocineId"].cast(sa.Integer))
    sa.Index("product_visa_idx", extraData["visa"].astext)
    sa.Index("unique_ix_product_ean", ean, unique=True)

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


class Mediation(PcObject, Base, Model, HasThumbMixin, DeactivableMixin):
    __tablename__ = "mediation"

    author: sa_orm.Mapped["User | None"] = sa_orm.relationship("User", backref="mediations")
    authorId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    credit = sa.Column(sa.String(255), nullable=True)
    dateCreated: datetime.datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    dateModifiedAtLastProvider = sa.Column(sa.DateTime, nullable=True, default=datetime.datetime.utcnow)
    lastProviderId: int = sa.Column(sa.BigInteger, sa.ForeignKey("provider.id"), nullable=True)
    lastProvider: sa_orm.Mapped["Provider | None"] = sa_orm.relationship("Provider", foreign_keys=[lastProviderId])
    offer: sa_orm.Mapped["Offer"] = sa_orm.relationship("Offer", backref="mediations")
    offerId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id"), index=True, nullable=False)
    thumb_path_component = "mediations"


class Stock(PcObject, Base, Model, SoftDeletableMixin):
    __tablename__ = "stock"

    MAX_STOCK_QUANTITY = 1_000_000

    activationCodes: sa_orm.Mapped[list["ActivationCode"]] = sa_orm.relationship(
        "ActivationCode", back_populates="stock"
    )
    beginningDatetime: datetime.datetime | None = sa.Column(sa.DateTime, nullable=True)
    bookingLimitDatetime = sa.Column(sa.DateTime, nullable=True)
    dateCreated: datetime.datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.datetime.utcnow, server_default=sa.func.now()
    )
    dateModified: datetime.datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    dnBookedQuantity: int = sa.Column(sa.BigInteger, nullable=False, server_default=sa.text("0"))
    offer: sa_orm.Mapped["Offer"] = sa_orm.relationship("Offer", backref="stocks")
    offerId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id"), index=True, nullable=False)
    price: decimal.Decimal = sa.Column(
        sa.Numeric(10, 2),
        sa.CheckConstraint("price >= 0", name="check_price_is_not_negative"),
        index=True,
        nullable=False,
    )
    priceCategoryId: int | None = sa.Column(
        sa.BigInteger, sa.ForeignKey("price_category.id"), index=True, nullable=True
    )
    priceCategory: sa_orm.Mapped["PriceCategory | None"] = sa_orm.relationship("PriceCategory", back_populates="stocks")
    quantity: int | None = sa.Column(sa.Integer, nullable=True)
    # FIXME: mageoffray (2024-01-05) : remove this column when Provider API is not used anymore
    rawProviderQuantity = sa.Column(sa.Integer, nullable=True)
    features: list[str] = sa.Column(postgresql.ARRAY(sa.Text), nullable=False, server_default=sa.text("'{}'::text[]"))
    eventOpeningHoursId: sa_orm.Mapped[int] = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("event_opening_hours.id"),
        sa.CheckConstraint(
            '"eventOpeningHoursId" IS NULL OR "beginningDatetime" IS NULL',
            name="check_stock_with_opening_hours_does_not_have_beginningDatetime",
        ),
        nullable=True,
    )
    eventOpeningHours: sa_orm.Mapped["EventOpeningHours"] = relationship(
        "EventOpeningHours", foreign_keys=[eventOpeningHoursId]
    )

    @declared_attr
    def lastProviderId(cls) -> sa_orm.Mapped[int | None]:
        return sa.Column(sa.BigInteger, sa.ForeignKey("provider.id"), nullable=True)

    @declared_attr
    def lastProvider(cls) -> sa_orm.Mapped["Provider | None"]:
        return relationship("Provider", foreign_keys=[cls.lastProviderId])

    idAtProviders = sa.Column(
        sa.String(70),
        sa.CheckConstraint(
            '"lastProviderId" IS NULL OR "idAtProviders" IS NOT NULL',
            name="check_providable_with_provider_has_idatproviders",
        ),
        nullable=True,
    )

    dateModifiedAtLastProvider = sa.Column(sa.DateTime, nullable=True, default=datetime.datetime.utcnow)

    fieldsUpdated: sa_orm.Mapped[list[str]] = sa.Column(
        postgresql.ARRAY(sa.String(100)), nullable=False, default=[], server_default="{}"
    )

    # First step : Create a unique index on offerId/idAtProviders
    # Next step : Create a unicity constraint based on this index and to drop the unicity constraint on idAtProviders
    sa.Index("unique_ix_offer_id_id_at_providers", offerId, idAtProviders, unique=True)
    sa.Index("ix_stock_idAtProviders", idAtProviders)

    __table_args__ = (
        sa.Index(
            "ix_stock_beginningDatetime_partial", beginningDatetime, postgresql_where=beginningDatetime.is_not(None)
        ),
        sa.Index(
            "ix_stock_bookingLimitDatetime_partial",
            bookingLimitDatetime,
            postgresql_where=bookingLimitDatetime.is_not(None),
        ),
    )

    @property
    def isBookable(self) -> bool:
        return self._bookable and self.offer.isReleased

    @hybrid_property
    def _bookable(self) -> bool:
        return not self.isExpired and not self.isSoldOut

    @_bookable.expression  # type: ignore[no-redef]
    def _bookable(cls) -> BooleanClauseList:
        return sa.and_(sa.not_(cls.isExpired), sa.not_(cls.isSoldOut))

    @property
    def is_forbidden_to_underage(self) -> bool:
        return (self.price > 0 and not self.offer.subcategory.is_bookable_by_underage_when_not_free) or (
            self.price == 0 and not self.offer.subcategory.is_bookable_by_underage_when_free
        )

    @hybrid_property
    def hasBookingLimitDatetimePassed(self) -> bool:
        return bool(self.bookingLimitDatetime and self.bookingLimitDatetime <= datetime.datetime.utcnow())

    @hasBookingLimitDatetimePassed.expression  # type: ignore[no-redef]
    def hasBookingLimitDatetimePassed(cls) -> BooleanClauseList:
        return sa.and_(cls.bookingLimitDatetime.is_not(None), cls.bookingLimitDatetime <= sa.func.now())

    # TODO(fseguin, 2021-03-25): replace unlimited by None (also in the front-end)
    @hybrid_property
    def remainingQuantity(self) -> int | str:
        return "unlimited" if self.quantity is None else self.quantity - self.dnBookedQuantity

    @remainingQuantity.expression  # type: ignore[no-redef]
    def remainingQuantity(cls) -> Case:
        return sa.case((cls.quantity.is_(None), None), else_=(cls.quantity - cls.dnBookedQuantity))

    AUTOMATICALLY_USED_SUBCATEGORIES = [
        subcategories.CARTE_MUSEE.id,
        subcategories.ABO_BIBLIOTHEQUE.id,
        subcategories.ABO_MEDIATHEQUE.id,
    ]

    @property
    def is_automatically_used(self) -> bool:
        return self.offer.subcategoryId in self.AUTOMATICALLY_USED_SUBCATEGORIES and not self.price

    @hybrid_property
    def isEventExpired(self) -> bool:
        return bool(self.beginningDatetime and self.beginningDatetime <= datetime.datetime.utcnow())

    @isEventExpired.expression  # type: ignore[no-redef]
    def isEventExpired(cls) -> BooleanClauseList:
        return sa.and_(cls.beginningDatetime.is_not(None), cls.beginningDatetime <= sa.func.now())

    @hybrid_property
    def isExpired(self) -> bool:
        return self.isEventExpired or self.hasBookingLimitDatetimePassed

    @isExpired.expression  # type: ignore[no-redef]
    def isExpired(cls) -> BooleanClauseList:
        return sa.or_(cls.isEventExpired, cls.hasBookingLimitDatetimePassed)

    @property
    def isEventDeletable(self) -> bool:
        if not self.beginningDatetime or self.offer.validation == OfferValidationStatus.DRAFT:
            return True
        limit_date_for_stock_deletion = self.beginningDatetime + bookings_constants.AUTO_USE_AFTER_EVENT_TIME_DELAY
        return limit_date_for_stock_deletion >= datetime.datetime.utcnow()

    @hybrid_property
    def isSoldOut(self) -> bool:
        return (
            self.isSoftDeleted
            or (self.beginningDatetime is not None and self.beginningDatetime <= datetime.datetime.utcnow())
            or (self.remainingQuantity != "unlimited" and self.remainingQuantity <= 0)
        )

    @isSoldOut.expression  # type: ignore[no-redef]
    def isSoldOut(cls) -> BooleanClauseList:
        return sa.or_(
            cls.isSoftDeleted,
            sa.and_(sa.not_(cls.beginningDatetime.is_(None)), cls.beginningDatetime <= sa.func.now()),
            sa.and_(
                sa.not_(cls.remainingQuantity.is_(None)),
                cls.remainingQuantity <= 0,
            ),
        )

    @classmethod
    def queryNotSoftDeleted(cls) -> BaseQuery:
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
        return self.offer.isDigital

    @hybrid_property
    def remainingStock(self) -> int | None:
        if self.isBookable:
            return None if self.remainingQuantity == "unlimited" else self.remainingQuantity
        return 0

    @remainingStock.expression  # type: ignore[no-redef]
    def remainingStock(cls) -> Case:
        return sa.case((cls._bookable, cls.remainingQuantity), else_=0)


@sa.event.listens_for(Stock, "before_insert")
def before_insert(mapper: sa_orm.Mapper, configuration: sa.engine.Connection, self: Stock) -> None:
    if self.beginningDatetime and not self.bookingLimitDatetime:
        self.bookingLimitDatetime = self.beginningDatetime.replace(hour=23).replace(minute=59) - datetime.timedelta(
            days=3
        )


Stock.trig_ddl = """
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
    """

sa.event.listen(Stock.__table__, "after_create", sa.DDL(Stock.trig_ddl))

Stock.trig_update_date_ddl = """
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
    """

sa.event.listen(Stock.__table__, "after_create", sa.DDL(Stock.trig_update_date_ddl))


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


class EventOpeningHours(PcObject, Base, Model, SoftDeletableMixin):
    __tablename__ = "event_opening_hours"

    offerId: sa_orm.Mapped[int] = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id"), nullable=False, index=True)
    offer: sa_orm.Mapped["Offer"] = relationship("Offer", foreign_keys=[offerId], back_populates="eventOpeningHours")

    # To track
    dateCreated: sa_orm.Mapped[datetime.datetime] = sa.Column(
        sa.DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    dateUpdated: sa_orm.Mapped[datetime.datetime | None] = sa.Column(
        sa.DateTime, nullable=True, onupdate=datetime.datetime.utcnow
    )

    # Event parameters
    startDatetime: sa_orm.Mapped[datetime.datetime] = sa.Column(sa.DateTime, nullable=False)
    endDatetime: sa_orm.Mapped[datetime.datetime | None] = sa.Column(sa.DateTime, nullable=True)
    weekDayOpeningHours: sa_orm.Mapped[list["EventWeekDayOpeningHours"]] = relationship(
        "EventWeekDayOpeningHours", passive_deletes=True
    )


class EventWeekDayOpeningHours(PcObject, Base, Model):
    __tablename__ = "event_week_day_opening_hours"

    eventOpeningHoursId: sa_orm.Mapped[int] = sa.Column(
        sa.BigInteger, sa.ForeignKey("event_opening_hours.id", ondelete="CASCADE"), nullable=False, index=True
    )
    eventOpeningHours: sa_orm.Mapped[EventOpeningHours] = relationship(
        "EventOpeningHours", foreign_keys=[eventOpeningHoursId], back_populates="weekDayOpeningHours"
    )
    weekday: sa_orm.Mapped[Weekday] = sa.Column(db_utils.MagicEnum(Weekday), nullable=False)
    timeSpans: sa_orm.Mapped[list[psycopg2.extras.NumericRange]] = sa.Column(
        postgresql.ARRAY(postgresql.ranges.NUMRANGE)
    )

    __table_args__ = (
        sa.CheckConstraint(sa.func.cardinality(timeSpans) <= 2, name="max_timespan_is_2"),
        sa.UniqueConstraint("weekday", "eventOpeningHoursId", name="unique_weekday_eventOpeningHoursDetailsId"),
    )


class HeadlineOffer(PcObject, Base, Model):
    __tablename__ = "headline_offer"

    offerId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), nullable=False, index=True, unique=False
    )
    offer: sa_orm.Mapped["Offer"] = sa_orm.relationship("Offer", back_populates="headlineOffers")
    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), nullable=False, index=True, unique=False)
    venue: sa_orm.Mapped["Venue"] = sa_orm.relationship("Venue", back_populates="headlineOffers")

    timespan: psycopg2.extras.DateTimeRange = sa.Column(postgresql.TSRANGE, nullable=False)

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
        now = datetime.datetime.utcnow()
        has_images = self.offer.mediations or (self.offer.product.images if self.offer.product else None)
        return now in self.timespan and self.offer.status == OfferStatus.ACTIVE and has_images

    @isActive.expression  # type: ignore[no-redef]
    def isActive(cls) -> bool:
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
def after_insert_product_reaction(
    _mapper: sa_orm.Mapper, connection: sa.engine.Connection, target: HeadlineOffer
) -> None:
    if target.offer.productId:
        _increment_product_headlines_count(connection, target.offer.productId, 1)


@sa.event.listens_for(HeadlineOffer, "after_delete")
def after_delete_product_reaction(
    _mapper: sa_orm.Mapper, connection: sa.engine.Connection, target: HeadlineOffer
) -> None:
    # SQLAlchemy will not call this event if the object is deleted using a bulk delete
    # (e.g. db.session.execute(sa.delete(Chronicle).where(...)))
    if target.offer.productId:
        _increment_product_headlines_count(connection, target.offer.productId, -1)


def _increment_product_headlines_count(connection: sa.engine.Connection, product_id: int, increment: int) -> None:
    connection.execute(
        sa.update(Product).where(Product.id == product_id).values(headlinesCount=Product.headlinesCount + increment)
    )


class ValidationRuleOfferLink(PcObject, Base, Model):
    __tablename__ = "validation_rule_offer_link"
    ruleId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("offer_validation_rule.id", ondelete="CASCADE"), nullable=False
    )
    offerId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), index=True, nullable=False)


class Offer(PcObject, Base, Model, DeactivableMixin, ValidationMixin, AccessibilityMixin):
    __tablename__ = "offer"

    @declared_attr
    def __table_args__(self):
        parent_args = []

        # Retrieves indexes from parent mixins defined in __table_args__
        for base_class in self.__mro__:
            try:
                parent_args += super(base_class, self).__table_args__
            except (AttributeError, TypeError):
                pass

        parent_args += [
            sa.UniqueConstraint("idAtProvider", "venueId", name="unique_idAtProvider_venueId"),
            sa.CheckConstraint("ean ~ '^\\d{13}$'", name="check_ean_validity"),
        ]

        return tuple(parent_args)

    MAX_STOCKS_PER_OFFER = 2_500
    MAX_PRICE_CATEGORIES_PER_OFFER = 50

    authorId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=True)
    author: sa_orm.Mapped["User | None"] = relationship(
        "User", backref="offers", foreign_keys=[authorId], uselist=False
    )
    bookingContact = sa.Column(sa.String(120), nullable=True)
    bookingEmail = sa.Column(sa.String(120), nullable=True)
    compliance: sa_orm.Mapped["OfferCompliance | None"] = sa_orm.relationship(
        "OfferCompliance", back_populates="offer", uselist=False
    )
    criteria: sa_orm.Mapped[list["Criterion"]] = sa_orm.relationship(
        "Criterion", backref=sa_orm.backref("criteria", lazy="dynamic"), secondary=OfferCriterion.__table__
    )
    dateCreated: datetime.datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    dateModifiedAtLastProvider = sa.Column(sa.DateTime, nullable=True, default=datetime.datetime.utcnow)
    dateUpdated: datetime.datetime = sa.Column(
        sa.DateTime, nullable=True, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    finalizationDatetime: sa_orm.Mapped[datetime.datetime | None] = sa.Column(sa.DateTime, nullable=True)
    publicationDatetime: sa_orm.Mapped[datetime.datetime | None] = sa.Column(sa.DateTime, nullable=True)
    bookingAllowedDatetime: sa_orm.Mapped[datetime.datetime | None] = sa.Column(sa.DateTime, nullable=True)

    _description = sa.Column("description", sa.Text, nullable=True)
    _durationMinutes = sa.Column("durationMinutes", sa.Integer, nullable=True)
    ean = sa.Column(sa.Text, nullable=True, index=True)
    externalTicketOfficeUrl = sa.Column(sa.String, nullable=True)
    _extraData: OfferExtraData | None = sa.Column("jsonData", sa_mutable.MutableDict.as_mutable(postgresql.JSONB))
    fieldsUpdated: list[str] = sa.Column(
        postgresql.ARRAY(sa.String(100)), nullable=False, default=[], server_default="{}"
    )
    flaggingValidationRules: sa_orm.Mapped[list["OfferValidationRule"]] = sa_orm.relationship(
        "OfferValidationRule", secondary=ValidationRuleOfferLink.__table__, back_populates="offers"
    )

    lastProviderId = sa.Column(sa.BigInteger, sa.ForeignKey("provider.id"), nullable=True)
    lastProvider: sa_orm.Mapped["Provider|None"] = sa_orm.relationship("Provider", foreign_keys=[lastProviderId])
    idAtProvider = sa.Column(
        sa.Text,
        sa.CheckConstraint(
            '"lastProviderId" IS NULL OR "idAtProvider" IS NOT NULL',
            name="check_providable_with_provider_has_idatprovider",
        ),
        nullable=True,
    )
    isDuo: bool = sa.Column(sa.Boolean, server_default=sa.false(), default=False, nullable=False)
    isNational: bool = sa.Column(sa.Boolean, default=False, nullable=False)
    lastValidationPrice: decimal.Decimal = sa.Column(sa.Numeric(10, 2), nullable=True)
    name: str = sa.Column(sa.String(140), nullable=False)
    priceCategories: sa_orm.Mapped[list["PriceCategory"]] = sa_orm.relationship("PriceCategory", back_populates="offer")
    product: sa_orm.Mapped["Product | None"] = sa_orm.relationship(
        Product, backref=sa_orm.backref("offers", order_by="Offer.id")
    )
    productId: int = sa.Column(sa.BigInteger, sa.ForeignKey("product.id"), index=True, nullable=True)
    rankingWeight = sa.Column(sa.Integer, nullable=True)
    subcategoryId: str = sa.Column(sa.Text, nullable=False, index=True)
    url = sa.Column(sa.String(255), nullable=True)
    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), nullable=False, index=True)
    venue: sa_orm.Mapped["Venue"] = sa_orm.relationship("Venue", foreign_keys=[venueId], backref="offers")
    withdrawalDelay = sa.Column(sa.BigInteger, nullable=True)
    withdrawalDetails = sa.Column(sa.Text, nullable=True)
    withdrawalType = sa.Column(sa.Enum(WithdrawalTypeEnum), nullable=True)
    offererAddressId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offerer_address.id"), nullable=True)
    offererAddress: sa_orm.Mapped["OffererAddress | None"] = sa_orm.relationship(
        "OffererAddress", foreign_keys=[offererAddressId], uselist=False
    )
    reactions: sa_orm.Mapped[list["Reaction"]] = sa_orm.relationship(
        "Reaction", back_populates="offer", uselist=True, cascade="all, delete-orphan", passive_deletes=True
    )
    headlineOffers: sa_orm.Mapped[list["HeadlineOffer"]] = sa_orm.relationship(
        "HeadlineOffer", back_populates="offer", uselist=True, cascade="all, delete-orphan", passive_deletes=True
    )
    # eventOpeningHours is a list, but will only contain at most ONE element that is not soft deleted
    eventOpeningHours: sa_orm.Mapped[list["EventOpeningHours"]] = relationship(
        "EventOpeningHours", passive_deletes=True
    )

    sa.Index("idx_offer_trgm_name", name, postgresql_using="gin")
    sa.Index("offer_idAtProvider", idAtProvider)
    sa.Index("offer_visa_idx", _extraData["visa"].astext)
    sa.Index("offer_authorId_idx", authorId, postgresql_using="btree")
    sa.Index("ix_offer_lastProviderId", lastProviderId, postgresql_where=lastProviderId.is_not(None))
    sa.Index("ix_offer_publicationDatetime", publicationDatetime, postgresql_where=publicationDatetime.is_not(None))
    sa.Index(
        "ix_offer_bookingAllowedDatetime", bookingAllowedDatetime, postgresql_where=bookingAllowedDatetime.is_not(None)
    )

    sa.Index("ix_offer_offererAddressId", offererAddressId, postgresql_where=offererAddressId.is_not(None))
    isNonFreeOffer: sa_orm.Mapped["bool"] = sa_orm.query_expression()
    bookingsCount: sa_orm.Mapped["int"] = sa_orm.query_expression()
    hasPendingBookings: sa_orm.Mapped["bool"] = sa_orm.query_expression()
    likesCount: sa_orm.Mapped["int"] = sa_orm.query_expression()

    @property
    def extraData(self) -> OfferExtraData | None:
        if self.product:
            return self.product.extraData
        return self._extraData

    @extraData.setter
    def extraData(self, value: dict) -> None:
        if not value:
            self._extraData = value
            return
        if self.product:
            logger.error("No extraData should be set on an offer with a product")
            self._extraData = None
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
                and (stock.beginningDatetime is None or stock.beginningDatetime > datetime.datetime.utcnow())
                and (stock.remainingQuantity == "unlimited" or stock.remainingQuantity > 0)
            ):
                return False
        return True

    @isSoldOut.expression  # type: ignore[no-redef]
    def isSoldOut(cls) -> UnaryExpression:
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

    @canExpire.expression  # type: ignore[no-redef]
    def canExpire(cls) -> BinaryExpression:
        return cls.subcategoryId.in_(subcategories.EXPIRABLE_SUBCATEGORIES)

    @property
    def isReleased(self) -> bool:
        offerer = self.venue.managingOfferer
        return self._released and offerer.isActive and offerer.isValidated

    @hybrid_property
    def _released(self) -> bool:
        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        return (
            self.isActive
            and self.validation == OfferValidationStatus.APPROVED
            and (self.publicationDatetime is not None and self.publicationDatetime <= now)
        )

    @_released.expression  # type: ignore[no-redef]
    def _released(cls) -> BooleanClauseList:
        return sa.and_(
            cls.isActive,
            cls.validation == OfferValidationStatus.APPROVED,
            sa.or_(cls.publicationDatetime != None, cls.publicationDatetime <= sa.func.now()),
        )

    @hybrid_property
    def isPermanent(self) -> bool:
        return self.subcategoryId in subcategories.PERMANENT_SUBCATEGORIES

    @isPermanent.expression  # type: ignore[no-redef]
    def isPermanent(cls) -> BinaryExpression:
        return cls.subcategoryId.in_(subcategories.PERMANENT_SUBCATEGORIES)

    @hybrid_property
    def isEvent(self) -> bool:
        return self.subcategory.is_event

    @isEvent.expression  # type: ignore[no-redef]
    def isEvent(cls) -> BinaryExpression:
        return cls.subcategoryId.in_(subcategories.EVENT_SUBCATEGORIES)

    @property
    def isEventLinkedToTicketingService(self) -> bool:
        return self.isEvent and self.withdrawalType == WithdrawalTypeEnum.IN_APP

    @property
    def isThing(self) -> bool:
        return not self.subcategory.is_event

    @hybrid_property
    def isDigital(self) -> bool:
        return self.url is not None and self.url != ""

    @isDigital.expression  # type: ignore[no-redef]
    def isDigital(cls) -> BooleanClauseList:
        return sa.and_(cls.url.is_not(None), cls.url != "")

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

    @is_eligible_for_search.expression  # type: ignore[no-redef]
    def is_eligible_for_search(cls) -> BooleanClauseList:
        return sa.and_(cls._released, Stock._bookable)

    @hybrid_property
    def is_released_and_bookable(self) -> bool:
        return self.isReleased and self.isBookable

    @is_released_and_bookable.expression  # type: ignore[no-redef]
    def is_released_and_bookable(cls) -> BooleanClauseList:
        return sa.and_(cls._released, Stock._bookable)

    @hybrid_property
    def is_offer_released_with_bookable_stock(self) -> bool:
        return self.isReleased and self.isBookable

    @is_offer_released_with_bookable_stock.expression  # type: ignore[no-redef]
    def is_offer_released_with_bookable_stock(cls) -> BooleanClauseList:
        return sa.and_(cls._released, sa.exists().where(Stock.offerId == cls.id).where(Stock._bookable))

    @hybrid_property
    def hasBookingLimitDatetimesPassed(self) -> bool:
        if self.activeStocks:
            return all(stock.hasBookingLimitDatetimePassed for stock in self.activeStocks)
        return False

    @hasBookingLimitDatetimesPassed.expression  # type: ignore[no-redef]
    def hasBookingLimitDatetimesPassed(cls) -> BooleanClauseList:
        return sa.and_(
            sa.exists().where(Stock.offerId == cls.id).where(Stock.isSoftDeleted.is_(False)),
            ~sa.exists()
            .where(Stock.offerId == cls.id)
            .where(Stock.isSoftDeleted.is_(False))
            .where(Stock.hasBookingLimitDatetimePassed.is_(False)),
        )

    @hybrid_property
    def firstBeginningDatetime(self) -> datetime.datetime | None:
        stocks_with_date = [
            stock.beginningDatetime for stock in self.activeStocks if stock.beginningDatetime is not None
        ]
        return min(stocks_with_date) if stocks_with_date else None

    @firstBeginningDatetime.expression  # type: ignore[no-redef]
    def firstBeginningDatetime(cls) -> datetime.datetime | None:
        return (
            sa.select(sa.func.min(Stock.beginningDatetime))
            .where(Stock.offerId == cls.id)
            .where(Stock.isSoftDeleted.is_(False))
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
        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
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

        images = {
            image_type.value: OfferImage(product_images[image_type.value], credit=None)
            for image_type in ImageType
            if product_images.get(image_type.value)
        }
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
    def min_price(self) -> float | None:
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
    def is_expired(self) -> bool:
        return self.hasBookingLimitDatetimesPassed

    @is_expired.expression  # type: ignore[no-redef]
    def is_expired(cls) -> UnaryExpression:
        return cls.hasBookingLimitDatetimesPassed

    @hybrid_property
    def status(self) -> OfferStatus:
        if self.validation == OfferValidationStatus.REJECTED:
            return OfferStatus.REJECTED

        if self.validation == OfferValidationStatus.PENDING:
            return OfferStatus.PENDING

        if self.validation == OfferValidationStatus.DRAFT:
            return OfferStatus.DRAFT

        if FeatureToggle.WIP_REFACTO_FUTURE_OFFER.is_active():
            now_utc = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

            if not self.publicationDatetime:
                return OfferStatus.INACTIVE

            if now_utc < self.publicationDatetime:
                return OfferStatus.SCHEDULED

            if self.bookingAllowedDatetime and now_utc < self.bookingAllowedDatetime:
                return OfferStatus.PUBLISHED
        else:
            if not self.isActive:
                return OfferStatus.INACTIVE

        if self.validation == OfferValidationStatus.APPROVED:
            if self.hasBookingLimitDatetimesPassed:
                return OfferStatus.EXPIRED
            if self.isSoldOut:
                return OfferStatus.SOLD_OUT

        return OfferStatus.ACTIVE

    @status.expression  # type: ignore[no-redef]
    def status(cls) -> Case:
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
    def isActivable(self) -> bool:
        if self.status == OfferStatus.REJECTED:
            return False
        if (
            self.lastProviderId
            and not db.session.query(VenueProvider)
            .filter_by(
                isActive=True,
                venueId=self.venueId,
                providerId=self.lastProviderId,
            )
            .one_or_none()
        ):
            return False
        return True

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
        if self.offererAddressId == self.venue.offererAddressId:
            label = self.venue.common_name
        if not label:
            return self.offererAddress.address.fullAddress
        return f"{label} - {self.offererAddress.address.fullAddress}"

    @hybrid_property
    def is_headline_offer(self) -> bool:
        return any(headline_offer.isActive for headline_offer in self.headlineOffers)

    @is_headline_offer.expression  # type: ignore[no-redef]
    def is_headline_offer(cls) -> UnaryExpression:
        headline_offer_alias = sa_orm.aliased(HeadlineOffer)
        return sa.exists().where(headline_offer_alias.offerId == cls.id, headline_offer_alias.isActive)


class ActivationCode(PcObject, Base, Model):
    __tablename__ = "activation_code"

    booking: sa_orm.Mapped["Booking | None"] = sa_orm.relationship("Booking", back_populates="activationCode")
    bookingId = sa.Column(sa.BigInteger, sa.ForeignKey("booking.id"), index=True, nullable=True)
    code: str = sa.Column(sa.Text, nullable=False)
    expirationDate = sa.Column(sa.DateTime, nullable=True, default=None)
    stock: sa_orm.Mapped["Stock"] = sa_orm.relationship("Stock", back_populates="activationCodes")
    stockId: int = sa.Column(sa.BigInteger, sa.ForeignKey("stock.id"), index=True, nullable=False)

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


class OfferValidationSubRule(PcObject, Base, Model):
    __tablename__ = "offer_validation_sub_rule"
    validationRule: sa_orm.Mapped["OfferValidationRule"] = sa_orm.relationship(
        "OfferValidationRule", backref="subRules", order_by="OfferValidationSubRule.id.asc()"
    )
    validationRuleId = sa.Column(sa.BigInteger, sa.ForeignKey("offer_validation_rule.id"), index=True, nullable=False)
    model: OfferValidationModel = sa.Column(sa.Enum(OfferValidationModel), nullable=True)
    __table_args__ = (
        sa.CheckConstraint(
            "(model IS NULL AND attribute = 'CLASS_NAME') OR (model IS NOT NULL AND attribute != 'CLASS_NAME')",
            name="check_not_model_and_attribute_class_or_vice_versa",
        ),
    )
    attribute: OfferValidationAttribute = sa.Column(sa.Enum(OfferValidationAttribute), nullable=False)
    operator: OfferValidationRuleOperator = sa.Column(sa.Enum(OfferValidationRuleOperator), nullable=False)
    comparated: dict = sa.Column("comparated", MutableDict.as_mutable(postgresql.json.JSONB), nullable=False)


class OfferValidationRule(PcObject, Base, Model, DeactivableMixin):
    __tablename__ = "offer_validation_rule"
    name: str = sa.Column(sa.Text, nullable=False)
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


class OfferPriceLimitationRule(PcObject, Base, Model):
    __tablename__ = "offer_price_limitation_rule"
    subcategoryId: str = sa.Column(sa.Text, nullable=False, unique=True)
    rate: decimal.Decimal = sa.Column(sa.Numeric(5, 4), nullable=False)


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


class OfferReport(PcObject, Base, Model):
    __tablename__ = "offer_report"

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

    user: sa_orm.Mapped["User"] = sa_orm.relationship("User", backref="reported_offers")
    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=False)
    offer: sa_orm.Mapped["Offer"] = sa_orm.relationship("Offer", backref="reports")
    offerId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id"), index=True, nullable=False)
    reason: Reason = sa.Column(sa.Enum(Reason, create_constraint=False), nullable=False, index=True)
    reportedAt: datetime.datetime = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())
    # If the reason code is OTHER, save the user's custom reason
    customReasonContent = sa.Column(sa.Text, nullable=True)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}#{self.id} userId={self.userId}, offerId={self.offerId}, when={self.when}"


class BookMacroSection(PcObject, Base, Model):
    __tablename__ = "book_macro_section"

    macroSection: str = sa.Column(sa.Text, nullable=False)
    section: str = sa.Column(sa.Text, nullable=False)

    __table_args__ = (sa.Index("book_macro_section_section_idx", sa.func.lower(section), unique=True),)


class PriceCategoryLabel(PcObject, Base, Model):
    __tablename__ = "price_category_label"
    label: str = sa.Column(sa.Text(), nullable=False)
    priceCategories: sa_orm.Mapped[list["PriceCategory"]] = sa_orm.relationship(
        "PriceCategory", back_populates="priceCategoryLabel"
    )
    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), index=True, nullable=False)
    venue: sa_orm.Mapped["Venue"] = sa_orm.relationship("Venue", back_populates="priceCategoriesLabel")

    __table_args__ = (
        sa.UniqueConstraint(
            "label",
            "venueId",
            name="unique_label_venue",
        ),
    )


class PriceCategory(PcObject, Base, Model):
    __tablename__ = "price_category"
    offerId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), index=True, nullable=False)
    offer: sa_orm.Mapped["Offer"] = sa_orm.relationship("Offer", back_populates="priceCategories")
    price: decimal.Decimal = sa.Column(
        sa.Numeric(10, 2), sa.CheckConstraint("price >= 0", name="check_price_is_not_negative"), nullable=False
    )
    priceCategoryLabelId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("price_category_label.id"), index=True, nullable=False
    )
    priceCategoryLabel: sa_orm.Mapped["PriceCategoryLabel"] = sa_orm.relationship(
        "PriceCategoryLabel", foreign_keys=[priceCategoryLabelId], back_populates="priceCategories"
    )
    stocks: sa_orm.Mapped[list["Stock"]] = relationship("Stock", back_populates="priceCategory", cascade="all")
    idAtProvider = sa.Column(sa.Text, nullable=True)

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


class TiteliveGtlMapping(PcObject, Base, Model):
    __tablename__ = "titelive_gtl_mapping"

    gtlType: TiteliveGtlType = sa.Column(sa.Enum(TiteliveGtlType), nullable=False)
    gtlId: str = sa.Column(sa.Text, nullable=True, unique=False, index=True)
    gtlLabelLevel1: str = sa.Column(sa.Text, nullable=True, unique=False)
    gtlLabelLevel2: str = sa.Column(sa.Text, nullable=True, unique=False)
    gtlLabelLevel3: str = sa.Column(sa.Text, nullable=True, unique=False)
    gtlLabelLevel4: str = sa.Column(sa.Text, nullable=True, unique=False)

    sa.Index("gtl_type_idx", gtlType, postgresql_using="hash")


@dataclass
class Movie:
    allocine_id: str | None
    description: str | None
    duration: int | None
    poster_url: str | None
    visa: str | None
    title: str
    extra_data: OfferExtraData | None


class OfferCompliance(PcObject, Base, Model):
    __tablename__ = "offer_compliance"
    offerId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), index=True, nullable=False, unique=True
    )
    offer: sa_orm.Mapped["Offer"] = sa_orm.relationship("Offer", back_populates="compliance")
    # Compliance_score is a score between 0 and 100. Keep it small with a smallint
    compliance_score: int = sa.Column(sa.SmallInteger, nullable=False)
    compliance_reasons: sa_orm.Mapped[list[str]] = sa.Column(
        MutableList.as_mutable(postgresql.ARRAY(sa.String)), nullable=False
    )
