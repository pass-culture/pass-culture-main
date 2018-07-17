from models.deactivable_mixin import DeactivableMixin
from models.pc_object import PcObject
from models.versioned_mixin import VersionedMixin

""" booking model """
from datetime import datetime
from sqlalchemy import event, DDL
from flask_sqlalchemy import Model
import sqlalchemy as db


class Booking(PcObject,
              Model,
              DeactivableMixin,
              VersionedMixin):

    id = db.Column(db.BigInteger,
                   primary_key=True,
                   autoincrement=True)

    dateModified = db.Column(db.DateTime,
                             nullable=False,
                             default=datetime.utcnow)

    recommendationId = db.Column(db.BigInteger,
                                db.ForeignKey("recommendation.id"))

    recommendation = db.orm.relationship('Recommendation',
                                     foreign_keys=[recommendationId],
                                     backref='bookings')

    offerId = db.Column(db.BigInteger,
                        db.ForeignKey("offer.id"),
                        index=True,
                        nullable=True)

    offer = db.orm.relationship('Offer',
                            foreign_keys=[offerId],
                            backref='bookings')

    quantity = db.Column(db.Integer,
                         nullable=False,
                         default=1)

    token = db.Column(db.String(6),
                      unique=True,
                      nullable=False)

    userId = db.Column(db.BigInteger,
                       db.ForeignKey('user.id'),
                       index=True,
                       nullable=False)

    user = db.orm.relationship('User',
                           foreign_keys=[userId],
                           backref='userBookings')

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
