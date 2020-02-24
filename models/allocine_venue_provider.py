from sqlalchemy import Column, Integer, ForeignKey, Boolean

from models.venue_provider import VenueProvider


class AllocineVenueProvider(VenueProvider):
    __tablename__ = 'allocine_venue_provider'

    id = Column(Integer, ForeignKey('venue_provider.id'), primary_key=True)

    isDuo = Column(Boolean,
                   default=False,
                   nullable=False)

    available = Column(Integer,
                       nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'allocine_venue_provider',
    }