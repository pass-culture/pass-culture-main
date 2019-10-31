""" venue provider """
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from models.db import Model
from models.deactivable_mixin import DeactivableMixin
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin


class TiteLiveThingThumbProvider(PcObject,
                    Model,
                    ProvidableMixin,
                    DeactivableMixin):

    providerId = Column(BigInteger,
                        ForeignKey('provider.id'),
                        nullable=False)

    provider = relationship('Provider',
                            back_populates="venueProviders",
                            foreign_keys=[providerId])