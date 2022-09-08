from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
import enum
import logging
from typing import TYPE_CHECKING
from typing import Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlalchemy.orm as sa_orm
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship
from sqlalchemy.sql.elements import BooleanClauseList
from sqlalchemy.sql.elements import Case
from sqlalchemy.sql.elements import UnaryExpression

import pcapi.core.bookings.constants as bookings_constants
from pcapi.core.categories import categories
from pcapi.core.categories import subcategories
from pcapi.core.categories import subcategories_v2
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.accessibility_mixin import AccessibilityMixin
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.extra_data_mixin import ExtraDataMixin
from pcapi.models.has_thumb_mixin import HasThumbMixin
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import StatusMixin
from pcapi.models.offer_mixin import ValidationMixin
from pcapi.models.pc_object import PcObject
from pcapi.models.providable_mixin import ProvidableMixin
from pcapi.models.soft_deletable_mixin import SoftDeletableMixin
from pcapi.utils.date import DateTimes


logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pcapi.core.users.models import User


class BookFormat(enum.Enum):
    REVUE = "REVUE"
    BANDE_DESSINEE = "BANDE DESSINEE "
    BEAUX_LIVRES = "BEAUX LIVRES"
    POCHE = "POCHE"
    LIVRE_CASSETTE = "LIVRE + CASSETTE"
    LIVRE_AUDIO = "LIVRE + CD AUDIO"
    MOYEN_FORMAT = "MOYEN FORMAT"


UNRELEASED_OR_UNAVAILABLE_BOOK_MARKER = "xxx"


class Product(PcObject, Base, Model, ExtraDataMixin, HasThumbMixin, ProvidableMixin):  # type: ignore [valid-type, misc]
    name: str = sa.Column(sa.String(140), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    conditions = sa.Column(sa.String(120), nullable=True)
    ageMin = sa.Column(sa.Integer, nullable=True)
    ageMax = sa.Column(sa.Integer, nullable=True)
    # FIXME (cgaunet, 2022-08-02): this field seems to be unused
    mediaUrls = sa.Column(postgresql.ARRAY(sa.String(220)), nullable=False, default=[])
    url = sa.Column(sa.String(255), nullable=True)
    durationMinutes = sa.Column(sa.Integer, nullable=True)
    isGcuCompatible = sa.Column(sa.Boolean, default=True, server_default=sa.true(), nullable=False)
    isSynchronizationCompatible = sa.Column(sa.Boolean, default=True, server_default=sa.true(), nullable=False)
    isNational = sa.Column(sa.Boolean, server_default=sa.false(), default=False, nullable=False)
    owningOffererId = sa.Column(sa.BigInteger, sa.ForeignKey("offerer.id"), nullable=True)
    owningOfferer = sa_orm.relationship("Offerer", foreign_keys=[owningOffererId], backref="events")  # type: ignore [misc]
    subcategoryId = sa.Column(sa.Text, nullable=False, index=True)

    sa.Index("product_isbn_idx", ExtraDataMixin.extraData["isbn"].astext)

    thumb_path_component = "products"

    @property
    def subcategory(self) -> subcategories.Subcategory:
        if self.subcategoryId not in subcategories.ALL_SUBCATEGORIES_DICT:
            raise ValueError(f"Unexpected subcategoryId '{self.subcategoryId}' for product {self.id}")
        return subcategories.ALL_SUBCATEGORIES_DICT[self.subcategoryId]

    @property
    def isDigital(self) -> bool:
        return self.url is not None and self.url != ""

    @property
    def is_offline_only(self) -> bool:
        return self.subcategory.online_offline_platform == subcategories.OnlineOfflinePlatformChoices.OFFLINE.value

    @property
    def is_online_only(self) -> bool:
        return self.subcategory.online_offline_platform == subcategories.OnlineOfflinePlatformChoices.ONLINE.value

    @sa.ext.hybrid.hybrid_property
    def can_be_synchronized(self) -> bool:
        return (
            self.isGcuCompatible  # type: ignore [operator]
            & self.isSynchronizationCompatible
            & (self.name != UNRELEASED_OR_UNAVAILABLE_BOOK_MARKER)
        )


class Mediation(PcObject, Base, Model, HasThumbMixin, ProvidableMixin, DeactivableMixin):  # type: ignore [valid-type, misc]
    __tablename__ = "mediation"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    credit = sa.Column(sa.String(255), nullable=True)

    dateCreated = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)

    authorId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=True)

    author = sa.orm.relationship("User", foreign_keys=[authorId], backref="mediations")  # type: ignore [misc]

    offerId = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id"), index=True, nullable=False)

    offer = sa.orm.relationship("Offer", foreign_keys=[offerId], backref="mediations")  # type: ignore [misc]

    thumb_path_component = "mediations"


class Stock(PcObject, Base, Model, ProvidableMixin, SoftDeletableMixin):  # type: ignore [valid-type, misc]
    __tablename__ = "stock"

    dateCreated = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow, server_default=sa.func.now())

    dateModified = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)

    beginningDatetime = sa.Column(sa.DateTime, index=True, nullable=True)

    offerId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id"), index=True, nullable=False)

    offer = sa.orm.relationship("Offer", foreign_keys=[offerId], backref="stocks")  # type: ignore [misc]

    price = sa.Column(
        sa.Numeric(10, 2), sa.CheckConstraint("price >= 0", name="check_price_is_not_negative"), nullable=False
    )

    quantity = sa.Column(sa.Integer, nullable=True)

    bookingLimitDatetime = sa.Column(sa.DateTime, nullable=True)

    dnBookedQuantity: int = sa.Column(sa.BigInteger, nullable=False, server_default=sa.text("0"))

    rawProviderQuantity = sa.Column(sa.Integer, nullable=True)

    activationCodes = sa.orm.relationship("ActivationCode", back_populates="stock")  # type: ignore [misc]

    numberOfTickets = sa.Column(sa.Integer, nullable=True)

    educationalPriceDetail = sa.Column(sa.Text, nullable=True)

    @property
    def isBookable(self):  # type: ignore [no-untyped-def]
        return self._bookable and self.offer.isReleased

    @sa.ext.hybrid.hybrid_property
    def _bookable(self) -> bool:
        return not self.isExpired and not self.isSoldOut

    @_bookable.expression  # type: ignore [no-redef]
    def _bookable(cls) -> BooleanClauseList:  # pylint: disable=no-self-argument
        return sa.and_(sa.not_(cls.isExpired), sa.not_(cls.isSoldOut))

    @property
    def is_forbidden_to_underage(self):  # type: ignore [no-untyped-def]
        return (self.price > 0 and not self.offer.subcategory.is_bookable_by_underage_when_not_free) or (
            self.price == 0 and not self.offer.subcategory.is_bookable_by_underage_when_free
        )

    @sa.ext.hybrid.hybrid_property
    def hasBookingLimitDatetimePassed(self) -> bool:
        return bool(self.bookingLimitDatetime and self.bookingLimitDatetime <= datetime.utcnow())

    @hasBookingLimitDatetimePassed.expression  # type: ignore [no-redef]
    def hasBookingLimitDatetimePassed(cls) -> BooleanClauseList:  # pylint: disable=no-self-argument
        return sa.and_(cls.bookingLimitDatetime != None, cls.bookingLimitDatetime <= sa.func.now())

    # TODO(fseguin, 2021-03-25): replace unlimited by None (also in the front-end)
    @sa.ext.hybrid.hybrid_property
    def remainingQuantity(self) -> Union[int, str]:
        return "unlimited" if self.quantity is None else self.quantity - self.dnBookedQuantity

    @remainingQuantity.expression  # type: ignore [no-redef]
    def remainingQuantity(cls) -> Case:  # pylint: disable=no-self-argument
        return sa.case([(cls.quantity.is_(None), None)], else_=(cls.quantity - cls.dnBookedQuantity))

    @sa.ext.hybrid.hybrid_property
    def isEventExpired(self) -> bool:
        return bool(self.beginningDatetime and self.beginningDatetime <= datetime.utcnow())

    @isEventExpired.expression  # type: ignore [no-redef]
    def isEventExpired(cls) -> BooleanClauseList:  # pylint: disable=no-self-argument
        return sa.and_(cls.beginningDatetime != None, cls.beginningDatetime <= sa.func.now())

    @sa.ext.hybrid.hybrid_property
    def isExpired(self) -> bool:
        return self.isEventExpired or self.hasBookingLimitDatetimePassed

    @isExpired.expression  # type: ignore [no-redef]
    def isExpired(cls) -> BooleanClauseList:  # pylint: disable=no-self-argument
        return sa.or_(cls.isEventExpired, cls.hasBookingLimitDatetimePassed)

    @property
    def isEventDeletable(self):  # type: ignore [no-untyped-def]
        if not self.beginningDatetime:
            return True
        limit_date_for_stock_deletion = self.beginningDatetime + bookings_constants.AUTO_USE_AFTER_EVENT_TIME_DELAY
        return limit_date_for_stock_deletion >= datetime.utcnow()

    @sa.ext.hybrid.hybrid_property
    def isSoldOut(self) -> bool:
        # pylint: disable=comparison-with-callable
        return (
            self.isSoftDeleted
            or (self.beginningDatetime is not None and self.beginningDatetime <= datetime.utcnow())
            or (self.remainingQuantity != "unlimited" and self.remainingQuantity <= 0)
        )

    @isSoldOut.expression  # type: ignore [no-redef]
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
    def queryNotSoftDeleted(cls):  # type: ignore [no-untyped-def]
        return Stock.query.filter_by(isSoftDeleted=False)

    @staticmethod
    def restize_internal_error(internal_error):  # type: ignore [no-untyped-def]
        if "check_stock" in str(internal_error.orig):
            if "quantity_too_low" in str(internal_error.orig):
                return ["quantity", "Le stock total ne peut être inférieur au nombre de réservations"]
            if "bookingLimitDatetime_too_late" in str(internal_error.orig):
                return [
                    "bookingLimitDatetime",
                    "La date limite de réservation pour cette offre est postérieure à la date de début de l'évènement",
                ]
            logger.error("Unexpected error in patch stocks: %s", internal_error)
        return PcObject.restize_internal_error(internal_error)

    @property
    def canHaveActivationCodes(self):  # type: ignore [no-untyped-def]
        return self.offer.isDigital


@sa.event.listens_for(Stock, "before_insert")
def before_insert(mapper, configuration, self):  # type: ignore [no-untyped-def]
    if self.beginningDatetime and not self.bookingLimitDatetime:
        self.bookingLimitDatetime = self.beginningDatetime.replace(hour=23).replace(minute=59) - timedelta(days=3)


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
    NO_TICKET = "no_ticket"
    BY_EMAIL = "by_email"
    ON_SITE = "on_site"


class Offer(PcObject, Base, Model, ExtraDataMixin, DeactivableMixin, ValidationMixin, AccessibilityMixin, StatusMixin):  # type: ignore [valid-type, misc]
    __tablename__ = "offer"

    productId: int = sa.Column(sa.BigInteger, sa.ForeignKey("product.id"), index=True, nullable=False)

    product: Product = sa.orm.relationship(Product, foreign_keys=[productId], backref="offers")

    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id"), nullable=False, index=True)

    venue = sa.orm.relationship("Venue", foreign_keys=[venueId], backref="offers")  # type: ignore [misc]

    bookingEmail = sa.Column(sa.String(120), nullable=True)

    name: str = sa.Column(sa.String(140), nullable=False)
    sa.Index("idx_offer_trgm_name", name, postgresql_using="gin")

    description = sa.Column(sa.Text, nullable=True)

    withdrawalDetails = sa.Column(sa.Text, nullable=True)

    withdrawalType = sa.Column(sa.Enum(WithdrawalTypeEnum), nullable=True)
    withdrawalDelay = sa.Column(sa.BigInteger, nullable=True)

    conditions = sa.Column(sa.String(120), nullable=True)

    ageMin = sa.Column(sa.Integer, nullable=True)
    ageMax = sa.Column(sa.Integer, nullable=True)

    url = sa.Column(sa.String(255), nullable=True)

    # FIXME (cgaunet, 2022-08-02): this field seems to be unused
    mediaUrls = sa.Column(postgresql.ARRAY(sa.String(220)), nullable=False, default=[])

    durationMinutes = sa.Column(sa.Integer, nullable=True)

    isNational = sa.Column(sa.Boolean, default=False, nullable=False)

    isDuo = sa.Column(sa.Boolean, server_default=sa.false(), default=False, nullable=False)

    dateCreated = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)

    criteria = sa.orm.relationship(  # type: ignore [misc]
        "Criterion", backref=db.backref("criteria", lazy="dynamic"), secondary="offer_criterion"
    )

    externalTicketOfficeUrl = sa.Column(sa.String, nullable=True)

    authorId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=True)

    author: Mapped["User"] | None = relationship("User", foreign_keys=[authorId], backref="offers", uselist=False)

    rankingWeight = sa.Column(sa.Integer, nullable=True)

    # This field replaces the idAtProviders coming from ProvidableMixin
    idAtProvider = sa.Column(
        sa.Text,
        sa.CheckConstraint(
            '"lastProviderId" IS NULL OR "idAtProvider" IS NOT NULL',
            name="check_providable_with_provider_has_idatprovider",
        ),
        nullable=True,
    )

    @property
    def isEducational(self) -> bool:
        return False

    subcategoryId = sa.Column(sa.Text, nullable=False, index=True)

    dateUpdated: datetime = sa.Column(sa.DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)

    dateModifiedAtLastProvider = sa.Column(sa.DateTime, nullable=True, default=datetime.utcnow)

    fieldsUpdated = sa.Column(postgresql.ARRAY(sa.String(100)), nullable=False, default=[], server_default="{}")

    # FIXME: We shoud be able to remove the index on `venueId`, since this composite index
    #  can be used by PostgreSQL when filtering on the `venueId` column only.
    sa.Index("venueId_idAtProvider_index", venueId, idAtProvider, unique=True)

    sa.Index("offer_isbn_idx", ExtraDataMixin.extraData["isbn"].astext)

    @sa.ext.declarative.declared_attr  # type: ignore [misc]
    def lastProviderId(cls):  # pylint: disable=no-self-argument
        return sa.Column(sa.BigInteger, sa.ForeignKey("provider.id"), nullable=True)

    @sa.ext.declarative.declared_attr  # type: ignore [misc]
    def lastProvider(cls):  # pylint: disable=no-self-argument
        return sa.orm.relationship("Provider", foreign_keys=[cls.lastProviderId])

    @sa.ext.hybrid.hybrid_property
    def isSoldOut(self) -> bool:
        for stock in self.stocks:
            if (
                not stock.isSoftDeleted
                and (stock.beginningDatetime is None or stock.beginningDatetime > datetime.utcnow())
                and (stock.remainingQuantity == "unlimited" or stock.remainingQuantity > 0)
            ):
                return False
        return True

    @isSoldOut.expression  # type: ignore [no-redef]
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

    @sa.ext.hybrid.hybrid_property
    def canExpire(self) -> bool:
        return self.subcategoryId in subcategories.EXPIRABLE_SUBCATEGORIES

    @canExpire.expression  # type: ignore [no-redef]
    def canExpire(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.subcategoryId.in_(subcategories.EXPIRABLE_SUBCATEGORIES)

    @property
    def isReleased(self) -> bool:
        return (
            self._released
            and self.venue.isReleased
            and self.venue.managingOfferer.isActive
            and self.venue.managingOfferer.isValidated
        )

    @sa.ext.hybrid.hybrid_property
    def _released(self) -> bool:
        return self.isActive and self.validation == OfferValidationStatus.APPROVED

    @_released.expression  # type: ignore [no-redef]
    def _released(cls) -> bool:  # pylint: disable=no-self-argument
        return sa.and_(cls.isActive, cls.validation == OfferValidationStatus.APPROVED)

    @sa.ext.hybrid.hybrid_property
    def isPermanent(self) -> bool:
        return self.subcategoryId in subcategories.PERMANENT_SUBCATEGORIES

    @isPermanent.expression  # type: ignore [no-redef]
    def isPermanent(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.subcategoryId.in_(subcategories.PERMANENT_SUBCATEGORIES)

    @property
    def dateRange(self) -> DateTimes:
        if self.isThing or not self.activeStocks:
            return DateTimes()

        start = min(stock.beginningDatetime for stock in self.activeStocks)  # type: ignore [type-var]
        end = max(stock.beginningDatetime for stock in self.activeStocks)  # type: ignore [type-var]
        return DateTimes(start, end)

    @sa.ext.hybrid.hybrid_property
    def isEvent(self) -> bool:
        return self.subcategory.is_event

    @isEvent.expression  # type: ignore [no-redef]
    def isEvent(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.subcategoryId.in_(subcategories.EVENT_SUBCATEGORIES)

    @property
    def isThing(self) -> bool:
        return not self.subcategory.is_event

    @sa.ext.hybrid.hybrid_property
    def isDigital(self) -> bool:
        return self.url is not None and self.url != ""

    @isDigital.expression  # type: ignore [no-redef]
    def isDigital(cls) -> bool:  # pylint: disable=no-self-argument
        return sa.and_(cls.url != None, cls.url != "")

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
        return self.isFromProvider and self.lastProvider.isAllocine

    @property
    def isBookable(self) -> bool:
        for stock in self.stocks:
            if stock.isBookable:
                return True
        return False

    @sa.ext.hybrid.hybrid_property
    def is_eligible_for_search(self) -> bool:
        return self.isReleased and self.isBookable

    @is_eligible_for_search.expression  # type: ignore [no-redef]
    def is_eligible_for_search(cls) -> BooleanClauseList:  # pylint: disable=no-self-argument
        return sa.and_(cls._released, Stock._bookable)

    @sa.ext.hybrid.hybrid_property
    def hasBookingLimitDatetimesPassed(self) -> bool:
        if self.activeStocks:
            return all(stock.hasBookingLimitDatetimePassed for stock in self.activeStocks)
        return False

    @hasBookingLimitDatetimesPassed.expression  # type: ignore [no-redef]
    def hasBookingLimitDatetimesPassed(cls) -> BooleanClauseList:  # pylint: disable=no-self-argument
        return sa.and_(
            sa.exists().where(Stock.offerId == cls.id).where(Stock.isSoftDeleted.is_(False)),
            ~sa.exists()
            .where(Stock.offerId == cls.id)
            .where(Stock.isSoftDeleted.is_(False))
            .where(Stock.hasBookingLimitDatetimePassed.is_(False)),
        )

    @property
    def activeStocks(self) -> list[Stock]:
        return [stock for stock in self.stocks if not stock.isSoftDeleted]

    @property
    def bookableStocks(self) -> list[Stock]:
        return [stock for stock in self.stocks if stock.isBookable]

    @property
    def is_forbidden_to_underage(self) -> bool:
        return all(stock.is_forbidden_to_underage for stock in self.bookableStocks)

    @property
    def subcategory(self) -> subcategories.Subcategory:
        if self.subcategoryId not in subcategories.ALL_SUBCATEGORIES_DICT:
            raise ValueError(f"Unexpected subcategoryId '{self.subcategoryId}' for offer {self.id}")
        return subcategories.ALL_SUBCATEGORIES_DICT[self.subcategoryId]

    @property
    def subcategory_v2(self) -> subcategories_v2.Subcategory:
        if self.subcategoryId not in subcategories_v2.ALL_SUBCATEGORIES_DICT:
            raise ValueError(f"Unexpected subcategoryId (v2) '{self.subcategoryId}' for offer {self.id}")
        return subcategories_v2.ALL_SUBCATEGORIES_DICT[self.subcategoryId]

    @property
    def category(self) -> categories.Category:
        return self.subcategory.category

    @property
    def image(self) -> OfferImage | None:
        activeMediation = self.activeMediation
        if activeMediation:
            url = activeMediation.thumbUrl
            if url:
                return OfferImage(url, activeMediation.credit)

        productUrl = self.product.thumbUrl if self.product else None
        if productUrl:
            return OfferImage(productUrl, credit=None)

        return None

    @property
    def thumbUrl(self) -> str:
        image = self.image
        return image.url if image else None  # type: ignore [return-value]

    @property
    def is_offline_only(self) -> bool:
        return self.subcategory.online_offline_platform == subcategories.OnlineOfflinePlatformChoices.OFFLINE.value

    @property
    def max_price(self) -> float:  # used in validation rule, do not remove
        try:
            return max(stock.price for stock in self.stocks if not stock.isSoftDeleted)
        except ValueError:  # if no non-deleted stocks
            return 0


class ActivationCode(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    __tablename__ = "activation_code"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    code = sa.Column(sa.Text, nullable=False)

    expirationDate = sa.Column(sa.DateTime, nullable=True, default=None)

    stockId = sa.Column(sa.BigInteger, sa.ForeignKey("stock.id"), index=True, nullable=False)

    stock = sa.orm.relationship("Stock", back_populates="activationCodes")  # type: ignore [misc]

    bookingId = sa.Column(sa.BigInteger, sa.ForeignKey("booking.id"), index=True, nullable=True)

    booking = sa.orm.relationship("Booking", back_populates="activationCode")  # type: ignore [misc]

    __table_args__ = (
        sa.UniqueConstraint(
            "stockId",
            "code",
            name="unique_code_in_stock",
        ),
    )


class OfferValidationConfig(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    __tablename__ = "offer_validation_config"

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    dateCreated = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)

    userId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"))

    user = sa.orm.relationship("User", foreign_keys=[userId], backref="offer_validation_configs")  # type: ignore [misc]

    specs = sa.Column("specs", sa.dialects.postgresql.JSONB, nullable=False)


@dataclass
class ReasonMeta:
    title: str
    description: str


class Reason(enum.Enum):
    """
    Describe possible reason codes to used when reporting an offer.

    The whole meta part is only consumed by the api client, it has no meaning
    inside the whole API code.

    Note: when adding a new enum symbol, do not forget to update the meta
    method.
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


class OfferReport(PcObject, Base, Model):  # type: ignore [valid-type, misc]
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

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    userId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)

    user = sa.orm.relationship("User", foreign_keys=[userId], backref="reported_offers")  # type: ignore [misc]

    offerId = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), index=True, nullable=False)

    offer = sa.orm.relationship("Offer", foreign_keys=[offerId], backref="reports")  # type: ignore [misc]

    reportedAt = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())

    reason = sa.Column(sa.Enum(Reason, create_constraint=False), nullable=False, index=True)

    # If the reason code is OTHER, save the user's custom reason
    customReasonContent = sa.Column(sa.Text, nullable=True)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}#{self.id} userId={self.userId}, offerId={self.offerId}, when={self.when}"
