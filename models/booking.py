""" booking model """
from datetime import datetime
from sqlalchemy import BigInteger, \
    Column, \
    DateTime, \
    DDL, \
    event, \
    ForeignKey, \
    Integer, \
    String, Numeric
from sqlalchemy.orm import relationship

from models.db import Model
from models.deactivable_mixin import DeactivableMixin
from models.pc_object import PcObject
from models.versioned_mixin import VersionedMixin


class Booking(PcObject,
              Model,
              DeactivableMixin,
              VersionedMixin):
    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    dateModified = Column(DateTime,
                          nullable=False,
                          default=datetime.utcnow)

    recommendationId = Column(BigInteger,
                              ForeignKey("recommendation.id"))

    recommendation = relationship('Recommendation',
                                  foreign_keys=[recommendationId],
                                  backref='bookings')

    offerId = Column(BigInteger,
                     ForeignKey("offer.id"),
                     index=True,
                     nullable=True)

    offer = relationship('Offer',
                         foreign_keys=[offerId],
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

    @property
    def eventOccurenceBeginningDatetime(self):
        offer = self.offer
        if offer.thingId:
            return None
        return offer.eventOccurence.beginningDatetime


trig_ddl = DDL("""
    CREATE OR REPLACE FUNCTION check_booking()
    RETURNS TRIGGER AS $$
    BEGIN
      IF EXISTS (SELECT "available" FROM offer WHERE id=NEW."offerId" AND "available" IS NOT NULL)
         AND ((SELECT "available" FROM offer WHERE id=NEW."offerId")
              < (SELECT COUNT(*) FROM booking WHERE "offerId"=NEW."offerId")) THEN
          RAISE EXCEPTION 'tooManyBookings'
                USING HINT = 'Number of bookings cannot exceed "offer.available"';
      END IF;
      
      IF (
        SELECT (
          (SELECT COALESCE(SUM(AMOUNT), 0) FROM deposit WHERE "userId"=NEW."userId")
          -
          (SELECT COALESCE(SUM(AMOUNT), 0) FROM booking WHERE "userId"=NEW."userId")
        ) < 0
      )
      THEN RAISE EXCEPTION 'insufficientFunds'
                 USING HINT = 'The user does not have enough credit to book';
      END IF;
      
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE CONSTRAINT TRIGGER booking_update AFTER INSERT OR UPDATE
    ON booking
    FOR EACH ROW EXECUTE PROCEDURE check_booking()
    """)
event.listen(Booking.__table__,
             'after_create',
             trig_ddl)