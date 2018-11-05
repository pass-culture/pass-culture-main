""" booking model """
from datetime import datetime
from sqlalchemy import BigInteger, \
    Boolean, \
    Column, \
    DateTime, \
    DDL, \
    event, \
    ForeignKey, \
    Integer, \
    String, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from models.db import Model
from models.pc_object import PcObject
from models.versioned_mixin import VersionedMixin
from utils.human_ids import humanize


class Booking(PcObject,
              Model,
              VersionedMixin):
    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    dateCreated = Column(DateTime,
                         nullable=False,
                         default=datetime.utcnow)

    recommendationId = Column(BigInteger,
                              ForeignKey("recommendation.id"))

    recommendation = relationship('Recommendation',
                                  foreign_keys=[recommendationId],
                                  backref='bookings')

    stockId = Column(BigInteger,
                     ForeignKey("stock.id"),
                     index=True,
                     nullable=False)

    stock = relationship('Stock',
                         foreign_keys=[stockId],
                         backref='bookings')

    quantity = Column(Integer,
                      nullable=False,
                      default=1)

    token = Column(String(6),
                   unique=True,
                   nullable=False)

    userId = Column(BigInteger,
                    ForeignKey('user.id'),
                    index=True,
                    nullable=False)

    user = relationship('User',
                        foreign_keys=[userId],
                        backref='userBookings')

    amount = Column(Numeric(10, 2),
                    nullable=False)

    isCancelled = Column(Boolean,
                         nullable=False,
                         server_default=expression.false(),
                         default=False)

    isUsed = Column(Boolean,
                    nullable=False,
                    default=False)

    @property
    def value(self):
        return self.amount * self.quantity

    @property
    def completedUrl(self):
        offer = self.stock.resolvedOffer
        url = offer.eventOrThing.url
        if url is None:
            return None
        if not url.startswith('http'):
            url = "http://" + url
        return url.replace('{token}', self.token)\
                  .replace('{offerId}', humanize(offer.id))\
                  .replace('{email}', self.user.email)



Booking.trig_ddl = """
    CREATE OR REPLACE FUNCTION get_wallet_balance(user_id BIGINT)
    RETURNS NUMERIC(10,2) AS $$
    BEGIN
        RETURN 
                (SELECT COALESCE(SUM(amount), 0) FROM deposit WHERE "userId"=user_id)
                -
                (SELECT COALESCE(SUM(amount * quantity), 0) FROM booking WHERE "userId"=user_id AND NOT "isCancelled");
    END; $$
    LANGUAGE plpgsql;

    CREATE OR REPLACE FUNCTION check_booking()
    RETURNS TRIGGER AS $$
    BEGIN
      IF EXISTS (SELECT "available" FROM stock WHERE id=NEW."stockId" AND "available" IS NOT NULL)
         AND ((SELECT "available" FROM stock WHERE id=NEW."stockId")
              < (SELECT SUM(quantity) FROM booking WHERE "stockId"=NEW."stockId" AND NOT "isCancelled")) THEN
          RAISE EXCEPTION 'tooManyBookings'
                USING HINT = 'Number of bookings cannot exceed "stock.available"';
      END IF;
      
      IF (SELECT get_wallet_balance(NEW."userId") < 0)
      THEN RAISE EXCEPTION 'insufficientFunds'
                 USING HINT = 'The user does not have enough credit to book';
      END IF;
      
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS booking_update ON booking;
    CREATE CONSTRAINT TRIGGER booking_update AFTER INSERT OR UPDATE
    ON booking
    FOR EACH ROW EXECUTE PROCEDURE check_booking()
    """
event.listen(Booking.__table__,
             'after_create',
             DDL(Booking.trig_ddl))
