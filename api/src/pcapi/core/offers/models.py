from dataclasses import dataclass
import datetime
import decimal
import enum
import logging
import typing

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlalchemy.exc as sa_exc
from sqlalchemy.ext import mutable as sa_mutable
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
import sqlalchemy.orm as sa_orm
from sqlalchemy.orm import relationship
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.elements import BooleanClauseList
from sqlalchemy.sql.elements import Case
from sqlalchemy.sql.elements import UnaryExpression

import pcapi.core.bookings.constants as bookings_constants
from pcapi.core.categories import categories
from pcapi.core.categories import subcategories_v2
from pcapi.core.providers.models import VenueProvider
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.accessibility_mixin import AccessibilityMixin
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.has_thumb_mixin import HasThumbMixin
from pcapi.models.offer_mixin import OfferStatus
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import ValidationMixin
from pcapi.models.pc_object import PcObject
from pcapi.models.providable_mixin import ProvidableMixin
from pcapi.models.soft_deletable_mixin import SoftDeletableMixin
from pcapi.utils.date import METROPOLE_TIMEZONE
from pcapi.utils.db import MagicEnum


logger = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    from pcapi.core.bookings.models import Booking
    from pcapi.core.criteria.models import Criterion
    from pcapi.core.educational.models import CollectiveOffer
    from pcapi.core.educational.models import CollectiveOfferTemplate
    from pcapi.core.offerers.models import Offerer
    from pcapi.core.offerers.models import OffererAddress
    from pcapi.core.offerers.models import Venue
    from pcapi.core.providers.models import Provider
    from pcapi.core.users.models import User


UNRELEASED_OR_UNAVAILABLE_BOOK_MARKER = "xxx"


class OfferExtraData(typing.TypedDict, total=False):
    artist: str | None
    author: str | None
    complianceScore: int | None
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


class TiteliveImageType(enum.Enum):
    RECTO = "recto"
    VERSO = "verso"


class ProductMediation(PcObject, Base, Model, ProvidableMixin):
    __tablename__ = "product_mediation"

    productId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("product.id", ondelete="CASCADE"), index=True, nullable=False
    )
    url: str = sa.Column(sa.String(255), nullable=False, unique=True)
    imageType = sa.Column(sa.Enum(TiteliveImageType), nullable=False)


class GcuCompatibilityType(enum.Enum):
    COMPATIBLE = "COMPATIBLE"
    PROVIDER_INCOMPATIBLE = "PROVIDER_INCOMPATIBLE"
    FRAUD_INCOMPATIBLE = "FRAUD_INCOMPATIBLE"


class Product(PcObject, Base, Model, HasThumbMixin, ProvidableMixin):
    description = sa.Column(sa.Text, nullable=True)
    durationMinutes = sa.Column(sa.Integer, nullable=True)
    extraData: OfferExtraData | None = sa.Column("jsonData", sa_mutable.MutableDict.as_mutable(postgresql.JSONB))
    gcuCompatibilityType = sa.Column(
        MagicEnum(GcuCompatibilityType),
        nullable=False,
        default=GcuCompatibilityType.COMPATIBLE,
        server_default=GcuCompatibilityType.COMPATIBLE.value,
    )
    last_30_days_booking = sa.Column(sa.Integer, nullable=True)
    name: str = sa.Column(sa.String(140), nullable=False)
    subcategoryId: str = sa.Column(sa.Text, nullable=False, index=True)
    thumb_path_component = "products"
    productMediations: sa_orm.Mapped[ProductMediation] = sa.orm.relationship(
        "ProductMediation",
        backref="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    sa.Index("product_ean_idx", extraData["ean"].astext)
    sa.Index("product_allocineId_idx", extraData["allocineId"].cast(sa.Integer))
    sa.Index("product_visa_idx", extraData["visa"].astext)

    @property
    def subcategory(self) -> subcategories_v2.Subcategory:
        if self.subcategoryId not in subcategories_v2.ALL_SUBCATEGORIES_DICT:
            raise ValueError(f"Unexpected subcategoryId '{self.subcategoryId}' for product {self.id}")
        return subcategories_v2.ALL_SUBCATEGORIES_DICT[self.subcategoryId]

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
                "recto": next(
                    (pm.url for pm in self.productMediations if pm.imageType == TiteliveImageType.RECTO), None
                ),
                "verso": next(
                    (pm.url for pm in self.productMediations if pm.imageType == TiteliveImageType.VERSO), None
                ),
            }
        return {"recto": self.thumbUrl}


class Mediation(PcObject, Base, Model, HasThumbMixin, ProvidableMixin, DeactivableMixin):
    __tablename__ = "mediation"

    author: sa_orm.Mapped["User"] | None = sa.orm.relationship("User", backref="mediations")
    authorId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    credit = sa.Column(sa.String(255), nullable=True)
    dateCreated: datetime.datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    offer: sa_orm.Mapped["Offer"] = sa.orm.relationship("Offer", backref="mediations")
    offerId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id"), index=True, nullable=False)
    thumb_path_component = "mediations"


class Stock(PcObject, Base, Model, ProvidableMixin, SoftDeletableMixin):
    __tablename__ = "stock"

    MAX_STOCK_QUANTITY = 1_000_000

    activationCodes: sa_orm.Mapped["ActivationCode"] = sa.orm.relationship("ActivationCode", back_populates="stock")
    beginningDatetime: datetime.datetime | None = sa.Column(sa.DateTime, nullable=True)
    bookingLimitDatetime = sa.Column(sa.DateTime, nullable=True)
    dateCreated: datetime.datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.datetime.utcnow, server_default=sa.func.now()
    )
    dateModified: datetime.datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    dnBookedQuantity: int = sa.Column(sa.BigInteger, nullable=False, server_default=sa.text("0"))
    offer: sa_orm.Mapped["Offer"] = sa.orm.relationship("Offer", backref="stocks")
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
    priceCategory: sa_orm.Mapped["PriceCategory | None"] = sa.orm.relationship("PriceCategory", back_populates="stocks")
    quantity: int | None = sa.Column(sa.Integer, nullable=True)
    # FIXME: mageoffray (2024-01-05) : remove this column when Provider API is not used anymore
    rawProviderQuantity = sa.Column(sa.Integer, nullable=True)
    features: list[str] = sa.Column(postgresql.ARRAY(sa.Text), nullable=False, server_default=sa.text("'{}'::text[]"))
    offererAddressId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offerer_address.id"), nullable=True)
    offererAddress: sa.orm.Mapped["OffererAddress"] = sa.orm.relationship(
        "OffererAddress", foreign_keys=[offererAddressId], uselist=False
    )
    sa.Index("ix_stock_offererAddressId", offererAddressId, postgresql_where=offererAddressId.is_not(None))

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
    def _bookable(cls) -> BooleanClauseList:  # pylint: disable=no-self-argument
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
    def hasBookingLimitDatetimePassed(cls) -> BooleanClauseList:  # pylint: disable=no-self-argument
        return sa.and_(cls.bookingLimitDatetime.is_not(None), cls.bookingLimitDatetime <= sa.func.now())

    # TODO(fseguin, 2021-03-25): replace unlimited by None (also in the front-end)
    @hybrid_property
    def remainingQuantity(self) -> int | str:
        return "unlimited" if self.quantity is None else self.quantity - self.dnBookedQuantity

    @remainingQuantity.expression  # type: ignore[no-redef]
    def remainingQuantity(cls) -> Case:  # pylint: disable=no-self-argument
        return sa.case((cls.quantity.is_(None), None), else_=(cls.quantity - cls.dnBookedQuantity))

    AUTOMATICALLY_USED_SUBCATEGORIES = [
        subcategories_v2.CARTE_MUSEE.id,
        subcategories_v2.ABO_BIBLIOTHEQUE.id,
        subcategories_v2.ABO_MEDIATHEQUE.id,
    ]

    @property
    def is_automatically_used(self) -> bool:
        return self.offer.subcategoryId in self.AUTOMATICALLY_USED_SUBCATEGORIES and not self.price

    @hybrid_property
    def isEventExpired(self) -> bool:
        return bool(self.beginningDatetime and self.beginningDatetime <= datetime.datetime.utcnow())

    @isEventExpired.expression  # type: ignore[no-redef]
    def isEventExpired(cls) -> BooleanClauseList:  # pylint: disable=no-self-argument
        return sa.and_(cls.beginningDatetime.is_not(None), cls.beginningDatetime <= sa.func.now())

    @hybrid_property
    def isExpired(self) -> bool:
        return self.isEventExpired or self.hasBookingLimitDatetimePassed

    @isExpired.expression  # type: ignore[no-redef]
    def isExpired(cls) -> BooleanClauseList:  # pylint: disable=no-self-argument
        return sa.or_(cls.isEventExpired, cls.hasBookingLimitDatetimePassed)

    @property
    def isEventDeletable(self) -> bool:
        if not self.beginningDatetime or self.offer.validation == OfferValidationStatus.DRAFT:
            return True
        limit_date_for_stock_deletion = self.beginningDatetime + bookings_constants.AUTO_USE_AFTER_EVENT_TIME_DELAY
        return limit_date_for_stock_deletion >= datetime.datetime.utcnow()

    @hybrid_property
    def isSoldOut(self) -> bool:
        # pylint: disable=comparison-with-callable
        return (
            self.isSoftDeleted
            or (self.beginningDatetime is not None and self.beginningDatetime <= datetime.datetime.utcnow())
            or (self.remainingQuantity != "unlimited" and self.remainingQuantity <= 0)
        )

    @isSoldOut.expression  # type: ignore[no-redef]
    def isSoldOut(cls) -> BooleanClauseList:  # pylint: disable=no-self-argument
        return sa.or_(
            cls.isSoftDeleted,
            sa.and_(sa.not_(cls.beginningDatetime.is_(None)), cls.beginningDatetime <= sa.func.now()),
            sa.and_(
                sa.not_(cls.remainingQuantity.is_(None)),
                cls.remainingQuantity <= 0,  # pylint: disable=comparison-with-callable
            ),
        )

    @classmethod
    def queryNotSoftDeleted(cls) -> BaseQuery:
        return Stock.query.filter_by(isSoftDeleted=False)

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
    def remainingStock(cls) -> Case:  # pylint: disable=no-self-argument
        return sa.case((cls._bookable, cls.remainingQuantity), else_=0)


@sa.event.listens_for(Stock, "before_insert")
def before_insert(mapper: sa.orm.Mapper, configuration: sa.engine.Connection, self: Stock) -> None:
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


class Offer(PcObject, Base, Model, DeactivableMixin, ValidationMixin, AccessibilityMixin):
    __tablename__ = "offer"

    MAX_STOCKS_PER_OFFER = 2_500

    authorId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=True)
    author: sa_orm.Mapped["User"] | None = relationship(
        "User", backref="offers", foreign_keys=[authorId], uselist=False
    )
    bookingContact = sa.Column(sa.String(120), nullable=True)
    bookingEmail = sa.Column(sa.String(120), nullable=True)
    criteria: sa_orm.Mapped["Criterion"] = sa.orm.relationship(
        "Criterion", backref=db.backref("criteria", lazy="dynamic"), secondary="offer_criterion"
    )
    dateCreated: datetime.datetime = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    dateModifiedAtLastProvider = sa.Column(sa.DateTime, nullable=True, default=datetime.datetime.utcnow)
    dateUpdated: datetime.datetime = sa.Column(
        sa.DateTime, nullable=True, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    description = sa.Column(sa.Text, nullable=True)
    durationMinutes = sa.Column(sa.Integer, nullable=True)
    externalTicketOfficeUrl = sa.Column(sa.String, nullable=True)
    extraData: OfferExtraData | None = sa.Column("jsonData", sa_mutable.MutableDict.as_mutable(postgresql.JSONB))
    fieldsUpdated: list[str] = sa.Column(
        postgresql.ARRAY(sa.String(100)), nullable=False, default=[], server_default="{}"
    )
    flaggingValidationRules: list["OfferValidationRule"] = sa.orm.relationship(
        "OfferValidationRule", secondary="validation_rule_offer_link", back_populates="offers"
    )

    lastProviderId = sa.Column(sa.BigInteger, sa.ForeignKey("provider.id"), nullable=True)
    lastProvider: "Provider|None" = sa.orm.relationship("Provider", foreign_keys=[lastProviderId])
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
    priceCategories: sa_orm.Mapped[list["PriceCategory"]] = sa.orm.relationship("PriceCategory", back_populates="offer")
    product: Product = sa.orm.relationship(Product, backref="offers")
    productId: int = sa.Column(sa.BigInteger, sa.ForeignKey("product.id"), index=True, nullable=True)
    rankingWeight = sa.Column(sa.Integer, nullable=True)
    subcategoryId: str = sa.Column(sa.Text, nullable=False, index=True)
    url = sa.Column(sa.String(255), nullable=True)
    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), nullable=False, index=True)
    venue: sa_orm.Mapped["Venue"] = sa.orm.relationship("Venue", foreign_keys=[venueId], backref="offers")
    withdrawalDelay = sa.Column(sa.BigInteger, nullable=True)
    withdrawalDetails = sa.Column(sa.Text, nullable=True)
    withdrawalType = sa.Column(sa.Enum(WithdrawalTypeEnum), nullable=True)
    offererAddressId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offerer_address.id"), nullable=True)
    offererAddress: sa_orm.Mapped["OffererAddress"] = sa_orm.relationship(
        "OffererAddress", foreign_keys=[offererAddressId], uselist=False
    )

    sa.Index("idx_offer_trgm_name", name, postgresql_using="gin")
    sa.Index("offer_idAtProvider", idAtProvider)
    sa.Index("offer_ean_idx", extraData["ean"].astext)
    sa.Index("offer_visa_idx", extraData["visa"].astext)
    sa.Index("offer_music_type_idx", extraData["musicType"].astext, postgresql_where=extraData["musicType"] is not None)
    sa.Index(
        "offer_music_sub_type_idx",
        extraData["musicSubType"].astext,
        postgresql_where=extraData["musicSubType"] is not None,
    )
    sa.Index("offer_show_type_idx", extraData["showType"].astext, postgresql_where=extraData["showType"] is not None)
    sa.Index(
        "offer_show_sub_type_idx",
        extraData["showSubType"].astext,
        postgresql_where=extraData["showSubType"] is not None,
    )
    sa.Index("offer_authorId_idx", authorId, postgresql_using="btree")
    sa.Index("ix_offer_lastProviderId", lastProviderId, postgresql_where=lastProviderId.is_not(None))

    # FIXME: We should be able to remove the index on `venueId`, since this composite index
    #  can be used by PostgreSQL when filtering on the `venueId` column only.
    sa.Index("venueId_idAtProvider_index", venueId, idAtProvider, unique=True)

    sa.Index("ix_offer_offererAddressId", offererAddressId, postgresql_where=offererAddressId.is_not(None))
    isNonFreeOffer: sa_orm.Mapped["bool"] = sa_orm.query_expression()
    bookingsCount: sa_orm.Mapped["int"] = sa_orm.query_expression()

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
    def isSoldOut(cls) -> UnaryExpression:  # pylint: disable=no-self-argument
        return (
            ~sa.exists()
            .where(Stock.offerId == cls.id)
            .where(Stock.isSoftDeleted.is_(False))
            .where(sa.or_(Stock.beginningDatetime > sa.func.now(), Stock.beginningDatetime.is_(None)))
            .where(sa.or_(Stock.remainingQuantity.is_(None), Stock.remainingQuantity > 0))
        )

    @property
    def activeMediation(self) -> Mediation | None:
        sorted_by_date_desc = sorted(self.mediations, key=lambda m: m.dateCreated, reverse=True)
        only_active = list(filter(lambda m: m.isActive, sorted_by_date_desc))
        return only_active[0] if only_active else None

    @hybrid_property
    def canExpire(self) -> bool:
        return self.subcategoryId in subcategories_v2.EXPIRABLE_SUBCATEGORIES

    @canExpire.expression  # type: ignore[no-redef]
    def canExpire(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.subcategoryId.in_(subcategories_v2.EXPIRABLE_SUBCATEGORIES)

    @property
    def isReleased(self) -> bool:
        offerer = self.venue.managingOfferer
        return self._released and offerer.isActive and offerer.isValidated

    @hybrid_property
    def _released(self) -> bool:
        return self.isActive and self.validation == OfferValidationStatus.APPROVED

    @_released.expression  # type: ignore[no-redef]
    def _released(cls) -> BooleanClauseList:  # pylint: disable=no-self-argument
        return sa.and_(cls.isActive, cls.validation == OfferValidationStatus.APPROVED)

    @hybrid_property
    def isPermanent(self) -> bool:
        return self.subcategoryId in subcategories_v2.PERMANENT_SUBCATEGORIES

    @isPermanent.expression  # type: ignore[no-redef]
    def isPermanent(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.subcategoryId.in_(subcategories_v2.PERMANENT_SUBCATEGORIES)

    @hybrid_property
    def isEvent(self) -> bool:
        return self.subcategory.is_event

    @isEvent.expression  # type: ignore[no-redef]
    def isEvent(cls) -> BinaryExpression:  # pylint: disable=no-self-argument
        return cls.subcategoryId.in_(subcategories_v2.EVENT_SUBCATEGORIES)

    @property
    def isThing(self) -> bool:
        return not self.subcategory.is_event

    @hybrid_property
    def isDigital(self) -> bool:
        return self.url is not None and self.url != ""

    @isDigital.expression  # type: ignore[no-redef]
    def isDigital(cls) -> BooleanClauseList:  # pylint: disable=no-self-argument
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
        return self.isReleased and self.isBookable

    @is_eligible_for_search.expression  # type: ignore[no-redef]
    def is_eligible_for_search(cls) -> BooleanClauseList:  # pylint: disable=no-self-argument
        return sa.and_(cls._released, Stock._bookable)

    @hybrid_property
    def is_offer_released_with_bookable_stock(self) -> bool:
        return self.isReleased and self.isBookable

    @is_offer_released_with_bookable_stock.expression  # type: ignore[no-redef]
    def is_offer_released_with_bookable_stock(cls) -> BooleanClauseList:  # pylint: disable=no-self-argument
        return sa.and_(cls._released, sa.exists().where(Stock.offerId == cls.id).where(Stock._bookable))

    @hybrid_property
    def hasBookingLimitDatetimesPassed(self) -> bool:
        if self.activeStocks:
            return all(stock.hasBookingLimitDatetimePassed for stock in self.activeStocks)
        return False

    @hasBookingLimitDatetimesPassed.expression  # type: ignore[no-redef]
    def hasBookingLimitDatetimesPassed(cls) -> BooleanClauseList:  # pylint: disable=no-self-argument
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
    def firstBeginningDatetime(cls) -> datetime.datetime | None:  # pylint: disable=no-self-argument
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
    def is_forbidden_to_underage(self) -> bool:
        return all(stock.is_forbidden_to_underage for stock in self.bookableStocks)

    @property
    def subcategory(self) -> subcategories_v2.Subcategory:
        if self.subcategoryId not in subcategories_v2.ALL_SUBCATEGORIES_DICT:
            raise ValueError(f"Unexpected subcategoryId (v2) '{self.subcategoryId}' for offer {self.id}")
        return subcategories_v2.ALL_SUBCATEGORIES_DICT[self.subcategoryId]

    @property
    def category(self) -> categories.Category:
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
                return {"recto": OfferImage(url, activeMediation.credit)}

        product_images = self.product.images if self.product else None
        if product_images is None:
            return None
        images = {}
        if product_images.get("recto"):
            images["recto"] = OfferImage(product_images.get("recto"), credit=None)
        if product_images.get("verso"):
            images["verso"] = OfferImage(product_images.get("verso"), credit=None)
        if images:
            return images
        return None

    @property
    def image(self) -> OfferImage | None:
        if self.images:
            return self.images.get("recto") if self.images.get("recto") else self.images.get("verso")
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
    def is_expired(cls) -> UnaryExpression:  # pylint: disable=no-self-argument
        return cls.hasBookingLimitDatetimesPassed

    @hybrid_property
    def status(self) -> OfferStatus:
        if self.validation == OfferValidationStatus.REJECTED:
            return OfferStatus.REJECTED

        if self.validation == OfferValidationStatus.PENDING:
            return OfferStatus.PENDING

        if self.validation == OfferValidationStatus.DRAFT:
            return OfferStatus.DRAFT

        if not self.isActive:
            return OfferStatus.INACTIVE

        if self.validation == OfferValidationStatus.APPROVED:
            if self.hasBookingLimitDatetimesPassed:  # pylint: disable=using-constant-test
                return OfferStatus.EXPIRED
            if self.isSoldOut:  # pylint: disable=using-constant-test
                return OfferStatus.SOLD_OUT

        return OfferStatus.ACTIVE

    @status.expression  # type: ignore[no-redef]
    def status(cls) -> Case:  # pylint: disable=no-self-argument
        return sa.case(
            (cls.validation == OfferValidationStatus.REJECTED.name, OfferStatus.REJECTED.name),
            (cls.validation == OfferValidationStatus.PENDING.name, OfferStatus.PENDING.name),
            (cls.validation == OfferValidationStatus.DRAFT.name, OfferStatus.DRAFT.name),
            (cls.isActive.is_(False), OfferStatus.INACTIVE.name),
            (cls.hasBookingLimitDatetimesPassed.is_(True), OfferStatus.EXPIRED.name),
            (cls.isSoldOut.is_(True), OfferStatus.SOLD_OUT.name),
            else_=OfferStatus.ACTIVE.name,
        )

    @property
    def isActivable(self) -> bool:
        if self.status == OfferStatus.REJECTED:
            return False
        if (
            self.lastProviderId
            and not VenueProvider.query.filter_by(
                isActive=True,
                venueId=self.venueId,
                providerId=self.lastProviderId,
            ).one_or_none()
        ):
            return False
        return True


class ActivationCode(PcObject, Base, Model):
    __tablename__ = "activation_code"

    booking: sa.orm.Mapped["Booking | None"] = sa.orm.relationship("Booking", back_populates="activationCode")
    bookingId = sa.Column(sa.BigInteger, sa.ForeignKey("booking.id"), index=True, nullable=True)
    code: str = sa.Column(sa.Text, nullable=False)
    expirationDate = sa.Column(sa.DateTime, nullable=True, default=None)
    stock: sa.orm.Mapped["Stock"] = sa.orm.relationship("Stock", back_populates="activationCodes")
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
    validationRule: sa.orm.Mapped["OfferValidationRule"] = sa.orm.relationship(
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
    offers: list["Offer"] = sa.orm.relationship(
        "Offer", secondary="validation_rule_offer_link", back_populates="flaggingValidationRules"
    )
    collectiveOffers: list["CollectiveOffer"] = sa.orm.relationship(
        "CollectiveOffer", secondary="validation_rule_collective_offer_link", back_populates="flaggingValidationRules"
    )
    collectiveOfferTemplates: list["CollectiveOfferTemplate"] = sa.orm.relationship(
        "CollectiveOfferTemplate",
        secondary="validation_rule_collective_offer_template_link",
        back_populates="flaggingValidationRules",
    )


class ValidationRuleOfferLink(PcObject, Base, Model):
    __tablename__ = "validation_rule_offer_link"
    ruleId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("offer_validation_rule.id", ondelete="CASCADE"), nullable=False
    )
    offerId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), index=True, nullable=False)


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

    user: sa.orm.Mapped["User"] = sa.orm.relationship("User", backref="reported_offers")
    userId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=False)
    offer: sa.orm.Mapped["Offer"] = sa.orm.relationship("Offer", backref="reports")
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
    label: str = sa.Column(sa.Text(), nullable=False)
    priceCategory: sa_orm.Mapped["PriceCategory"] = sa.orm.relationship(
        "PriceCategory", back_populates="priceCategoryLabel"
    )
    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), index=True, nullable=False)
    venue: sa_orm.Mapped["Venue"] = sa.orm.relationship("Venue", back_populates="priceCategoriesLabel")

    __table_args__ = (
        sa.UniqueConstraint(
            "label",
            "venueId",
            name="unique_label_venue",
        ),
    )


class PriceCategory(PcObject, Base, Model):
    offerId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), index=True, nullable=False)
    offer: sa_orm.Mapped["Offer"] = sa.orm.relationship("Offer", back_populates="priceCategories")
    price: decimal.Decimal = sa.Column(
        sa.Numeric(10, 2), sa.CheckConstraint("price >= 0", name="check_price_is_not_negative"), nullable=False
    )
    priceCategoryLabelId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("price_category_label.id"), index=True, nullable=False
    )
    priceCategoryLabel: sa_orm.Mapped["PriceCategoryLabel"] = sa.orm.relationship(
        "PriceCategoryLabel", back_populates="priceCategory"
    )
    stocks: sa_orm.Mapped[list["Stock"]] = relationship("Stock", back_populates="priceCategory", cascade="all")

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


class OfferAddress(PcObject, Base, Model):
    __tablename__ = "offer_address"

    offerId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), nullable=False, index=True)
    offer: sa_orm.Mapped["Offer"] = sa.orm.relationship("Offer", backref="address")
    # address specific columns
    banId: str | None = sa.Column(sa.Text(), nullable=True)
    inseeCode: str | None = sa.Column(sa.Text(), nullable=True)
    street: str | None = sa.Column(sa.Text(), nullable=True)
    postalCode: str = sa.Column(sa.Text(), nullable=False)
    city: str = sa.Column(sa.Text(), nullable=False)
    latitude: float = sa.Column(sa.Numeric(8, 5), nullable=False)
    longitude: float = sa.Column(sa.Numeric(8, 5), nullable=False)
    departmentCode = sa.Column(sa.Text(), nullable=True, index=True)
    timezone = sa.Column(sa.Text(), nullable=False, default=METROPOLE_TIMEZONE, server_default=METROPOLE_TIMEZONE)

    __table_args__ = (
        sa.Index(
            "ix_partial_unique_address_per_street_and_insee_code_oa",
            "street",
            "inseeCode",
            unique=True,
            postgresql_where=sa.and_(street.is_not(None), inseeCode.is_not(None)),
        ),
        sa.CheckConstraint('length("postalCode") = 5'),
        sa.CheckConstraint('length("inseeCode") = 5'),
        sa.CheckConstraint('length("city") <= 50'),
        sa.CheckConstraint('length("departmentCode") = 2 OR length("departmentCode") = 3'),
        sa.CheckConstraint('length("timezone") <= 50'),
    )
