from itertools import chain

from datetime import datetime
from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, desc, ForeignKey, String, Text, Integer, Binary, \
    ARRAY, Boolean, false, cast, TEXT, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import coalesce

from domain.keywords import create_tsvector
from models import ExtraDataMixin
from models import DeactivableMixin
from models.db import Model
from models.deactivable_mixin import DeactivableMixin
from models.offer_type import ThingType, EventType
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin
from models.stock import Stock
from models.venue import Venue
from utils.date import DateTimes


class Offer(PcObject,
            Model,
            ExtraDataMixin,
            DeactivableMixin,
            ProvidableMixin):
    thingId = Column(BigInteger,
                     ForeignKey("thing.id"),
                     index=True,
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
                     index=True,
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

    type = Column(String(50),
                  nullable=True)

    name = Column(String(140), nullable=False)

    description = Column(Text, nullable=True)

    conditions = Column(String(120),
                        nullable=True)

    ageMin = Column(Integer,
                    nullable=True)
    ageMax = Column(Integer,
                    nullable=True)

    accessibility = Column(Binary(1),
                           CheckConstraint('("eventId" IS  NULL) OR (accessibility IS NOT NULL)',
                                           name='check_accessibility_not_null_for_event'),
                           nullable=True,
                           default=bytes([0]),

                           )

    url = Column(String(255), nullable=True)

    mediaUrls = Column(ARRAY(String(220)),
                       nullable=False,
                       default=[])

    durationMinutes = Column(Integer,
                             CheckConstraint('("eventId" IS NULL) OR ("durationMinutes" IS NOT NULL)',
                                             name='check_duration_minutes_not_null_for_event'),
                             nullable=True)

    isNational = Column(Boolean,
                        server_default=false(),
                        default=False,
                        nullable=False)

    dateCreated = Column(DateTime,
                         nullable=False,
                         default=datetime.utcnow)

    def errors(self):
        api_errors = super(Offer, self).errors()
        if self.venue:
            venue = self.venue
        else:
            venue = Venue.query.get(self.venueId)
        if self.isDigital and not venue.isVirtual:
            api_errors.addError('venue',
                                'Une offre numérique doit obligatoirement être associée au lieu "Offre en ligne"')
        elif not self.isDigital and venue.isVirtual:
            api_errors.addError('venue', 'Une offre physique ne peut être associée au lieu "Offre en ligne"')
        if self.isDigital and self._type_can_only_be_offline():
            api_errors.addError('url', 'Une offre de type {} ne peut pas être numérique'.format(
                self._get_label_from_type_string()))
        return api_errors

    def updatewith_thing_or_event_data(self, thing_or_event_dict: dict):
        self.populateFromDict(thing_or_event_dict)
        owning_offerer = self.eventOrThing.owningOfferer
        if owning_offerer and owning_offerer == self.venue.managingOfferer:
            self.eventOrThing.populateFromDict(thing_or_event_dict)

    @property
    def dateRange(self):
        if self.thing or not self.stocks:
            return DateTimes()

        start = min([stock.beginningDatetime for stock in self.stocks])
        end = max([stock.endDatetime for stock in self.stocks])
        return DateTimes(start, end)

    @property
    def eventOrThing(self):
        return self.event or self.thing

    @property
    def lastStock(self):
        query = Stock.queryNotSoftDeleted()
        return query.join(Offer) \
            .filter(Offer.id == self.id) \
            .order_by(desc(Stock.bookingLimitDatetime)) \
            .first()

    @property
    def hasActiveMediation(self):
        return any(map(lambda m: m.isActive, self.mediations))

    @property
    def offerType(self):
        all_types = list(ThingType) + list(EventType)
        for possible_type in all_types:
            if str(possible_type) == self.type:
                return possible_type.as_dict()

    @property
    def isDigital(self):
        return self.url is not None and self.url != ''

    def _type_can_only_be_offline(self):
        offline_only_things = filter(lambda thing_type: thing_type.value['offlineOnly'], ThingType)
        offline_only_types_for_things = map(lambda x: x.__str__(), offline_only_things)
        return self.type in offline_only_types_for_things

    def _get_label_from_type_string(self):
        matching_type_thing = next(filter(lambda thing_type: str(thing_type) == self.type, ThingType))
        return matching_type_thing.value['label']


Offer.__ts_vector__ = create_tsvector(
    cast(coalesce(Offer.name, ''), TEXT),
    coalesce(Offer.extraData['author'].cast(TEXT), ''),
    coalesce(Offer.extraData['byArtist'].cast(TEXT), ''),
    cast(coalesce(Offer.description, ''), TEXT),
)

Offer.__table_args__ = (
    Index(
        'idx_offer_fts',
        Offer.__ts_vector__,
        postgresql_using='gin'
    ),
)
