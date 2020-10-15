import math
from typing import Optional

from pcapi.domain.identifier.identifier import Identifier

from pcapi.domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap
from pcapi.domain.pro_offers.paginated_offers_recap_repository import PaginatedOffersRepository
from pcapi.domain.ts_vector import create_filter_on_ts_vector_matching_all_keywords
from pcapi.infrastructure.repository.pro_offers.paginated_offers_recap_domain_converter import to_domain
from pcapi.models import Offerer, OfferSQLEntity, UserOfferer, VenueSQLEntity


class PaginatedOffersSQLRepository(PaginatedOffersRepository):
    def get_paginated_offers_for_offerer_venue_and_keywords(self,
                                                            user_id: int,
                                                            user_is_admin: bool,
                                                            page: Optional[int],
                                                            offers_per_page: int,
                                                            offerer_id: Optional[Identifier] = None,
                                                            venue_id: Optional[Identifier] = None,
                                                            name_keywords: Optional[str] = None) -> PaginatedOffersRecap:
        query = OfferSQLEntity.query
        if venue_id is not None:
            query = query.filter(OfferSQLEntity.venueId == venue_id.persisted)
        if offerer_id is not None:
            query = query \
                .join(VenueSQLEntity) \
                .filter(VenueSQLEntity.managingOffererId == offerer_id.persisted)
        if not user_is_admin:
            query = query \
                .join(VenueSQLEntity) \
                .join(Offerer) \
                .join(UserOfferer) \
                .filter(UserOfferer.userId == user_id) \
                .filter(UserOfferer.validationToken == None)
        if name_keywords is not None:
            name_keywords_filter = create_filter_on_ts_vector_matching_all_keywords(OfferSQLEntity.__name_ts_vector__, name_keywords)
            query = query.filter(name_keywords_filter)

        query = query.order_by(OfferSQLEntity.id.desc())

        query = query.paginate(page, per_page=offers_per_page, error_out=False)

        total_offers = query.total
        total_pages = math.ceil(total_offers / offers_per_page)

        return to_domain(offer_sql_entities=query.items, current_page=query.page, total_pages=total_pages, total_offers=total_offers)
