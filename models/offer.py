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
                             default=datetime.utcnow)

    eventOccurenceId = db.Column(db.BigInteger,
                                 db.ForeignKey("event_occurence.id"),
                                 db.CheckConstraint('"eventOccurenceId" IS NOT NULL OR "thingId" IS NOT NULL',
                                                    name='check_offer_has_event_occurence_or_thing'),
                                 index=True,
                                 nullable=True)

    eventOccurence = db.relationship(lambda: app.model.EventOccurence,
                                     foreign_keys=[eventOccurenceId],
                                     backref='offers')

    thingId = db.Column(db.BigInteger,
                        db.ForeignKey("thing.id"),
                        index=True,
                        nullable=True)

    thing = db.relationship(lambda: app.model.Thing,
                            foreign_keys=[thingId],
                            backref='offers')

    venueId = db.Column(db.BigInteger,
                        db.ForeignKey("venue.id"),
                        db.CheckConstraint('("venueId" IS NOT NULL AND "eventOccurenceId" IS NULL)'
                                           + 'OR ("venueId" IS NULL AND "eventOccurenceId" IS NOT NULL)',
                                           name='check_offer_has_venue_xor_event_occurence'),
                        index=True,
                        nullable=True)

    venue = db.relationship(lambda: app.model.Venue,
                            foreign_keys=[venueId],
                            backref='offers')

    offererId = db.Column(db.BigInteger,
                          db.ForeignKey("offerer.id"),
                          index=True,
                          nullable=False)

    offerer = db.relationship(lambda: app.model.Offerer,
                              foreign_keys=[offererId],
                              backref='offers')

    price = db.Column(db.Numeric(10, 2),
                      nullable=False)

    available = db.Column(db.Integer,
                          index=True,
                          nullable=True)

    # TODO: add pmr
    #pmrGroupSize = db.Column(db.Integer,
    #                         nullable=False,
    #                         default=1)

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
        eventOccurence = target.eventOccurence
        if eventOccurence is None:
            eventOccurence = app.model.EventOccurence\
                                      .query\
                                      .filter_by(id=target.eventOccurenceId)\
                                      .first_or_404()
        target.bookingLimitDatetime = eventOccurence.beginningDatetime\
                                                    .replace(hour=23)\
                                                    .replace(minute=59) - timedelta(days=3)


trig_ddl = DDL("""
    CREATE OR REPLACE FUNCTION check_offer()
    RETURNS TRIGGER AS $$
    BEGIN
      IF NOT NEW.available IS NULL AND
      ((SELECT COUNT(*) FROM booking WHERE "offerId"=NEW.id) > NEW.available) THEN
        RAISE EXCEPTION 'available_too_low'
              USING HINT = 'offer.available cannot be lower than number of bookings';
      END IF;
      
      IF NOT NEW."bookingLimitDatetime" IS NULL AND
      (NEW."bookingLimitDatetime" > (SELECT "beginningDatetime" FROM event_occurence WHERE id=NEW."eventOccurenceId")) THEN
      
      RAISE EXCEPTION 'bookingLimitDatetime_too_late'
      USING HINT = 'offer.bookingLimitDatetime after event_occurence.beginningDatetime';
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
