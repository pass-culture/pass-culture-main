from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
import enum
import logging
from typing import Optional

from sqlalchemy import ARRAY
from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import DDL
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy import and_
from sqlalchemy import case
from sqlalchemy import event
from sqlalchemy import exists
from sqlalchemy import false
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.event import listens_for
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

import pcapi.core.bookings.conf as bookings_conf
from pcapi.models.db import Model
from pcapi.models.db import db
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.extra_data_mixin import ExtraDataMixin
from pcapi.models.has_thumb_mixin import HasThumbMixin
from pcapi.models.offer_type import ALL_OFFER_TYPES_DICT
from pcapi.models.offer_type import CATEGORIES_LABEL_DICT
from pcapi.models.offer_type import CategoryType
from pcapi.models.offer_type import EXPIRABLE_OFFER_TYPES
from pcapi.models.offer_type import PERMANENT_OFFER_TYPES
from pcapi.models.offer_type import ProductType
from pcapi.models.offer_type import ThingType
from pcapi.models.pc_object import PcObject
from pcapi.models.providable_mixin import ProvidableMixin
from pcapi.models.soft_deletable_mixin import SoftDeletableMixin
from pcapi.utils.date import DateTimes


logger = logging.getLogger(__name__)


class Mediation(PcObject, Model, HasThumbMixin, ProvidableMixin, DeactivableMixin):
    __tablename__ = "mediation"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    credit = Column(String(255), nullable=True)

    dateCreated = Column(DateTime, nullable=False, default=datetime.utcnow)

    authorId = Column(BigInteger, ForeignKey("user.id"), nullable=True)

    author = relationship("User", foreign_keys=[authorId], backref="mediations")

    offerId = Column(BigInteger, ForeignKey("offer.id"), index=True, nullable=False)

    offer = relationship("Offer", foreign_keys=[offerId], backref="mediations")


class Stock(PcObject, Model, ProvidableMixin, SoftDeletableMixin):
    __tablename__ = "stock"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    dateCreated = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())

    dateModified = Column(DateTime, nullable=False, default=datetime.utcnow)

    beginningDatetime = Column(DateTime, index=True, nullable=True)

    offerId = Column(BigInteger, ForeignKey("offer.id"), index=True, nullable=False)

    offer = relationship("Offer", foreign_keys=[offerId], backref="stocks")

    price = Column(Numeric(10, 2), CheckConstraint("price >= 0", name="check_price_is_not_negative"), nullable=False)

    quantity = Column(Integer, nullable=True)

    bookingLimitDatetime = Column(DateTime, nullable=True)

    dnBookedQuantity = Column(BigInteger, nullable=False, server_default=text("0"))

    rawProviderQuantity = Column(Integer, nullable=True)

    activationCodes = relationship("ActivationCode", back_populates="stock")

    @property
    def isBookable(self):
        return not self.isExpired and self.offer.isReleased and not self.isSoldOut

    @hybrid_property
    def hasBookingLimitDatetimePassed(self):
        return bool(self.bookingLimitDatetime and self.bookingLimitDatetime <= datetime.utcnow())

    @hasBookingLimitDatetimePassed.expression
    def hasBookingLimitDatetimePassed(cls):  # pylint: disable=no-self-argument
        return and_(cls.bookingLimitDatetime != None, cls.bookingLimitDatetime <= func.now())

    # TODO(fseguin, 2021-03-25): replace unlimited by None (also in the front-end)
    @hybrid_property
    def remainingQuantity(self):
        return "unlimited" if self.quantity is None else self.quantity - self.dnBookedQuantity

    @remainingQuantity.expression
    def remainingQuantity(cls):  # pylint: disable=no-self-argument
        return case([(cls.quantity.is_(None), None)], else_=(cls.quantity - cls.dnBookedQuantity))

    @hybrid_property
    def isEventExpired(self):
        return bool(self.beginningDatetime and self.beginningDatetime <= datetime.utcnow())

    @isEventExpired.expression
    def isEventExpired(cls):  # pylint: disable=no-self-argument
        return and_(cls.beginningDatetime != None, cls.beginningDatetime <= func.now())

    @property
    def isExpired(self):
        return self.isEventExpired or self.hasBookingLimitDatetimePassed

    @property
    def isEventDeletable(self):
        if not self.beginningDatetime:
            return True
        limit_date_for_stock_deletion = self.beginningDatetime + bookings_conf.AUTO_USE_AFTER_EVENT_TIME_DELAY
        return limit_date_for_stock_deletion >= datetime.utcnow()

    @property
    def isSoldOut(self):
        # pylint: disable=comparison-with-callable
        if (
            not self.isSoftDeleted
            and (self.beginningDatetime is None or self.beginningDatetime > datetime.utcnow())
            and (self.remainingQuantity == "unlimited" or self.remainingQuantity > 0)
        ):
            return False
        return True

    @classmethod
    def queryNotSoftDeleted(cls):
        return Stock.query.filter_by(isSoftDeleted=False)

    @staticmethod
    def restize_internal_error(ie):
        if "check_stock" in str(ie.orig):
            if "quantity_too_low" in str(ie.orig):
                return ["quantity", "Le stock total ne peut être inférieur au nombre de réservations"]
            if "bookingLimitDatetime_too_late" in str(ie.orig):
                return [
                    "bookingLimitDatetime",
                    "La date limite de réservation pour cette offre est postérieure à la date de début de l'évènement",
                ]
            logger.error("Unexpected error in patch stocks: %s", ie)
        return PcObject.restize_internal_error(ie)

    @property
    def canHaveActivationCodes(self):
        return self.offer.isDigital


@listens_for(Stock, "before_insert")
def before_insert(mapper, configuration, self):
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
          AND NOT booking."isCancelled"
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

event.listen(Stock.__table__, "after_create", DDL(Stock.trig_ddl))

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

event.listen(Stock.__table__, "after_create", DDL(Stock.trig_update_date_ddl))


@dataclass
class OfferImage:
    url: str
    credit: Optional[str] = None


class OfferStatus(enum.Enum):
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


class Offer(PcObject, Model, ExtraDataMixin, DeactivableMixin, ProvidableMixin):
    __tablename__ = "offer"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    productId = Column(BigInteger, ForeignKey("product.id"), index=True, nullable=False)

    product = relationship("Product", foreign_keys=[productId], backref="offers")

    venueId = Column(BigInteger, ForeignKey("venue.id"), nullable=False, index=True)

    venue = relationship("Venue", foreign_keys=[venueId], backref="offers")

    bookingEmail = Column(String(120), nullable=True)

    type = Column(String(50), CheckConstraint("type != 'None'"), index=True, nullable=False)

    name = Column(String(140), nullable=False)
    Index("idx_offer_trgm_name", name, postgresql_using="gin")

    description = Column(Text, nullable=True)

    withdrawalDetails = Column(Text, nullable=True)

    conditions = Column(String(120), nullable=True)

    ageMin = Column(Integer, nullable=True)
    ageMax = Column(Integer, nullable=True)

    url = Column(String(255), nullable=True)

    mediaUrls = Column(ARRAY(String(220)), nullable=False, default=[])

    durationMinutes = Column(Integer, nullable=True)

    isNational = Column(Boolean, default=False, nullable=False)

    isDuo = Column(Boolean, server_default=false(), default=False, nullable=False)

    dateCreated = Column(DateTime, nullable=False, default=datetime.utcnow)

    criteria = relationship("Criterion", backref=db.backref("criteria", lazy="dynamic"), secondary="offer_criterion")

    audioDisabilityCompliant = Column(Boolean, nullable=True)

    mentalDisabilityCompliant = Column(Boolean, nullable=True)

    motorDisabilityCompliant = Column(Boolean, nullable=True)

    visualDisabilityCompliant = Column(Boolean, nullable=True)

    externalTicketOfficeUrl = Column(String, nullable=True)

    lastValidationDate = Column(DateTime, index=True, nullable=True)

    validation = Column(
        Enum(OfferValidationStatus),
        nullable=False,
        default=OfferValidationStatus.APPROVED,
        # changing the server_default will cost an UPDATE migration on all existing null rows
        server_default="APPROVED",
        index=True,
    )

    authorId = Column(BigInteger, ForeignKey("user.id"), nullable=True)

    author = relationship("User", foreign_keys=[authorId], backref="offers")

    rankingWeight = Column(Integer, nullable=True)

    # This field will replace the idAtProviders coming from ProvidableMixin
    idAtProvider = Column(
        Text,
        CheckConstraint(
            '"lastProviderId" IS NULL OR "idAtProvider" IS NOT NULL',
            name="check_providable_with_provider_has_idatprovider",
        ),
        nullable=True,
    )

    isEducational = Column(Boolean, server_default=false(), default=False, nullable=False)

    subcategoryId = Column(Text, nullable=True, index=True)

    # FIXME: We shoud be able to remove the index on `venueId`, since this composite index
    #  can be used by PostgreSQL when filtering on the `venueId` column only.
    Index("venueId_idAtProvider_index", venueId, idAtProvider, unique=True)

    @hybrid_property
    def isSoldOut(self):
        for stock in self.stocks:
            if (
                not stock.isSoftDeleted
                and (stock.beginningDatetime is None or stock.beginningDatetime > datetime.utcnow())
                and (stock.remainingQuantity == "unlimited" or stock.remainingQuantity > 0)
            ):
                return False
        return True

    @isSoldOut.expression
    def isSoldOut(cls):  # pylint: disable=no-self-argument
        return (
            ~exists()
            .where(Stock.offerId == cls.id)
            .where(Stock.isSoftDeleted.is_(False))
            .where(or_(Stock.beginningDatetime > func.now(), Stock.beginningDatetime.is_(None)))
            .where(or_(Stock.remainingQuantity.is_(None), Stock.remainingQuantity > 0))
        )

    @property
    def activeMediation(self) -> Optional[Mediation]:
        sorted_by_date_desc = sorted(self.mediations, key=lambda m: m.dateCreated, reverse=True)
        only_active = list(filter(lambda m: m.isActive, sorted_by_date_desc))
        return only_active[0] if only_active else None

    @hybrid_property
    def canExpire(self) -> bool:
        return self.type in EXPIRABLE_OFFER_TYPES

    @canExpire.expression
    def canExpire(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.type.in_(EXPIRABLE_OFFER_TYPES)

    @property
    def isReleased(self) -> bool:
        return (
            self.isActive
            and self.validation == OfferValidationStatus.APPROVED
            and self.venue.isValidated
            and self.venue.managingOfferer.isActive
            and self.venue.managingOfferer.isValidated
        )

    @hybrid_property
    def isPermanent(self) -> bool:
        return self.type in PERMANENT_OFFER_TYPES

    @isPermanent.expression
    def isPermanent(cls) -> bool:  # pylint: disable=no-self-argument
        return cls.type.in_(PERMANENT_OFFER_TYPES)

    @property
    def dateRange(self) -> DateTimes:
        if ProductType.is_thing(self.type) or not self.activeStocks:
            return DateTimes()

        start = min([stock.beginningDatetime for stock in self.activeStocks])
        end = max([stock.beginningDatetime for stock in self.activeStocks])
        return DateTimes(start, end)

    @property
    def isEvent(self) -> bool:
        return ProductType.is_event(self.type)

    @property
    def isThing(self) -> bool:
        return ProductType.is_thing(self.type)

    @property
    def isDigital(self) -> bool:
        return self.url is not None and self.url != ""

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

    @hybrid_property
    def hasBookingLimitDatetimesPassed(self) -> bool:
        if self.activeStocks:
            return all(stock.hasBookingLimitDatetimePassed for stock in self.activeStocks)
        return False

    @hasBookingLimitDatetimesPassed.expression
    def hasBookingLimitDatetimesPassed(cls):  # pylint: disable=no-self-argument
        return and_(
            exists().where(Stock.offerId == cls.id).where(Stock.isSoftDeleted.is_(False)),
            ~exists()
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
    def offerType(self) -> Optional[dict]:
        if self.type not in ALL_OFFER_TYPES_DICT:
            raise ValueError(f"Unexpected offer type '{self.type}' for offer {self.id}")

        return ALL_OFFER_TYPES_DICT[self.type]

    # TODO(fseguin, 2021-06-02: remove after fully implementing OfferCategory)
    @property
    def offer_category_name_for_app(self) -> str:
        # offer_types ThingType.OEUVRE_ART, EventType.ACTIVATION and ThingType.ACTIVATION do not have a corresponding Category so return None in this case
        return CATEGORIES_LABEL_DICT.get(self.offerType["appLabel"])

    @property
    def category_type(self) -> Optional[str]:
        if self.isEvent:
            return CategoryType.EVENT.value

        if self.isThing:
            return CategoryType.THING.value

        return None

    @property
    def image(self) -> Optional[OfferImage]:
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
        return image.url if image else None

    @property
    def is_offline_only(self) -> bool:
        offline_thing = [
            thing_type
            for thing_type in ThingType
            if self._is_same_type(thing_type) and self._is_offline_type_only(thing_type)
        ]

        return len(list(offline_thing)) == 1

    def _is_same_type(self, thing_type) -> bool:
        return str(thing_type) == self.type

    def _is_offline_type_only(self, thing_type):
        return thing_type.value["offlineOnly"]

    def get_label_from_type_string(self):
        matching_type_thing = next(filter(lambda thing_type: str(thing_type) == self.type, ThingType))
        return matching_type_thing.value["proLabel"]

    @hybrid_property
    def status(self) -> OfferStatus:
        # pylint: disable=too-many-return-statements
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

    @status.expression
    def status(cls):  # pylint: disable=no-self-argument
        return case(
            [
                (cls.validation == OfferValidationStatus.REJECTED.name, OfferStatus.REJECTED.name),
                (cls.validation == OfferValidationStatus.PENDING.name, OfferStatus.PENDING.name),
                (cls.validation == OfferValidationStatus.DRAFT.name, OfferStatus.DRAFT.name),
                (cls.isActive.is_(False), OfferStatus.INACTIVE.name),
                (cls.hasBookingLimitDatetimesPassed.is_(True), OfferStatus.EXPIRED.name),
                (cls.isSoldOut.is_(True), OfferStatus.SOLD_OUT.name),
            ],
            else_=OfferStatus.ACTIVE.name,
        )

    @property
    def max_price(self) -> float:
        return max(stock.price for stock in self.stocks if not stock.isSoftDeleted)


class ActivationCode(PcObject, Model):
    __tablename__ = "activation_code"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    code = Column(Text, nullable=False)

    expirationDate = Column(DateTime, nullable=True, default=None)

    stockId = Column(BigInteger, ForeignKey("stock.id"), index=True, nullable=False)

    stock = relationship("Stock", back_populates="activationCodes")

    bookingId = Column(BigInteger, ForeignKey("booking.id"), index=True, nullable=True)

    booking = relationship("Booking", back_populates="activationCode")

    __table_args__ = (
        UniqueConstraint(
            "stockId",
            "code",
            name="unique_code_in_stock",
        ),
    )


class OfferValidationConfig(PcObject, Model):
    __tablename__ = "offer_validation_config"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    dateCreated = Column(DateTime, nullable=False, default=datetime.utcnow)

    userId = Column(BigInteger, ForeignKey("user.id"))

    user = relationship("User", foreign_keys=[userId], backref="offer_validation_configs")

    specs = Column(JSON, nullable=False)


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


class OfferReport(PcObject, Model):
    __tablename__ = "offer_report"

    __table_args__ = (
        UniqueConstraint(
            "userId",
            "offerId",
            name="unique_offer_per_user",
        ),
        CheckConstraint(
            OFFER_REPORT_CUSTOM_REASONS_CONSTRAINT,
            name="custom_reason_null_only_if_reason_is_other",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    userId = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)

    user = relationship("User", foreign_keys=[userId], backref="reported_offers")

    offerId = Column(BigInteger, ForeignKey("offer.id", ondelete="CASCADE"), index=True, nullable=False)

    offer = relationship("Offer", foreign_keys=[offerId], backref="reports")

    reportedAt = Column(DateTime, nullable=False, server_default=func.now())

    reason = Column(Enum(Reason, create_constraint=False), nullable=False, index=True)

    # If the reason code is OTHER, save the user's custom reason
    customReasonContent = Column(Text, nullable=True)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}#{self.id} userId={self.userId}, offerId={self.offerId}, when={self.when}"
