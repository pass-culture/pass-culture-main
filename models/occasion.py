""" occasion model """
from datetime import datetime
from itertools import chain
from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, desc, ForeignKey
from sqlalchemy.orm import aliased, relationship

from models import Event, EventOccurence
from models.offer import Offer
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

    @property
    def thing_or_event(self):
        return self.thing or self.event

    @property
    def offers(self):
        if self.thingId:
            return self.thing.offers
        elif self.eventId:
            return chain(map(lambda eo: eo.offers,
                             self.event.eventOccurence))
        else:
            return []

    @property
    def lastOffer(self):
        query = Offer.query
        if self.eventId:
            query = query.join(EventOccurence)
        return query.join(Occasion)\
                    .filter(Occasion.id == self.id)\
                    .order_by(desc(Offer.bookingLimitDatetime))\
                    .first()

    @staticmethod
    def joinWithAliasedOffer(query, occasionType):
        query = Occasion.query
        if occasionType == Event:
            query = query.filter(Occasion.eventId != None)\
                         .join(aliased(EventOccurence))
        else:
            query = query.filter(Occasion.thingId != None)\
                         .join(aliased(EventOccurence))
        offer_alias = aliased(Offer)
        return query.join(offer_alias), offer_alias
