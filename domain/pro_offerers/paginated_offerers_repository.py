from abc import ABC, \
    abstractmethod
from typing import Optional

from domain.pro_offerers.paginated_offerers import PaginatedOfferers


class PaginatedOfferersRepository(ABC):
    @abstractmethod
    def with_status_and_keywords(self,
                                 user_id: int,
                                 user_is_admin: bool,
                                 pagination_limit: int,
                                 is_filtered_by_offerer_status: bool,
                                 only_validated_offerers: bool,
                                 page: int = 0,
                                 keywords: Optional[str] = None) -> PaginatedOfferers:
        pass
