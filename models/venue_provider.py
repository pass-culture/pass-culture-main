import sqlalchemy as db

from models.deactivable_mixin import DeactivableMixin
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin


class VenueProvider(PcObject,
                    ProvidableMixin,
                    DeactivableMixin,
                    db.Model):

    venueId = db.Column(db.BigInteger,
                        db.ForeignKey('venue.id'),
                        nullable=False,
                        index=True)
    venue = db.relationship('Venue',
                            back_populates="venueProviders",
                            foreign_keys=[venueId])

    providerId = db.Column(db.BigInteger,
                           db.ForeignKey('provider.id'),
                           nullable=False)
    provider = db.relationship('Provider',
                               back_populates="venueProviders",
                               foreign_keys=[providerId])

    venueIdAtOfferProvider = db.Column(db.String(70))

    lastSyncDate = db.Column(db.DateTime,
                             nullable=True)
