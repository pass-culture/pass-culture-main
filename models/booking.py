""" booking model """
from datetime import datetime
from sqlalchemy import BigInteger,\
                       Column,\
                       DateTime,\
                       DDL,\
                       event,\
                       ForeignKey,\
                       Integer,\
                       String
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

    @property
    def eventOccurenceBeginningDatetime(self):
        offer = self.offer
        if offer.thingId:
            return None
        return offer.eventOccurence.beginningDatetime

    userId = Column(BigInteger,
                    ForeignKey('user.id'),
                    index=True,
                    nullable=False)

    user = relationship('User',
                        foreign_keys=[userId],
                        backref='userBookings')

trig_ddl = DDL("""
    CREATE OR REPLACE FUNCTION check_booking()
    RETURNS TRIGGER AS $$
    BEGIN
      IF EXISTS (SELECT "available" FROM offer WHERE id=NEW."offerId" AND "available" IS NOT NULL)
         AND ((SELECT "available" FROM offer WHERE id=NEW."offerId")
              < (SELECT COUNT(*) FROM booking WHERE "offerId"=NEW."offerId")) THEN
          RAISE EXCEPTION 'Offer has too many bookings'
                USING HINT = 'Number of bookings cannot exceed "offer.available"';
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
