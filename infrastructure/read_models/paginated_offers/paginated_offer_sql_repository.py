from typing import Optional

from infrastructure.read_models.paginated_offers.paginated_offer import PaginatedOffers
from models import UserSQLEntity
from repository.offer_queries import build_find_offers_with_filter_parameters


class PaginatedOfferSQLRepository:
    def get_paginated_offers_for_offerer_venue_and_keywords(self,
                                                            user: UserSQLEntity,
                                                            offerer_id: int,
                                                            pagination_limit: int,
                                                            venue_id: int,
                                                            page: Optional[int],
                                                            keywords: str) -> PaginatedOffers:
        query = build_find_offers_with_filter_parameters(
            user=user,
            offerer_id=offerer_id,
            venue_id=venue_id,
            keywords_string=keywords,
        )
        query = query.paginate(page, per_page=int(pagination_limit), error_out=False)
        results = query.items
        total = query.total

        return PaginatedOffers(results, total)
