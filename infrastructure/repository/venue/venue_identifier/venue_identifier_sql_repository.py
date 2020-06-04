from typing import List

from sqlalchemy import func

from domain.venue.venue_identifier.venue_identifier import VenueIdentifier
from domain.venue.venue_identifier.venue_identifier_repository import VenueIdentifierRepository
from infrastructure.repository.venue.venue_identifier import venue_identifier_domain_converter
from models import VenueSQLEntity


class VenueIdentifierSQLRepository(VenueIdentifierRepository):
    def find_by_siret(self, siret: str) -> VenueIdentifier:
        venue_sql_entity = VenueSQLEntity.query \
            .filter_by(siret=siret) \
            .one_or_none()
        return venue_identifier_domain_converter.to_domain(venue_sql_entity) if venue_sql_entity else None

    def find_by_name(self, name: str, offerer_id: int) -> List[VenueIdentifier]:
        venue_sql_entities = VenueSQLEntity.query \
            .filter_by(managingOffererId=offerer_id) \
            .filter(VenueSQLEntity.siret == None) \
            .filter(func.lower(VenueSQLEntity.name) == func.lower(name)) \
            .all()
        return [venue_identifier_domain_converter.to_domain(venue_sql_entity) for venue_sql_entity in venue_sql_entities]
