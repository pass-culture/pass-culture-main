from datetime import datetime, timedelta
from pprint import pformat

from sqlalchemy import BigInteger, \
    Boolean, \
    CheckConstraint, \
    Column, \
    DateTime, \
    DDL, \
    event, \
    ForeignKey, \
    Integer, \
    Numeric
from sqlalchemy.event import listens_for
from sqlalchemy.orm import relationship

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

    quantity = Column(Integer, nullable=True)

    bookingLimitDatetime = Column(DateTime, nullable=True)

    hasBeenMigrated = Column(Boolean, nullable=True)

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
        return 'unlimited' if self.quantity is None else self.quantity - self.bookingsQuantity

    @classmethod
    def queryNotSoftDeleted(cls):
        return Stock.query.filter_by(isSoftDeleted=False)

    @staticmethod
    def restize_internal_error(ie):
        if 'check_stock' in str(ie.orig):
            if 'quantity_too_low' in str(ie.orig):
                return ['quantity', 'Le stock total ne peut être inférieur au nombre de réservations']
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

event.listen(Stock.__table__,
             'after_create',
             DDL(Stock.trig_ddl))

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

event.listen(Stock.__table__,
             'after_create',
             DDL(Stock.trig_update_date_ddl))
