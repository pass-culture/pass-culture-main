""" offer model """
from datetime import datetime, timedelta
from flask import current_app as app
from sqlalchemy import event, DDL
from sqlalchemy.ext.hybrid import hybrid_property

db = app.db


class Offer(app.model.PcObject,
            db.Model,
            app.model.DeactivableMixin,
            app.model.ProvidableMixin):

    id = db.Column(db.BigInteger,
                   primary_key=True,
                   autoincrement=True)

    # an offer is either linked to a thing or to an eventOccurence

    dateModified = db.Column(db.DateTime,
                             nullable=False,
                             default=datetime.now)

    recommendationOffers = db.relationship(lambda: app.model.RecommendationOffer,
                                           back_populates="offer")

    eventOccurenceId = db.Column(db.BigInteger,
                                 db.ForeignKey("event_occurence.id"),
                                 db.CheckConstraint('"eventOccurenceId" IS NOT NULL OR "thingId" IS NOT NULL',
                                                    name='check_offer_has_event_occurence_or_thing'),
                                 nullable=True)

    eventOccurence = db.relationship(lambda: app.model.EventOccurence,
                                     foreign_keys=[eventOccurenceId],
                                     backref='offer')

    thingId = db.Column(db.BigInteger,
                        db.ForeignKey("thing.id"),
                        nullable=True)

    thing = db.relationship(lambda: app.model.Thing,
                            foreign_keys=[thingId])

    venueId = db.Column(db.BigInteger,
                        db.ForeignKey("venue.id"),
                        db.CheckConstraint('("venueId" IS NOT NULL AND "eventOccurenceId" IS NULL)'
                                           + 'OR ("venueId" IS NULL AND "eventOccurenceId" IS NOT NULL)',
                                           name='check_offer_has_venue_xor_event_occurence'),
                        nullable=True)

    venue = db.relationship(lambda: app.model.Venue,
                            foreign_keys=[venueId],
                            backref='offers')

    offererId = db.Column(db.BigInteger,
                          db.ForeignKey("offerer.id"),
                          nullable=False)

    offerer = db.relationship(lambda: app.model.Offerer,
                              foreign_keys=[offererId],
                              backref='offers')

    price = db.Column(db.Numeric(10, 2),
                      nullable=False)

    available = db.Column(db.Integer,
                          nullable=True)

    groupSize = db.Column(db.Integer,
                          nullable=False,
                          default=1)

    bookingLimitDatetime = db.Column(db.DateTime,
                                     nullable=True)

    bookingRecapSent = db.Column(db.DateTime,
                                 nullable=True)

    @hybrid_property
    def object(self):
        return self.thing or self.eventOccurence


app.model.Offer = Offer


@event.listens_for(Offer, 'before_insert')
def page_defaults(mapper, configuration, target):
    # `bookingLimitDatetime` defaults to midnight before `beginningDatetime`
    # for eventOccurences
    if target.eventOccurenceId and not target.bookingLimitDatetime:
        target.bookingLimitDatetime = target.eventOccurence.beginningDatetime.replace(hour=23).replace(minute=59) - timedelta(days=3)


trig_ddl = DDL("""
    CREATE OR REPLACE FUNCTION check_offer()
    RETURNS TRIGGER AS $$
    BEGIN
      IF NOT NEW.available IS NULL AND
      ((SELECT COUNT(*) FROM booking WHERE "offerId"=NEW.id) > NEW.available) THEN
        RAISE EXCEPTION 'Available too low'
              USING HINT = 'offer.available cannot be lower than number of bookings';
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE CONSTRAINT TRIGGER offer_update AFTER INSERT OR UPDATE
    ON offer
    FOR EACH ROW EXECUTE PROCEDURE check_offer()
    """)
event.listen(Offer.__table__,
             'after_create',
             trig_ddl)
