from typing import Optional

from pcapi.domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap
from pcapi.core.offers.repository import (
    get_paginated_offers_for_offerer_venue_and_keywords,
)
from pcapi.repository import (
    user_offerer_queries,
    venue_queries,
)
from . import validation

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
    if venue_id:
        venue = venue_queries.find_by_id(venue_id)
        validation.check_venue_exists_when_requested(venue, venue_id)
        offerer_id = offerer_id or venue.managingOffererId

    if not user_is_admin and offerer_id is not None:
        user_offerer = user_offerer_queries.find_one_or_none_by_user_id_and_offerer_id(
            user_id=user_id, offerer_id=offerer_id
        )
        validation.check_user_has_rights_on_offerer(user_offerer)

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
