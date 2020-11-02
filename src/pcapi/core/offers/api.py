from typing import Optional

from pcapi.domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap
from pcapi.core.offers.repository import (
    get_paginated_offers_for_offerer_venue_and_keywords,
)

DEFAULT_OFFERS_PER_PAGE = 20
DEFAULT_PAGE = 1


def list_offers_for_pro_user(
    user_id: int,
    user_is_admin: bool,
    venue_id: Optional[int],
    type_id: Optional[str],
    offerer_id: Optional[int],
    offers_per_page: Optional[int],
    page: Optional[int],
    exclude_active: Optional[bool] = False,
    exclude_inactive: Optional[bool] = False,
    name_keywords: Optional[str] = None,
) -> PaginatedOffersRecap:
    return get_paginated_offers_for_offerer_venue_and_keywords(
        user_id=user_id,
        user_is_admin=user_is_admin,
        offerer_id=offerer_id,
        offers_per_page=offers_per_page or DEFAULT_OFFERS_PER_PAGE,
        venue_id=venue_id,
        type_id=type_id,
        page=page or DEFAULT_PAGE,
        name_keywords=name_keywords,
        exclude_active=exclude_active,
        exclude_inactive=exclude_inactive,
    )
