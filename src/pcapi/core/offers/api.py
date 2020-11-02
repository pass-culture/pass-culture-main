from typing import Optional

from pcapi.domain.pro_offers.offers_status_filters import OffersStatusFilters

from pcapi.domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap
from pcapi.core.offers.repository import (
    get_paginated_offers_for_offerer_venue_and_keywords,
)


class OffersRequestParameters:
    DEFAULT_OFFERS_PER_PAGE = 20
    DEFAULT_PAGE = 1

    def __init__(
        self,
        user_id: int,
        user_is_admin: bool,
        offerer_id: Optional[int],
        venue_id: Optional[int],
        type_id: Optional[str],
        offers_per_page: Optional[int],
        page: Optional[int],
        name_keywords: Optional[str] = None,
        status_filters: OffersStatusFilters = OffersStatusFilters(),
    ):
        self.user_id = user_id
        self.user_is_admin = user_is_admin
        self.offerer_id = offerer_id
        self.venue_id = venue_id
        self.type_id = type_id
        self.offers_per_page = offers_per_page or self.DEFAULT_OFFERS_PER_PAGE
        self.page = page or self.DEFAULT_PAGE
        self.name_keywords = name_keywords
        self.status_filters = status_filters


def list_offers_for_pro_user(
    offers_request_parameters: OffersRequestParameters,
) -> PaginatedOffersRecap:
    return get_paginated_offers_for_offerer_venue_and_keywords(
        user_id=offers_request_parameters.user_id,
        user_is_admin=offers_request_parameters.user_is_admin,
        offerer_id=offers_request_parameters.offerer_id,
        offers_per_page=offers_request_parameters.offers_per_page,
        venue_id=offers_request_parameters.venue_id,
        type_id=offers_request_parameters.type_id,
        page=offers_request_parameters.page,
        name_keywords=offers_request_parameters.name_keywords,
        status_filters=offers_request_parameters.status_filters,
    )
