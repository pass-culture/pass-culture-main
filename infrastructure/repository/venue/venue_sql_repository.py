from sqlalchemy import func

from domain.venue.venue_repository import VenueRepository
from domain.venue.venue import Venue
from infrastructure.repository.venue import venue_domain_converter
from models import Venue as VenueSQLEntity

class VenueSQLRepository(VenueRepository):
    def find_by_siret(self, siret):
        return VenueSQLEntity.query \
            .filter_by(siret=siret) \
            .one_or_none()

    def find_by_name(self, name, offerer_id):
        return VenueSQLEntity.query \
            .filter_by(managingOffererId=offerer_id) \
            .filter(VenueSQLEntity.siret == None) \
            .filter(func.lower(VenueSQLEntity.name) == func.lower(name)) \
            .all()
