from typing import Optional

from domain.identifier.identifier import Identifier

from domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap
from domain.pro_offers.paginated_offers_recap_repository import PaginatedOffersRepository


class OffersRequestParameters(object):
    def __init__(self,
                 user_id: int,
                 user_is_admin: bool,
                 offerer_id: Optional[Identifier],
                 venue_id: Optional[Identifier],
                 pagination_limit: str = '10',
                 name_keywords: Optional[str] = None,
                 page: str = '0'):
        self.user_id = user_id
        self.user_is_admin = user_is_admin
        self.offerer_id = offerer_id
        self.venue_id = venue_id
        self.pagination_limit = int(pagination_limit)
        self.name_keywords = name_keywords
        self.page = int(page)


class ListOffersForProUser:
    def __init__(self, paginated_offer_repository: PaginatedOffersRepository):
        self.paginated_offer_repository = paginated_offer_repository

    def execute(self, offers_request_parameters: OffersRequestParameters) -> PaginatedOffersRecap:
        return self.paginated_offer_repository.get_paginated_offers_for_offerer_venue_and_keywords(
            user_id=offers_request_parameters.user_id,
            user_is_admin=offers_request_parameters.user_is_admin,
            offerer_id=offers_request_parameters.offerer_id,
            pagination_limit=offers_request_parameters.pagination_limit,
            venue_id=offers_request_parameters.venue_id,
            name_keywords=offers_request_parameters.name_keywords,
            page=offers_request_parameters.page,
        )
