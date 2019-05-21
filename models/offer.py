from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, desc, ForeignKey, String
from sqlalchemy import Text, Integer, ARRAY, Boolean, false, cast, TEXT, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import coalesce

from domain.keywords import create_tsvector
from models import ExtraDataMixin
from models.db import Model
from models.deactivable_mixin import DeactivableMixin
from models.offer_type import ThingType, EventType, ProductType
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

    productId = Column(BigInteger,
                     ForeignKey("product.id"),
                     index=True,
                     nullable=False)

    product = relationship('Product',
                         foreign_keys=[productId],
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

    url = Column(String(255), nullable=True)

    mediaUrls = Column(ARRAY(String(220)),
                       nullable=False,
                       default=[])

    durationMinutes = Column(Integer, nullable=True)

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

        if self.isEvent and not self.durationMinutes:
            api_errors.addError('durationMinutes', 'Une offre de type évènement doit avoir une durée en minute')

        return api_errors

    def updatewith_product_data(self, product_dict: dict):
        owning_offerer = self.product.owningOfferer
        if owning_offerer and owning_offerer == self.venue.managingOfferer:
            self.product.populateFromDict(product_dict)

    @property
    def dateRange(self):
        if ProductType.is_thing(self.type) or not self.stocks:
            return DateTimes()

        start = min([stock.beginningDatetime for stock in self.stocks])
        end = max([stock.endDatetime for stock in self.stocks])
        return DateTimes(start, end)

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
    def isEvent(self):
        return ProductType.is_event(self.type)

    @property
    def isThing(self):
        return ProductType.is_thing(self.type)

    @property
    def isDigital(self):
        return self.url is not None and self.url != ''

    @property
    def isFinished(self):
        return all(map(lambda s: not s.isBookable, self.stocks))

    @property
    def isFullyBooked(self):
        if self._has_unlimited_stock():
            return False

        bookable_stocks = list(filter(lambda s: s.isBookable, self.stocks))
        total_quantity = 0

        for stock in bookable_stocks:
            bookings = filter(lambda b: not b.isCancelled, stock.bookings)
            total_quantity += sum(map(lambda s: s.quantity, bookings))

        available_stocks = sum(map(lambda s: s.available if s.isBookable else 0, self.stocks))
        return total_quantity >= available_stocks

    def _has_unlimited_stock(self):
        return any(map(lambda s: s.available is None, self.stocks))

    def _type_can_only_be_offline(self):
        offline_only_things = filter(lambda thing_type: thing_type.value['offlineOnly'], ThingType)
        offline_only_types_for_things = map(lambda x: x.__str__(), offline_only_things)
        return self.type in offline_only_types_for_things

    def _get_label_from_type_string(self):
        matching_type_thing = next(filter(lambda thing_type: str(thing_type) == self.type, ThingType))
        return matching_type_thing.value['proLabel']


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
