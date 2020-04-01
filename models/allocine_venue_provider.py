from sqlalchemy import Boolean, Column, ForeignKey, Integer, BigInteger, true

from models.venue_provider import VenueProvider


class AllocineVenueProvider(VenueProvider):
    __tablename__ = 'allocine_venue_provider'

    id = Column(BigInteger, ForeignKey('venue_provider.id'), primary_key=True)

    isDuo = Column(Boolean,
                   default=True,
                   server_default=true(),
                   nullable=False)

    quantity = Column(Integer, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'allocine_venue_provider',
    }
