from typing import List

from pcapi.domain.venue.venue_with_offerer_name.venue_with_offerer_name import VenueWithOffererName
from pcapi.domain.venue.venue_with_offerer_name.venue_with_offerer_name_repository import \
    VenueWithOffererNameRepository
from pcapi.infrastructure.repository.venue.venue_with_offerer_name import \
    venue_with_offerer_name_domain_converter
from pcapi.models import VenueSQLEntity, Offerer, UserOfferer, UserSQLEntity


class VenueWithOffererNameSQLRepository(VenueWithOffererNameRepository):
    def get_by_pro_identifier(self, pro_identifier: int, user_is_admin: bool,) -> List[VenueWithOffererName]:
        query = VenueSQLEntity.query

        if not user_is_admin:
            query = query \
                .join(Offerer, Offerer.id == VenueSQLEntity.managingOffererId) \
                .filter(Offerer.validationToken == None) \
                .join(UserOfferer, UserOfferer.offererId == Offerer.id) \
                .filter(UserOfferer.validationToken == None) \
                .filter(UserOfferer.userId == pro_identifier)

        venue_sql_entities = query \
            .order_by(VenueSQLEntity.name) \
            .all()
        return [venue_with_offerer_name_domain_converter.to_domain(venue_sql_entity) for venue_sql_entity in venue_sql_entities]
