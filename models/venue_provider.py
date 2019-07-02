""" venue provider """
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from models.db import Model
from models.deactivable_mixin import DeactivableMixin
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin


class VenueProvider(PcObject,
                    Model,
                    ProvidableMixin,
                    DeactivableMixin):

    venueId = Column(BigInteger,
                     ForeignKey('venue.id'),
                     nullable=False,
                     index=True)

    venue = relationship('Venue',
                         back_populates="venueProviders",
                         foreign_keys=[venueId])

    providerId = Column(BigInteger,
                        ForeignKey('provider.id'),
                        nullable=False)

    provider = relationship('Provider',
                            back_populates="venueProviders",
                            foreign_keys=[providerId])

    venueIdAtOfferProvider = Column(String(70))

    lastSyncDate = Column(DateTime,
                          nullable=True)

    @property
    def nOffers(self):
        number_of_offers_created_or_updated_by_this_provider = 0
        for offer in self.venue.offers:
            if offer.lastProviderId == self.providerId:
                number_of_offers_created_or_updated_by_this_provider += 1
        return number_of_offers_created_or_updated_by_this_provider
