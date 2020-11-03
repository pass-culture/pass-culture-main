import math
from typing import Optional

from pcapi.domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap
from pcapi.domain.ts_vector import create_filter_on_ts_vector_matching_all_keywords
from pcapi.infrastructure.repository.pro_offers.paginated_offers_recap_domain_converter import (
    to_domain,
)
from pcapi.models import Offerer, OfferSQLEntity, UserOfferer, VenueSQLEntity


def get_paginated_offers_for_offerer_venue_and_keywords(
    user_id: int,
    user_is_admin: bool,
    page: Optional[int],
    offers_per_page: int,
    offerer_id: Optional[int] = None,
    exclude_active: Optional[bool] = False,
    exclude_inactive: Optional[bool] = False,
    venue_id: Optional[int] = None,
    type_id: Optional[str] = None,
    name_keywords: Optional[str] = None,
) -> PaginatedOffersRecap:
    query = get_offers_by_filters(
        user_id=user_id,
        user_is_admin=user_is_admin,
        offerer_id=offerer_id,
        exclude_active=exclude_active,
        exclude_inactive=exclude_inactive,
        venue_id=venue_id,
        type_id=type_id,
        name_keywords=name_keywords,
    )

    query = query.order_by(OfferSQLEntity.id.desc())

    query = query.paginate(page, per_page=offers_per_page, error_out=False)

    total_offers = query.total
    total_pages = math.ceil(total_offers / offers_per_page)

    # FIXME (cgaunet, 2020-11-03): we should not have serialization logic in the repository
    return to_domain(
        offer_sql_entities=query.items,
        current_page=query.page,
        total_pages=total_pages,
        total_offers=total_offers,
    )


def get_offers_by_filters(
    user_id: int,
    user_is_admin: bool,
    offerer_id: Optional[int] = None,
    exclude_active: Optional[bool] = False,
    exclude_inactive: Optional[bool] = False,
    venue_id: Optional[int] = None,
    type_id: Optional[str] = None,
    name_keywords: Optional[str] = None,
):
    query = OfferSQLEntity.query.join(VenueSQLEntity)
    if venue_id is not None:
        query = query.filter(OfferSQLEntity.venueId == venue_id)
    if type_id is not None:
        query = query.filter(OfferSQLEntity.type == type_id)
    if offerer_id is not None:
        query = query.filter(VenueSQLEntity.managingOffererId == offerer_id)
    if not user_is_admin:
        query = (
            query.join(Offerer)
            .join(UserOfferer)
            .filter(UserOfferer.userId == user_id)
            .filter(UserOfferer.validationToken == None)
        )
    if exclude_active:
        query = query.filter(OfferSQLEntity.isActive != True)
    if exclude_inactive:
        query = query.filter(OfferSQLEntity.isActive != False)
    if name_keywords is not None:
        name_keywords_filter = create_filter_on_ts_vector_matching_all_keywords(
            OfferSQLEntity.__name_ts_vector__, name_keywords
        )
        query = query.filter(name_keywords_filter)

    return query
