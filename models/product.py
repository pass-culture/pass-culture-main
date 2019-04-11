""" model product """
from enum import Enum

from sqlalchemy import Binary, \
    BigInteger, \
    Boolean, \
    Column, \
    Index, \
    Integer, \
    String, \
    Text, \
    TEXT, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import cast, false
from sqlalchemy.sql.functions import coalesce

from domain.keywords import create_tsvector
from models.offer_type import EventType, ThingType
from models.db import Model
from models.extra_data_mixin import ExtraDataMixin
from models.has_thumb_mixin import HasThumbMixin
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin


class Product(PcObject,
              Model,
              ExtraDataMixin,
              HasThumbMixin,
              ProvidableMixin):
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

    mediaUrls = Column(ARRAY(String(220)),
                       nullable=False,
                       default=[])

    url = Column(String(255), nullable=True)

    durationMinutes = Column(Integer, nullable=True)

    isNational = Column(Boolean,
                        server_default=false(),
                        default=False,
                        nullable=False)

    owningOffererId = Column(BigInteger,
                             ForeignKey("offerer.id"),
                             nullable=True)

    owningOfferer = relationship('Offerer',
                                 foreign_keys=[owningOffererId],
                                 backref='events')


    @property
    def offerType(self):
        all_types = list(ThingType) + list(EventType)
        for possible_type in all_types:
            if str(possible_type) == self.type:
                return possible_type.as_dict()

    @property
    def isDigital(self):
        return self.url is not None and self.url != ''


Product.__ts_vector__ = create_tsvector(
    cast(coalesce(Product.name, ''), TEXT),
    cast(coalesce(Product.description, ''), TEXT),
    coalesce(Product.extraData['author'].cast(TEXT), ''),
    coalesce(Product.extraData['byArtist'].cast(TEXT), '')
)

Product.__table_args__ = (
    Index(
        'idx_product_fts',
        Product.__ts_vector__,
        postgresql_using='gin'
    ),
)
