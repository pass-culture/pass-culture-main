""" event occurence """
from flask import current_app as app
from sqlalchemy.ext.hybrid import hybrid_property

db = app.db


class EventOccurence(PcObject,
                     db.Model,
                     DeactivableMixin,
                     ProvidableMixin
                    ):
    id = db.Column(db.BigInteger,
                   primary_key=True)

    type = db.Column(db.Enum(EventType),
                     nullable=True)

    eventId = db.Column(db.BigInteger,
                        db.ForeignKey("event.id"),
                        index=True,
                        nullable=False)

    event = db.relationship(lambda: Event,
                            foreign_keys=[eventId],
                            backref='occurences')

    venueId = db.Column(db.BigInteger,
                        db.ForeignKey("venue.id"),
                        index=True,
                        nullable=True)

    venue = db.relationship(lambda: Venue,
                            foreign_keys=[venueId],
                            backref='eventOccurences')

    beginningDatetime = db.Column(db.DateTime,
                                  index=True,
                                  nullable=False)

    endDatetime = db.Column(db.DateTime,
                            nullable=False)

    accessibility = db.Column(db.Binary(1),
                              nullable=False,
                              default=bytes([0]))

    @property
    def offer(self):
        return self.offers

EventOccurence = EventOccurence
