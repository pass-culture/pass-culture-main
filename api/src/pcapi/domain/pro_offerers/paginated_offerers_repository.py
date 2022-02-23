from abc import ABC
from abc import abstractmethod
from typing import Optional

from pcapi.domain.pro_offerers.paginated_offerers import PaginatedOfferers


class PaginatedOfferersRepository(ABC):
    @abstractmethod
    def with_status_and_keywords(
        self,
        user_id: int,
        user_is_admin: bool,
        pagination_limit: int,
        page: int = 0,
        keywords: Optional[str] = None,
    ) -> PaginatedOfferers:
        pass
