from typing import Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Query, aliased

from domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap
from domain.pro_offers.paginated_offers_recap_repository import PaginatedOffersRepository
from domain.ts_vector import create_filter_on_ts_vector_matching_all_keywords
from infrastructure.repository.pro_offers.paginated_offers_recap_domain_converter import to_domain
from models import OfferSQLEntity, VenueSQLEntity, Offerer, UserOfferer


class PaginatedOffersSQLRepository(PaginatedOffersRepository):
    def get_paginated_offers_for_offerer_venue_and_keywords(self,
                                                            user_id: int,
                                                            user_is_admin: bool,
                                                            page: Optional[int],
                                                            pagination_limit: int,
                                                            offerer_id: Optional[int] = None,
                                                            venue_id: Optional[int] = None,
                                                            keywords: Optional[str] = None) -> PaginatedOffersRecap:
        query = OfferSQLEntity.query
        if venue_id is not None:
            query = query.filter(OfferSQLEntity.venueId == venue_id)
        if offerer_id is not None:
            query = query \
                .join(VenueSQLEntity) \
                .filter(VenueSQLEntity.managingOffererId == offerer_id)
        if not user_is_admin:
            query = query \
                .join(VenueSQLEntity) \
                .join(Offerer) \
                .join(UserOfferer) \
                .filter(UserOfferer.userId == user_id) \
                .filter(UserOfferer.validationToken == None)
        if keywords is not None:
            query = _filter_offers_with_keywords_string(
                    query,
                    keywords
            )
        else:
            query = query.order_by(OfferSQLEntity.id.desc())

        query = query.paginate(page, per_page=int(pagination_limit), error_out=False)
        results = query.items
        total = query.total

        return to_domain(results, total)


def _filter_offers_with_keywords_string(query: Query, keywords_string: str) -> Query:
    query_on_offer_using_keywords = _build_query_using_keywords_on_model(keywords_string, query)
    query_on_offer_using_keywords = _order_by_offer_name_containing_keyword_string(keywords_string,
                                                                                   query_on_offer_using_keywords)
    return query_on_offer_using_keywords


def _build_query_using_keywords_on_model(keywords_string: str, query: Query) -> Query:
    keywords_filter = create_filter_on_ts_vector_matching_all_keywords(OfferSQLEntity.__name_ts_vector__, keywords_string)
    return query.filter(keywords_filter)


def _order_by_offer_name_containing_keyword_string(keywords_string: str, query: Query) -> Query:
    offer_alias = aliased(OfferSQLEntity)
    return query.order_by(
            desc(
                    OfferSQLEntity.query
                        .filter(OfferSQLEntity.id == offer_alias.id)
                        .filter(OfferSQLEntity.name.op('@@')(func.plainto_tsquery(keywords_string)))
                        .order_by(offer_alias.name)
                        .exists()
            ),
            desc(OfferSQLEntity.id)
    )
