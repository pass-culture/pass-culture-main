from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, UniqueConstraint
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
                     nullable=False)

    venue = relationship('Venue',
                         back_populates="venueProviders",
                         foreign_keys=[venueId])

    providerId = Column(BigInteger,
                        ForeignKey('provider.id'),
                        index=True,
                        nullable=False)

    provider = relationship('Provider',
                            back_populates="venueProviders",
                            foreign_keys=[providerId])

    venueIdAtOfferProvider = Column(String(70))

    lastSyncDate = Column(DateTime, nullable=True)

    syncWorkerId = Column(String(24), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            'venueId',
            'providerId',
            'venueIdAtOfferProvider',
            name='unique_venue_provider',
        ),
    )

    @staticmethod
    def restize_integrity_error(internal_error):
        if 'unique_venue_provider' in str(internal_error.orig):
            return ['global', 'Votre lieu est déjà lié à cette source']
        return PcObject.restize_integrity_error(internal_error)

    @property
    def nOffers(self):
        return Offer.query \
            .filter(Offer.venueId == self.venueId) \
            .filter(Offer.lastProviderId == self.providerId) \
            .count()
