from abc import ABC, abstractmethod
from typing import Optional

from domain.pro_offerers.paginated_offerers import PaginatedOfferers


class PaginatedOfferersRepository(ABC):
    @abstractmethod
    def with_status_and_keywords(self,
                                 user_id: int,
                                 user_is_admin: bool,
                                 page: Optional[int],
                                 pagination_limit: int,
                                 only_validated_offerers: bool,
                                 is_filtered_by_offerer_status: bool,
                                 keywords: Optional[str] = None) -> PaginatedOfferers:
        pass
