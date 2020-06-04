from typing import List

from domain.venue.venue_with_offerer_name.venue_with_offerer_name import VenueWithOffererName
from domain.venue.venue_with_offerer_name.venue_with_offerer_name_repository import \
    VenueWithOffererNameRepository
from infrastructure.repository.venue.venue_with_offerer_name import \
    venue_with_offerer_name_domain_converter
from models import VenueSQLEntity, Offerer, UserOfferer, UserSQLEntity


class VenueWithOffererNameSQLRepository(VenueWithOffererNameRepository):
    def get_by_pro_identifier(self, pro_identifier: int) -> List[VenueWithOffererName]:
        venue_sql_entities = VenueSQLEntity.query \
            .join(Offerer) \
            .join(UserOfferer) \
            .join(UserSQLEntity) \
            .filter(UserSQLEntity.id == pro_identifier) \
            .filter(Offerer.validationToken == None) \
            .order_by(VenueSQLEntity.name) \
            .all()
        return [venue_with_offerer_name_domain_converter.to_domain(venue_sql_entity) for venue_sql_entity in venue_sql_entities]
