""" occasion model """
from datetime import datetime
from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from models.db import Model
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin


class Occasion(PcObject,
               Model,
               ProvidableMixin):

    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    dateCreated = Column(DateTime,
                         nullable=False,
                         default=datetime.utcnow)

    thingId = Column(BigInteger,
                     ForeignKey("thing.id"),
                     nullable=True)

    thing = relationship('Thing',
                         foreign_keys=[thingId],
                         backref='occasions')

    eventId = Column(BigInteger,
                     ForeignKey("event.id"),
                     CheckConstraint(
                         '("eventId" IS NOT NULL AND "thingId" IS NULL)' +\
                         'OR ("eventId" IS NULL AND "thingId" IS NOT NULL)',
                         name='check_occasion_has_thing_xor_event'),
                     nullable=True)

    event = relationship('Event',
                         foreign_keys=[eventId],
                         backref='occasions')

    venueId = Column(BigInteger,
                     ForeignKey("venue.id"),
                     nullable=True,
                     index=True)

    venue = relationship('Venue',
                         foreign_keys=[venueId],
                         backref='occasions')
