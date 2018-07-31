""" occasion model """
from datetime import datetime
from itertools import chain
from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, desc, ForeignKey
from sqlalchemy.orm import aliased, relationship

from models import Event, EventOccurrence
from models.stock import Stock
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin
from models.db import Model


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

    @property
    def eventOrThing(self):
        return self.event or self.thing

    @property
    def stocks(self):
        if self.thingId:
            return self.thing.stocks
        elif self.eventId:
            return chain(map(lambda eo: eo.stocks,
                             self.eventOccurrences))
        else:
            return []

    @property
    def lastStock(self):
        query = Stock.query
        if self.eventId:
            query = query.join(EventOccurrence)
        return query.join(Occasion)\
                    .filter(Occasion.id == self.id)\
                    .order_by(desc(Stock.bookingLimitDatetime))\
                    .first()

    @staticmethod
    def joinWithAliasedStock(query, occasionType):
        query = Occasion.query
        if occasionType == Event:
            query = query.filter(Occasion.eventId != None)\
                         .join(aliased(EventOccurrence))
        else:
            query = query.filter(Occasion.thingId != None)\
                         .join(aliased(EventOccurrence))
        stock_alias = aliased(Stock)
        return query.join(stock_alias), stock_alias
