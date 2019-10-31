from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from models import Offer
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
        return Offer.query \
            .filter(Offer.venueId == self.venueId) \
            .filter(Offer.lastProviderId == self.providerId) \
            .count()
