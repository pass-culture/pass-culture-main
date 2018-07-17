""" event occurence """
from sqlalchemy import Binary,\
                       BigInteger,\
                       Column,\
                       DateTime,\
                       Enum,\
                       ForeignKey
from sqlalchemy.orm import relationship

from models.db import Model
from models.event import EventType
from models.deactivable_mixin import DeactivableMixin
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin


class EventOccurence(PcObject,
                     Model,
                     DeactivableMixin,
                     ProvidableMixin
                    ):

    id = Column(BigInteger,
                primary_key=True)

    type = Column(Enum(EventType),
                  nullable=True)

    eventId = Column(BigInteger,
                     ForeignKey("event.id"),
                     index=True,
                     nullable=False)

    event = relationship('Event',
                         foreign_keys=[eventId],
                         backref='occurences')

    venueId = Column(BigInteger,
                     ForeignKey("venue.id"),
                     index=True,
                     nullable=True)

    venue = relationship('Venue',
                         foreign_keys=[venueId],
                         backref='eventOccurences')

    beginningDatetime = Column(DateTime,
                               index=True,
                               nullable=False)

    endDatetime = Column(DateTime,
                         nullable=False)

    accessibility = Column(Binary(1),
                           nullable=False,
                           default=bytes([0]))

    @property
    def offer(self):
        return self.offers
