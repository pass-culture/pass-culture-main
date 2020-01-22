import enum

from sqlalchemy import BigInteger, \
    Boolean, \
    CheckConstraint, \
    Column, \
    ForeignKey, \
    Integer, \
    String, \
    Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import false

from models.db import Model
from models.extra_data_mixin import ExtraDataMixin
from models.has_thumb_mixin import HasThumbMixin
from models.offer_type import EventType, ThingType
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin


class BookFormat(enum.Enum):
    REVUE = "REVUE"
    BANDE_DESSINEE = "BANDE DESSINEE "
    BEAUX_LIVRES = "BEAUX LIVRES"
    POCHE = "POCHE"
    LIVRE_CASSETTE = "LIVRE + CASSETTE"
    LIVRE_AUDIO = "LIVRE + CD AUDIO"
    MOYEN_FORMAT = "MOYEN FORMAT"


class Product(PcObject,
              Model,
              ExtraDataMixin,
              HasThumbMixin,
              ProvidableMixin):

    type = Column(String(50),
                  CheckConstraint("type != 'None'"),
                  nullable=False)

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

    def type_can_only_be_offline(self):
        offline_only_products = filter(
            lambda product_type: product_type.value['offlineOnly'], ThingType)
        offline_only_types_for_products = map(
            lambda x: x.__str__(), offline_only_products)
        return self.type in offline_only_types_for_products

    def get_label_from_type_string(self):
        matching_type_product = next(
            filter(lambda product_type: product_type.__str__() == self.type, ThingType))
        return matching_type_product.value['proLabel']
