from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, UniqueConstraint, case, select
from sqlalchemy.orm import relationship, column_property

from models.db import Model, db
from models.deactivable_mixin import DeactivableMixin
from models.offer import Offer
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin
from models.provider import Provider


def is_from_allocine_provider(provider_local_class: str) -> bool:
    if provider_local_class == 'AllocineStocks':
        return db.true()
    return db.false()


class VenueProvider(PcObject,
                    Model,
                    ProvidableMixin,
                    DeactivableMixin):
    venueId = Column(BigInteger,
                     ForeignKey('venue.id'),
                     nullable=False)

    venue = relationship('Venue',
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

    providerClass = column_property(
        select([Provider.localClass]).
            where(Provider.id == providerId
                  )
    )

    __mapper_args__ = {
        "polymorphic_on": case([
            (is_from_allocine_provider(providerClass), "allocine_venue_provider")
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
