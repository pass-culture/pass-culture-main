from datetime import datetime
from typing import List, Optional

from sqlalchemy import ARRAY, Boolean, CheckConstraint, false, Integer, Text
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from pcapi.domain.ts_vector import create_ts_vector, create_fts_index
from pcapi.models.db import db, Model
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.extra_data_mixin import ExtraDataMixin
from pcapi.models.mediation_sql_entity import MediationSQLEntity
from pcapi.models.offer_type import ThingType, EventType, ProductType, Category
from pcapi.models.pc_object import PcObject
from pcapi.models.providable_mixin import ProvidableMixin
from pcapi.models.stock_sql_entity import StockSQLEntity
from pcapi.models.versioned_mixin import VersionedMixin
from pcapi.utils.date import DateTimes


class Offer(PcObject,
                     Model,
                     ExtraDataMixin,
                     DeactivableMixin,
                     ProvidableMixin,
                     VersionedMixin):
    __tablename__ = 'offer'

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

    venue = relationship('VenueSQLEntity',
                         foreign_keys=[venueId],
                         backref='offers')

    bookingEmail = Column(String(120), nullable=True)

    type = Column(String(50),
                  CheckConstraint("type != 'None'"),
                  index=True,
                  nullable=False)

    name = Column(String(140), nullable=False)

    description = Column(Text, nullable=True)

    withdrawalDetails = Column(Text, nullable=True)

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

    criteria = relationship('Criterion',
                            backref=db.backref('criteria', lazy='dynamic'),
                            secondary='offer_criterion')

    def update_with_product_data(self, product_dict: dict) -> None:
        owning_offerer = self.product.owningOfferer
        if owning_offerer and owning_offerer == self.venue.managingOfferer:
            self.product.populate_from_dict(product_dict)

    @property
    def activeMediation(self) -> Optional[MediationSQLEntity]:
        sorted_by_date_desc = sorted(self.mediations, key=lambda m: m.dateCreated, reverse=True)
        only_active = list(filter(lambda m: m.isActive, sorted_by_date_desc))
        return only_active[0] if only_active else None

    @property
    def dateRange(self) -> DateTimes:
        if ProductType.is_thing(self.type) or not self.activeStocks:
            return DateTimes()

        start = min([stock.beginningDatetime for stock in self.activeStocks])
        end = max([stock.beginningDatetime for stock in self.activeStocks])
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
        if self.activeStocks:
            return all([stock.hasBookingLimitDatetimePassed for stock in self.activeStocks])
        return False

    @property
    def activeStocks(self) -> List[StockSQLEntity]:
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
    def thumbUrl(self) -> str:
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

    def _is_same_type(self, thing_type) -> bool:
        return str(thing_type) == self.type

    def _is_offline_type_only(self, thing_type):
        return thing_type.value['offlineOnly']

    def get_label_from_type_string(self):
        matching_type_thing = next(filter(lambda thing_type: str(thing_type) == self.type, ThingType))
        return matching_type_thing.value['proLabel']


Offer.__name_ts_vector__ = create_ts_vector(Offer.name)
Offer.__table_args__ = [create_fts_index('idx_offer_fts_name', Offer.__name_ts_vector__)]
