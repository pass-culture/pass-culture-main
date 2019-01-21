""" offer model """
from datetime import datetime
from itertools import chain

from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, desc, ForeignKey, String
from sqlalchemy.orm import relationship

from models import DeactivableMixin, EventOccurrence
from models.db import Model
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin
from models.stock import Stock
from models.venue import Venue
from utils.date import DateTimes


class Offer(PcObject,
            Model,
            DeactivableMixin,
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
                         '("eventId" IS NOT NULL AND "thingId" IS NULL)' + \
                         'OR ("eventId" IS NULL AND "thingId" IS NOT NULL)',
                         name='check_offer_has_thing_xor_event'),
                     nullable=True)

    event = relationship('Event',
                         foreign_keys=[eventId],
                         backref='offers')

    venueId = Column(BigInteger,
                     ForeignKey("venue.id"),
                     nullable=False,
                     index=True)

    venue = relationship('Venue',
                         foreign_keys=[venueId],
                         backref='offers')

    bookingEmail = Column(String(120), nullable=True)

    def errors(self):
        api_errors = super(Offer, self).errors()
        thing = self.thing
        if self.venue:
            venue = self.venue
        else:
            venue = Venue.query.get(self.venueId)
        if thing and thing.url and not venue.isVirtual:
            api_errors.addError('venue',
                                'Une offre numérique doit obligatoirement être associée au lieu "Offre en ligne"')
        return api_errors

    @property
    def dateRange(self):
        if self.thing or not self.eventOccurrences:
            return DateTimes()

        start = min([occurrence.beginningDatetime for occurrence in self.eventOccurrences])
        end = max([occurrence.endDatetime for occurrence in self.eventOccurrences])
        return DateTimes(start, end)

    @property
    def eventOrThing(self):
        return self.event or self.thing

    @property
    def stocks(self):
        if self.thing:
            return self.thingStocks
        elif self.event:
            return list(chain(*map(lambda eo: eo.stocks,
                                   self.eventOccurrences)))
        else:
            return []

    @property
    def lastStock(self):
        query = Stock.queryNotSoftDeleted()
        if self.eventId:
            query = query.join(EventOccurrence)
        return query.join(Offer) \
            .filter(Offer.id == self.id) \
            .order_by(desc(Stock.bookingLimitDatetime)) \
            .first()

    @property
    def hasActiveMediation(self):
        return any(map(lambda m: m.isActive, self.mediations))
