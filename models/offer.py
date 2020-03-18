from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy import and_, ARRAY, Boolean, CheckConstraint, false, Integer, Text, TEXT
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.sql import select, func

from domain.bookings import filter_bookings_to_compute_remaining_stock
from domain.keywords import create_ts_vector_and_table_args
from models.criterion import Criterion
from models.db import db, Model
from models.deactivable_mixin import DeactivableMixin
from models.extra_data_mixin import ExtraDataMixin
from models.mediation import Mediation
from models.offer_criterion import OfferCriterion
from models.offer_type import ThingType, EventType, ProductType, Category
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin
from models.stock import Stock
from models.versioned_mixin import VersionedMixin
from utils.date import DateTimes
from utils.string_processing import pluralize


class Offer(PcObject,
            Model,
            ExtraDataMixin,
            DeactivableMixin,
            ProvidableMixin,
            VersionedMixin):
    # We redefine this so we can reference it in the baseScore column_property
    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

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
                  CheckConstraint("type != 'None'"),
                  index=True,
                  nullable=False)

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

    isDuo = Column(Boolean,
                   server_default=false(),
                   default=False,
                   nullable=False)

    dateCreated = Column(DateTime,
                         nullable=False,
                         default=datetime.utcnow)

    baseScore = column_property(
        select([func.coalesce(func.sum(Criterion.scoreDelta), 0)]).
            where(and_(Criterion.id == OfferCriterion.criterionId,
                       (OfferCriterion.offerId == id))
                  )
    )

    criteria = relationship('Criterion',
                            backref=db.backref('criteria', lazy='dynamic'),
                            secondary='offer_criterion')

    def update_with_product_data(self, product_dict: dict):
        owning_offerer = self.product.owningOfferer
        if owning_offerer and owning_offerer == self.venue.managingOfferer:
            self.product.populate_from_dict(product_dict)

    @property
    def activeMediation(self) -> Optional[Mediation]:
        sorted_by_date_desc = sorted(self.mediations, key=lambda m: m.dateCreated, reverse=True)
        only_active = list(filter(lambda m: m.isActive, sorted_by_date_desc))
        return only_active[0] if only_active else None

    @property
    def dateRange(self) -> DateTimes:
        if ProductType.is_thing(self.type) or not self.activeStocks:
            return DateTimes()

        start = min([stock.beginningDatetime for stock in self.activeStocks])
        end = max([stock.endDatetime for stock in self.activeStocks])
        return DateTimes(start, end)

    @property
    def isEvent(self) -> bool:
        return ProductType.is_event(self.type)

    @property
    def isThing(self) -> bool:
        return ProductType.is_thing(self.type)

    @property
    def isDigital(self) -> bool:
        return self.url is not None and self.url != ''

    @property
    def isEditable(self) -> bool:
        local_class = self.lastProvider.localClass if self.lastProvider else ''
        return self.isFromProvider is False or 'Allocine' in local_class

    @property
    def isFromProvider(self) -> bool:
        return self.lastProviderId is not None

    @property
    def isBookable(self) -> bool:
        for stock in self.stocks:
            if stock.isBookable:
                return True
        return False

    @property
    def hasBookingLimitDatetimesPassed(self) -> bool:
        return all(map(lambda stock: stock.hasBookingLimitDatetimePassed, self.stocks))

    @property
    def isFullyBooked(self) -> bool:
        has_unlimited_stock = any(map(lambda stock: stock.available is None, self.stocks))
        if has_unlimited_stock:
            return False

        bookable_stocks = list(filter(lambda stock: stock.isBookable, self.stocks))
        total_booked_quantity = 0

        for stock in bookable_stocks:
            bookings = filter_bookings_to_compute_remaining_stock(stock)
            total_booked_quantity += sum(map(lambda booking: booking.quantity, bookings))

        available_stocks = sum(map(lambda stock: stock.available, bookable_stocks))
        return total_booked_quantity >= available_stocks

    @property
    def activeStocks(self) -> List[Stock]:
        return [stock for stock in self.stocks if not stock.isSoftDeleted]

    @property
    def offerType(self) -> Optional[dict]:
        all_types = list(ThingType) + list(EventType)
        for possible_type in all_types:
            if str(possible_type) == self.type:
                return possible_type.as_dict()

    @property
    def offer_category(self) -> str:
        for category in Category:
            if self.offerType['appLabel'] in category.value:
                return category.name

    @property
    def availabilityMessage(self) -> str:
        if not self.activeStocks:
            return 'Pas encore de stock'

        incoming_stocks = list(filter(lambda stock: not stock.hasBookingLimitDatetimePassed, self.activeStocks))
        if not incoming_stocks:
            return 'Stock expiré'

        offer_has_at_least_one_unlimited_stock = any(map(lambda stock: stock.available is None, incoming_stocks))
        if offer_has_at_least_one_unlimited_stock:
            return 'Stock restant illimité'

        stocks_remaining_quantity = sum(map(lambda stock: stock.remainingQuantity, incoming_stocks))

        if stocks_remaining_quantity == 0:
            return 'Plus de stock restant'

        count_stocks_with_no_remaining_quantity = len(
            list(filter(lambda stock: stock.remainingQuantity == 0, incoming_stocks)))
        has_at_least_one_stock_with_remaining_quantity = count_stocks_with_no_remaining_quantity != len(incoming_stocks)

        if has_at_least_one_stock_with_remaining_quantity and count_stocks_with_no_remaining_quantity > 0:
            return f"Plus de stock restant pour" \
                   f" {count_stocks_with_no_remaining_quantity}" \
                   f" {pluralize(count_stocks_with_no_remaining_quantity, 'date')}"

        return f"Encore {stocks_remaining_quantity}" \
               f" {pluralize(stocks_remaining_quantity, 'stock')}" \
               f" {pluralize(stocks_remaining_quantity, 'restant')}"

    @property
    def thumb_url(self) -> str:
        offer_has_active_mediation = any(map(lambda mediation: mediation.isActive, self.mediations))
        if offer_has_active_mediation:
            return self.activeMediation.thumbUrl
        if self.product:
            return self.product.thumbUrl
        return ''

    @property
    def is_offline_only(self) -> bool:
        offline_thing = [thing_type for thing_type in ThingType if
                         self._is_same_type(thing_type) and self._is_offline_type_only(thing_type)]

        return len(list(offline_thing)) == 1

    def _is_same_type(self, thing_type):
        return str(thing_type) == self.type

    def _is_offline_type_only(self, thing_type):
        return thing_type.value['offlineOnly']

    def get_label_from_type_string(self):
        matching_type_thing = next(filter(lambda thing_type: str(thing_type) == self.type, ThingType))
        return matching_type_thing.value['proLabel']


ts_indexes = [('idx_offer_fts_name', Offer.name),
              ('idx_offer_fts_author', Offer.extraData['author'].cast(TEXT)),
              ('idx_offer_fts_byArtist', Offer.extraData['byArtist'].cast(TEXT)),
              ('idx_offer_fts_description', Offer.description)]

(Offer.__ts_vectors__, Offer.__table_args__) = create_ts_vector_and_table_args(ts_indexes)
