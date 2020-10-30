from abc import ABC, abstractmethod
from typing import Optional

from pcapi.domain.pro_offers.offers_status_filters import OffersStatusFilters
from pcapi.domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap


class PaginatedOffersRepository(ABC):
    @abstractmethod
    def get_paginated_offers_for_offerer_venue_and_keywords(
        self,
        user_id: int,
        user_is_admin: bool,
        page: Optional[int],
        offers_per_page: int,
        offerer_id: Optional[int] = None,
        status_filters: OffersStatusFilters = OffersStatusFilters(),
        venue_id: Optional[int] = None,
        type_id: Optional[str] = None,
        name_keywords: Optional[str] = None,
    ) -> PaginatedOffersRecap:
        pass
