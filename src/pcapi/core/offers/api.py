from typing import Optional

from pcapi.domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap
from pcapi.core.offers.repository import (
    get_paginated_offers_for_offerer_venue_and_keywords,
)
from pcapi.repository import (
    user_offerer_queries,
)
from pcapi.models import VenueSQLEntity

from . import validation

DEFAULT_OFFERS_PER_PAGE = 20
DEFAULT_PAGE = 1


def list_offers_for_pro_user(
        user_id: int,
        user_is_admin: bool,
        type_id: Optional[str],
        offerer_id: Optional[int],
        offers_per_page: Optional[int],
        page: Optional[int],
        venue_id: Optional[int] = None,
        name_keywords: Optional[str] = None,
        requested_status: Optional[str] = None,
) -> PaginatedOffersRecap:
    if not user_is_admin:
        offerer_id = None
        if venue_id:
            venue = VenueSQLEntity.query.filter_by(id=venue_id).first_or_404()
            offerer_id = offerer_id or venue.managingOffererId
        if offerer_id is not None:
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
        requested_status=requested_status,
    )
