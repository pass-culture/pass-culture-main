import enum

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import false
from sqlalchemy.sql.expression import true

from pcapi.models.db import Model
from pcapi.models.extra_data_mixin import ExtraDataMixin
from pcapi.models.has_thumb_mixin import HasThumbMixin
from pcapi.models.offer_type import EventType
from pcapi.models.offer_type import ThingType
from pcapi.models.pc_object import PcObject
from pcapi.models.providable_mixin import ProvidableMixin


class BookFormat(enum.Enum):
    REVUE = "REVUE"
    BANDE_DESSINEE = "BANDE DESSINEE "
    BEAUX_LIVRES = "BEAUX LIVRES"
    POCHE = "POCHE"
    LIVRE_CASSETTE = "LIVRE + CASSETTE"
    LIVRE_AUDIO = "LIVRE + CD AUDIO"
    MOYEN_FORMAT = "MOYEN FORMAT"


class Product(PcObject, Model, ExtraDataMixin, HasThumbMixin, ProvidableMixin):

    type = Column(String(50), CheckConstraint("type != 'None'"), nullable=False)

    name = Column(String(140), nullable=False)

    description = Column(Text, nullable=True)

    conditions = Column(String(120), nullable=True)

    ageMin = Column(Integer, nullable=True)
    ageMax = Column(Integer, nullable=True)

    mediaUrls = Column(ARRAY(String(220)), nullable=False, default=[])

    url = Column(String(255), nullable=True)

    durationMinutes = Column(Integer, nullable=True)

    isGcuCompatible = Column(Boolean, default=True, server_default=true(), nullable=False)

    isNational = Column(Boolean, server_default=false(), default=False, nullable=False)

    owningOffererId = Column(BigInteger, ForeignKey("offerer.id"), nullable=True)

    owningOfferer = relationship("Offerer", foreign_keys=[owningOffererId], backref="events")

    subcategoryId = Column(Text, nullable=True, index=True)

    @property
    def offerType(self):
        all_types = list(ThingType) + list(EventType)
        for possible_type in all_types:
            if str(possible_type) == self.type:
                return possible_type.as_dict()
        # FIXME (dbaty, 2020-12-03): shouldn't we raise an error such as
        #     raise ValueError(f"Unexpected offer type '{self.type}'")
        # instead of returning None?
        return None

    @property
    def isDigital(self):
        return self.url is not None and self.url != ""

    def is_offline_only(self):
        offline_only_products = filter(lambda product_type: product_type.value["offlineOnly"], ThingType)
        offline_only_types_for_products = map(lambda x: x.__str__(), offline_only_products)
        return self.type in offline_only_types_for_products

    def get_label_from_type_string(self):
        matching_type_product = next(filter(lambda product_type: product_type.__str__() == self.type, ThingType))
        return matching_type_product.value["proLabel"]
