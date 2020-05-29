from typing import List

from sqlalchemy import func

from domain.venue.venue import Venue
from domain.venue.venue_repository import VenueRepository
from infrastructure.repository.venue import venue_domain_converter
from models import VenueSQLEntity, Offerer, UserOfferer, UserSQLEntity


class VenueSQLRepository(VenueRepository):
    def find_by_siret(self, siret):
        venue_sql_entity = VenueSQLEntity.query \
            .filter_by(siret=siret) \
            .one_or_none()
        return venue_domain_converter.to_domain(venue_sql_entity) if venue_sql_entity else None

    def find_by_name(self, name, offerer_id) -> List[Venue]:
        venue_sql_entities = VenueSQLEntity.query \
            .filter_by(managingOffererId=offerer_id) \
            .filter(VenueSQLEntity.siret == None) \
            .filter(func.lower(VenueSQLEntity.name) == func.lower(name)) \
            .all()
        return [venue_domain_converter.to_domain(venue_sql_entity) for venue_sql_entity in venue_sql_entities]

    def get_all_by_pro_identifier(self, pro_identifier: int) -> List[Venue]:
        venue_sql_entities = VenueSQLEntity.query \
            .join(Offerer) \
            .join(UserOfferer) \
            .join(UserSQLEntity) \
            .filter(UserSQLEntity.id == pro_identifier) \
            .order_by(VenueSQLEntity.name) \
            .all()
        return [venue_domain_converter.to_domain(venue_sql_entity) for venue_sql_entity in venue_sql_entities]
