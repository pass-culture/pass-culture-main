""" stock """
from datetime import datetime, timedelta
from pprint import pformat

from sqlalchemy import BigInteger, \
    CheckConstraint, \
    Column, \
    DateTime, \
    DDL, \
    event, \
    ForeignKey, \
    Integer, \
    Numeric, \
    and_, \
    or_
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.sql import select, func
from sqlalchemy.event import listens_for

from models.booking import Booking
from models.db import Model
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin
from models.soft_deletable_mixin import SoftDeletableMixin
from models.versioned_mixin import VersionedMixin
from utils.logger import logger


class Stock(PcObject,
            Model,
            ProvidableMixin,
            SoftDeletableMixin,
            VersionedMixin):
    # We redefine this so we can reference it in the baseScore column_property
    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    dateCreated = Column(DateTime,
                         nullable=False,
                         default=datetime.utcnow)

    dateModified = Column(DateTime,
                          nullable=False,
                          default=datetime.utcnow)

    beginningDatetime = Column(DateTime,
                               index=True,
                               nullable=True)

    endDatetime = Column(DateTime,
                         CheckConstraint('"endDatetime" > "beginningDatetime"',
                                         name='check_end_datetime_is_after_beginning_datetime'),
                         nullable=True)

    offerId = Column(BigInteger,
                     ForeignKey('offer.id'),
                     index=True,
                     nullable=False)

    offer = relationship('Offer',
                         foreign_keys=[offerId],
                         backref='stocks')

    price = Column(Numeric(10, 2),
                   CheckConstraint('price >= 0', name='check_price_is_not_negative'),
                   nullable=False)

    available = Column(Integer,
                       nullable=True)

    remainingQuantity = column_property(
        select([func.greatest(available - func.coalesce(func.sum(Booking.quantity), 0), 0)])
        .where(
            and_(
                Booking.stockId == id,
                or_(
                    and_(Booking.isUsed == False,
                         Booking.isCancelled == False),
                    and_(Booking.isUsed == True,
                         Booking.dateUsed > dateModified)
                )
            )
        )
    )

    groupSize = Column(Integer,
                       nullable=False,
                       default=1)

    bookingLimitDatetime = Column(DateTime,
                                  nullable=True)

    bookingRecapSent = Column(DateTime,
                              nullable=True)

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
        if self.available is not None and self.remainingQuantity == 0:
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
    def resolvedOffer(self):
        return self.offer or self.eventOccurrence.offer

    @classmethod
    def queryNotSoftDeleted(cls):
        return Stock.query.filter_by(isSoftDeleted=False)

    @staticmethod
    def restize_internal_error(ie):
        if 'check_stock' in str(ie.orig):
            if 'available_too_low' in str(ie.orig):
                return ['available', 'Le stock total ne peut être inférieur au nombre de réservations']
            elif 'bookingLimitDatetime_too_late' in str(ie.orig):
                return ['bookingLimitDatetime',
                        'La date limite de réservation pour cette offre est postérieure à la date de début de l\'évènement']
            else:
                logger.error("Unexpected error in patch stocks: " + pformat(ie))
        return PcObject.restize_internal_error(ie)


@listens_for(Stock, 'before_insert')
def before_insert(mapper, configuration, self):
    if self.beginningDatetime and not self.bookingLimitDatetime:
        self.bookingLimitDatetime = self.beginningDatetime \
            .replace(hour=23) \
            .replace(minute=59) - timedelta(days=3)


Stock.trig_ddl = """
    CREATE OR REPLACE FUNCTION check_stock()
    RETURNS TRIGGER AS $$
    BEGIN
      IF
       NOT NEW.available IS NULL
       AND
        (
         (
          SELECT SUM(booking.quantity)
          FROM booking
          WHERE "stockId"=NEW.id
          AND NOT booking."isCancelled"
         ) > NEW.available
        )
      THEN
       RAISE EXCEPTION 'available_too_low'
       USING HINT = 'stock.available cannot be lower than number of bookings';
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

event.listen(Stock.__table__,
             'after_create',
             DDL(Stock.trig_ddl))

Stock.trig_update_date_ddl = """
    CREATE OR REPLACE FUNCTION save_stock_modification_date()
    RETURNS TRIGGER AS $$
    BEGIN
      IF NEW.available != OLD.available THEN
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

event.listen(Stock.__table__,
             'after_create',
             DDL(Stock.trig_update_date_ddl))
