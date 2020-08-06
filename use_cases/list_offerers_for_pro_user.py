from typing import Optional

from domain.pro_offerers.paginated_offerers import PaginatedOfferers
from domain.pro_offerers.paginated_offerers_repository import PaginatedOfferersRepository


class OfferersRequestParameters(object):
    def __init__(self,
                 user_id: int,
                 user_is_admin: bool,
                 is_filtered_by_offerer_status: bool,
                 only_validated_offerers: bool,
                 pagination_limit: str = '10',
                 keywords: Optional[str] = None,
                 page: str = '0'):
        self.only_validated_offerers = only_validated_offerers
        self.is_filtered_by_offerer_status = is_filtered_by_offerer_status
        self.user_id = user_id
        self.user_is_admin = user_is_admin
        self.pagination_limit = int(pagination_limit)
        self.keywords = keywords
        self.page = int(page)


class ListOfferersForProUser:
    def __init__(self, paginated_offerers_repository: PaginatedOfferersRepository):
        self.paginated_offerers_repository = paginated_offerers_repository

    def execute(self, offerers_request_parameters: OfferersRequestParameters) -> PaginatedOfferers:
        return self.paginated_offerers_repository.with_status_and_keywords(
            user_id=offerers_request_parameters.user_id,
            user_is_admin=offerers_request_parameters.user_is_admin,
            page=offerers_request_parameters.page,
            pagination_limit=offerers_request_parameters.pagination_limit,
            only_validated_offerers=offerers_request_parameters.only_validated_offerers,
            is_filtered_by_offerer_status=offerers_request_parameters.is_filtered_by_offerer_status,
            keywords=offerers_request_parameters.keywords,
        )
