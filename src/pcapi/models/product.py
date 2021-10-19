import enum

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import false
from sqlalchemy.sql.expression import true

from pcapi.core.categories import subcategories
from pcapi.models.db import Model
from pcapi.models.extra_data_mixin import ExtraDataMixin
from pcapi.models.has_thumb_mixin import HasThumbMixin
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

    subcategoryId = Column(Text, nullable=False, index=True)

    thumb_path_component = "products"

    @property
    def subcategory(self) -> subcategories.Subcategory:
        if self.subcategoryId not in subcategories.ALL_SUBCATEGORIES_DICT:
            raise ValueError(f"Unexpected subcategoryId '{self.subcategoryId}' for product {self.id}")
        return subcategories.ALL_SUBCATEGORIES_DICT[self.subcategoryId]

    @property
    def isDigital(self):
        return self.url is not None and self.url != ""

    @property
    def is_offline_only(self):
        return self.subcategory.online_offline_platform == subcategories.OnlineOfflinePlatformChoices.OFFLINE.value

    @property
    def is_online_only(self):
        return self.subcategory.online_offline_platform == subcategories.OnlineOfflinePlatformChoices.ONLINE.value
