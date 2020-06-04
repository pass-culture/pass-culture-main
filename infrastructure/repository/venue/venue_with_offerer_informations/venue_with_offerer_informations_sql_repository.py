from typing import List

from domain.venue.venue_with_offerer_informations.venue_with_offerer_informations import VenueWithOffererInformations
from domain.venue.venue_with_offerer_informations.venue_with_offerer_informations_repository import \
    VenueWithOffererInformationsRepository
from infrastructure.repository.venue.venue_with_offerer_informations import \
    venue_with_offerer_informations_domain_converter
from models import VenueSQLEntity, Offerer, UserOfferer, UserSQLEntity


class VenueWithOffererInformationsSQLRepository(VenueWithOffererInformationsRepository):
    def get_by_pro_identifier(self, pro_identifier: int) -> List[VenueWithOffererInformations]:
        venue_sql_entities = VenueSQLEntity.query \
            .join(Offerer) \
            .join(UserOfferer) \
            .join(UserSQLEntity) \
            .filter(UserSQLEntity.id == pro_identifier) \
            .filter(Offerer.validationToken == None) \
            .order_by(VenueSQLEntity.name) \
            .all()
        return [venue_with_offerer_informations_domain_converter.to_domain(venue_sql_entity) for venue_sql_entity in venue_sql_entities]
