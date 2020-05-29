from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, UniqueConstraint, case, select, and_, exists
from sqlalchemy.orm import relationship, column_property

from models.db import Model
from models.deactivable_mixin import DeactivableMixin
from models.offer import Offer
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin
from models.provider import Provider


class VenueProvider(PcObject,
                    Model,
                    ProvidableMixin,
                    DeactivableMixin):
    venueId = Column(BigInteger,
                     ForeignKey('venue.id'),
                     nullable=False)

    venue = relationship('VenueSQLEntity',
                         foreign_keys=[venueId])

    providerId = Column(BigInteger,
                        ForeignKey('provider.id'),
                        index=True,
                        nullable=False)

    provider = relationship('Provider',
                            foreign_keys=[providerId])

    venueIdAtOfferProvider = Column(String(70))

    lastSyncDate = Column(DateTime, nullable=True)

    syncWorkerId = Column(String(24), nullable=True)

    isFromAllocineProvider = column_property(
        exists(select([Provider.id]).
               where(and_(Provider.id == providerId,
                          Provider.localClass == 'AllocineStocks')
                     ))
    )

    __mapper_args__ = {
        "polymorphic_on": case([
            (isFromAllocineProvider, "allocine_venue_provider"),
        ], else_="venue_provider"),
        "polymorphic_identity": "venue_provider"
    }

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
