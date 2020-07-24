from typing import Optional

from domain.pro_offers.paginated_offers import PaginatedOffers
from domain.pro_offers.paginated_offers_repository import PaginatedOffersRepository
from repository.offer_queries import build_find_offers_with_filter_parameters


class PaginatedOffersSQLRepository(PaginatedOffersRepository):
    def get_paginated_offers_for_offerer_venue_and_keywords(self,
                                                            user_id: int,
                                                            user_is_admin: bool,
                                                            page: Optional[int],
                                                            pagination_limit: int,
                                                            offerer_id: Optional[int] = None,
                                                            venue_id: Optional[int] = None,
                                                            keywords: Optional[str] = None) -> PaginatedOffers:
        query = build_find_offers_with_filter_parameters(
            user_id=user_id,
            user_is_admin=user_is_admin,
            offerer_id=offerer_id,
            venue_id=venue_id,
            keywords_string=keywords,
        )
        query = query.paginate(page, per_page=int(pagination_limit), error_out=False)
        results = query.items
        total = query.total

        return PaginatedOffers(results, total)
