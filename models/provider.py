""" provider """
from sqlalchemy import BigInteger, \
    CheckConstraint, \
    Column, \
    DateTime, \
    String
from sqlalchemy.dialects.postgresql import CHAR
from sqlalchemy.orm import relationship

from models.deactivable_mixin import DeactivableMixin
from models.pc_object import PcObject
from models.venue_provider import VenueProvider


class Provider(PcObject, DeactivableMixin):

    id = Column(BigInteger,
                primary_key=True)

    name = Column(String(60),
                  nullable=False)

    localClass = Column(String(30),
                        CheckConstraint('("localClass" IS NOT NULL AND "apiKey" IS NULL)'
                                              + 'OR ("localClass" IS NULL AND "apiKey" IS NOT NULL)',
                                              name='check_provider_has_localclass_or_apikey'),
                           nullable=True,
                           unique=True)

    venueProviders = relationship(VenueProvider,
                                  back_populates="provider",
                                  foreign_keys=[VenueProvider.providerId])

    apiKey = Column(CHAR(32),
                    nullable=True)

    apiKeyGenerationDate = Column(DateTime,
                                  nullable=True)

    def getByClassName(name):
        return Provider.query\
                       .filter_by(localClass=name)\
                       .first()
