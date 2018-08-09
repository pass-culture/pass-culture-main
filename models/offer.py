""" offer model """
from datetime import datetime
from itertools import chain
from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, desc, ForeignKey
from sqlalchemy.orm import aliased, relationship

from models import Event, EventOccurrence
from models.stock import Stock
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin
from models.db import Model


class Offer(PcObject,
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
                         backref='offers')

    eventId = Column(BigInteger,
                     ForeignKey("event.id"),
                     CheckConstraint(
                         '("eventId" IS NOT NULL AND "thingId" IS NULL)' +\
                         'OR ("eventId" IS NULL AND "thingId" IS NOT NULL)',
                         name='check_offer_has_thing_xor_event'),
                     nullable=True)

    event = relationship('Event',
                         foreign_keys=[eventId],
                         backref='offers')

    venueId = Column(BigInteger,
                     ForeignKey("venue.id"),
                     nullable=True,
                     index=True)

    venue = relationship('Venue',
                         foreign_keys=[venueId],
                         backref='offers')

    @property
    def eventOrThing(self):
        return self.event or self.thing

    @property
    def stocks(self):
        if self.thing:
            return self.thing.stocks
        elif self.event:
            return list(chain(*map(lambda eo: eo.stocks,
                                   self.eventOccurrences)))
        else:
            return []

    @property
    def lastStock(self):
        query = Stock.query
        if self.eventId:
            query = query.join(EventOccurrence)
        return query.join(Offer)\
                    .filter(Offer.id == self.id)\
                    .order_by(desc(Stock.bookingLimitDatetime))\
                    .first()

    @staticmethod
    def joinWithAliasedStock(query, offerType):
        query = Offer.query
        if offerType == Event:
            query = query.filter(Offer.eventId != None)\
                         .join(aliased(EventOccurrence))
        else:
            query = query.filter(Offer.thingId != None)\
                         .join(aliased(EventOccurrence))
        stock_alias = aliased(Stock)
        return query.join(stock_alias), stock_alias
