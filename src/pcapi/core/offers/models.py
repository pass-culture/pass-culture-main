from datetime import datetime
from datetime import timedelta
from pprint import pformat
from typing import List
from typing import Optional

from sqlalchemy import ARRAY
from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import DDL
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import event
from sqlalchemy import false
from sqlalchemy.event import listens_for
from sqlalchemy.orm import relationship

from pcapi.domain.ts_vector import create_fts_index
from pcapi.domain.ts_vector import create_ts_vector
from pcapi.models.db import Model
from pcapi.models.db import db
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.extra_data_mixin import ExtraDataMixin
from pcapi.models.mediation_sql_entity import MediationSQLEntity
from pcapi.models.offer_type import Category
from pcapi.models.offer_type import EventType
from pcapi.models.offer_type import ProductType
from pcapi.models.offer_type import ThingType
from pcapi.models.pc_object import PcObject
from pcapi.models.providable_mixin import ProvidableMixin
from pcapi.models.soft_deletable_mixin import SoftDeletableMixin
from pcapi.models.versioned_mixin import VersionedMixin
from pcapi.utils.date import DateTimes
from pcapi.utils.logger import logger


EVENT_AUTOMATIC_REFUND_DELAY = timedelta(hours=48)


class Stock(PcObject, Model, ProvidableMixin, SoftDeletableMixin, VersionedMixin):
    __tablename__ = "stock"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    dateCreated = Column(DateTime, nullable=False, default=datetime.utcnow)

    dateModified = Column(DateTime, nullable=False, default=datetime.utcnow)

    beginningDatetime = Column(DateTime, index=True, nullable=True)

    offerId = Column(BigInteger, ForeignKey("offer.id"), index=True, nullable=False)

    offer = relationship("Offer", foreign_keys=[offerId], backref="stocks")

    price = Column(Numeric(10, 2), CheckConstraint("price >= 0", name="check_price_is_not_negative"), nullable=False)

    quantity = Column(Integer, nullable=True)

    bookingLimitDatetime = Column(DateTime, nullable=True)

    @property
    def isBookable(self):
        if self.hasBookingLimitDatetimePassed:
            return False
        if not self.offer.venue.managingOfferer.isActive:
            return False
        if self.offer.venue.managingOfferer.validationToken:
            return False
        if self.offer.venue.validationToken:
            return False
        if not self.offer.isActive:
            return False
        if self.isSoftDeleted:
            return False
        if self.beginningDatetime and self.beginningDatetime < datetime.utcnow():
            return False
        if self.quantity is not None and self.remainingQuantity == 0:
            return False
        return True

    @property
    def hasBookingLimitDatetimePassed(self):
        if self.bookingLimitDatetime and self.bookingLimitDatetime < datetime.utcnow():
            return True
        return False

    @property
    def bookingsQuantity(self):
        return sum([booking.quantity for booking in self.bookings if not booking.isCancelled])

    @property
    def remainingQuantity(self):
        return "unlimited" if self.quantity is None else self.quantity - self.bookingsQuantity

    @property
    def isEventExpired(self):
        return False if self.beginningDatetime is None else self.beginningDatetime <= datetime.utcnow()

    @property
    def isEventDeletable(self):
        if self.beginningDatetime:
            limit_date_for_stock_deletion = self.beginningDatetime + EVENT_AUTOMATIC_REFUND_DELAY
            return limit_date_for_stock_deletion >= datetime.utcnow()
        else:
            return True

    @classmethod
    def queryNotSoftDeleted(cls):
        return Stock.query.filter_by(isSoftDeleted=False)

    @staticmethod
    def restize_internal_error(ie):
        if "check_stock" in str(ie.orig):
            if "quantity_too_low" in str(ie.orig):
                return ["quantity", "Le stock total ne peut être inférieur au nombre de réservations"]
            elif "bookingLimitDatetime_too_late" in str(ie.orig):
                return [
                    "bookingLimitDatetime",
                    "La date limite de réservation pour cette offre est postérieure à la date de début de l'évènement",
                ]
            else:
                logger.error("Unexpected error in patch stocks: " + pformat(ie))
        return PcObject.restize_internal_error(ie)


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


class Offer(PcObject, Model, ExtraDataMixin, DeactivableMixin, ProvidableMixin, VersionedMixin):
    __tablename__ = "offer"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    productId = Column(BigInteger, ForeignKey("product.id"), index=True, nullable=False)

    product = relationship("Product", foreign_keys=[productId], backref="offers")

    venueId = Column(BigInteger, ForeignKey("venue.id"), nullable=False, index=True)

    venue = relationship("VenueSQLEntity", foreign_keys=[venueId], backref="offers")

    bookingEmail = Column(String(120), nullable=True)

    type = Column(String(50), CheckConstraint("type != 'None'"), index=True, nullable=False)

    name = Column(String(140), nullable=False)

    description = Column(Text, nullable=True)

    withdrawalDetails = Column(Text, nullable=True)

    conditions = Column(String(120), nullable=True)

    ageMin = Column(Integer, nullable=True)
    ageMax = Column(Integer, nullable=True)

    url = Column(String(255), nullable=True)

    mediaUrls = Column(ARRAY(String(220)), nullable=False, default=[])

    durationMinutes = Column(Integer, nullable=True)

    isNational = Column(Boolean, server_default=false(), default=False, nullable=False)

    isDuo = Column(Boolean, server_default=false(), default=False, nullable=False)

    dateCreated = Column(DateTime, nullable=False, default=datetime.utcnow)

    criteria = relationship("Criterion", backref=db.backref("criteria", lazy="dynamic"), secondary="offer_criterion")

    def update_with_product_data(self, product_dict: dict) -> None:
        owning_offerer = self.product.owningOfferer
        if owning_offerer and owning_offerer == self.venue.managingOfferer:
            self.product.populate_from_dict(product_dict)

    @property
    def activeMediation(self) -> Optional[MediationSQLEntity]:
        sorted_by_date_desc = sorted(self.mediations, key=lambda m: m.dateCreated, reverse=True)
        only_active = list(filter(lambda m: m.isActive, sorted_by_date_desc))
        return only_active[0] if only_active else None

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
        if not self.isFromProvider:
            return True
        return self.isFromAllocine

    @property
    def isFromProvider(self) -> bool:
        return self.lastProviderId is not None

    @property
    def isFromAllocine(self) -> bool:
        from pcapi import local_providers  # avoid import loop

        return self.isFromProvider and self.lastProvider.localClass == local_providers.AllocineStocks.__name__

    @property
    def isBookable(self) -> bool:
        for stock in self.stocks:
            if stock.isBookable:
                return True
        return False

    @property
    def hasBookingLimitDatetimesPassed(self) -> bool:
        if self.activeStocks:
            return all([stock.hasBookingLimitDatetimePassed for stock in self.activeStocks])
        return False

    @property
    def activeStocks(self) -> List[Stock]:
        return [stock for stock in self.stocks if not stock.isSoftDeleted]

    @property
    def offerType(self) -> Optional[dict]:
        all_types = list(ThingType) + list(EventType)
        for possible_type in all_types:
            if str(possible_type) == self.type:
                return possible_type.as_dict()

    @property
    def offer_category(self) -> str:
        for category in Category:
            if self.offerType["appLabel"] in category.value:
                return category.name

    @property
    def thumbUrl(self) -> str:
        offer_has_active_mediation = any(map(lambda mediation: mediation.isActive, self.mediations))
        if offer_has_active_mediation:
            return self.activeMediation.thumbUrl
        if self.product:
            return self.product.thumbUrl
        return ""

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


Offer.__name_ts_vector__ = create_ts_vector(Offer.name)
Offer.__table_args__ = [create_fts_index("idx_offer_fts_name", Offer.__name_ts_vector__)]
