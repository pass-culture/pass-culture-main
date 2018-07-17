import sqlalchemy as db

from models.deactivable_mixin import DeactivableMixin
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin

""" event occurence """


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

    event = db.relationship('Event',
                            foreign_keys=[eventId],
                            backref='occurences')

    venueId = db.Column(db.BigInteger,
                        db.ForeignKey("venue.id"),
                        index=True,
                        nullable=True)

    venue = db.relationship('Venue',
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
