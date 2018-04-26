""" booking model """
from datetime import datetime
from flask import current_app as app
from sqlalchemy import event, DDL

db = app.db


class Booking(app.model.PcObject,
              db.Model,
              app.model.DeactivableMixin,
              app.model.VersionedMixin):

    id = db.Column(db.BigInteger,
                   primary_key=True,
                   autoincrement=True)

    dateModified = db.Column(db.DateTime,
                             nullable=False,
                             default=datetime.now)

    recommendationId = db.Column(db.BigInteger,
                                db.ForeignKey("recommendation.id"))

    recommendation = db.relationship(lambda: app.model.Recommendation,
                                     foreign_keys=[recommendationId])

    offerId = db.Column(db.BigInteger,
                        db.ForeignKey("offer.id"),
                        nullable=True)

    offer = db.relationship(lambda: app.model.Offer,
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
                       nullable=False)

    user = db.relationship(lambda: app.model.User,
                           foreign_keys=[userId],
                           backref='userBookings')


app.model.Booking = Booking

trig_ddl = DDL("""
    CREATE OR REPLACE FUNCTION check_booking()
    RETURNS TRIGGER AS $$
    BEGIN
      IF EXISTS (SELECT "available" FROM offer WHERE id=NEW."offerId" AND "available" IS NOT NULL)
         AND ((SELECT "available" FROM offer WHERE id=NEW."offerId")
              < (SELECT COUNT(*) FROM booking WHERE "offerId"=NEW."offerId")) THEN
          RAISE EXCEPTION 'Offer has too many bookings'
                USING HINT = 'Number of bookings cannot exeed "offer.available"';
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
