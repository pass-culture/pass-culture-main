""" offer """
from datetime import datetime, timedelta
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import BigInteger,\
                       CheckConstraint,\
                       Column,\
                       DateTime,\
                       DDL,\
                       event,\
                       ForeignKey,\
                       Integer,\
                       Numeric    
from sqlalchemy.orm import relationship

from models.db import Model
from models.deactivable_mixin import DeactivableMixin
from models.event_occurence import EventOccurence
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin

class Offer(PcObject,
            Model,
            DeactivableMixin,
            ProvidableMixin):

    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    # an offer is either linked to a thing or to an eventOccurence

    dateModified = Column(DateTime,
                          nullable=False,
                          default=datetime.utcnow)

    eventOccurenceId = Column(BigInteger,
                              ForeignKey("event_occurence.id"),
                              CheckConstraint('"eventOccurenceId" IS NOT NULL OR "thingId" IS NOT NULL',
                                                    name='check_offer_has_event_occurence_or_thing'),
                              index=True,
                              nullable=True)

    eventOccurence = relationship('EventOccurence',
                                  foreign_keys=[eventOccurenceId],
                                  backref='offers')

    thingId = Column(BigInteger,
                     ForeignKey("thing.id"),
                     index=True,
                     nullable=True)

    thing = relationship('Thing',
                         foreign_keys=[thingId],
                         backref='offers')

    venueId = Column(BigInteger,
                     ForeignKey("venue.id"),
                     CheckConstraint('("venueId" IS NOT NULL AND "eventOccurenceId" IS NULL)'
                                           + 'OR ("venueId" IS NULL AND "eventOccurenceId" IS NOT NULL)',
                                           name='check_offer_has_venue_xor_event_occurence'),
                        index=True,
                        nullable=True)

    venue = relationship('Venue',
                         foreign_keys=[venueId],
                         backref='offers')

    offererId = Column(BigInteger,
                       ForeignKey("offerer.id"),
                       index=True,
                       nullable=False)

    offerer = relationship('Offerer',
                           foreign_keys=[offererId],
                           backref='offers')

    price = Column(Numeric(10, 2),
                   nullable=False)

    available = Column(Integer,
                       index=True,
                       nullable=True)

    # TODO: add pmr
    #pmrGroupSize = Column(db.Integer,
    #                         nullable=False,
    #                         default=1)

    groupSize = Column(Integer,
                       nullable=False,
                       default=1)

    bookingLimitDatetime = Column(DateTime,
                                  nullable=True)

    bookingRecapSent = Column(DateTime,
                              nullable=True)

    @hybrid_property
    def object(self):
        return self.thing or self.eventOccurence


@event.listens_for(Offer, 'before_insert')
def page_defaults(mapper, configuration, target):
    # `bookingLimitDatetime` defaults to midnight before `beginningDatetime`
    # for eventOccurences
    if target.eventOccurenceId and not target.bookingLimitDatetime:
        eventOccurence = target.eventOccurence
        if eventOccurence is None:
            eventOccurence = EventOccurence\
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
