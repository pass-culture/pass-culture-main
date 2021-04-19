from abc import ABC
from abc import abstractmethod
from typing import Optional

from pcapi.domain.identifier.identifier import Identifier
from pcapi.domain.venue.venue_with_offerer_name.venue_with_offerer_name import VenueWithOffererName


class VenueWithOffererNameRepository(ABC):
    @abstractmethod
    def get_by_pro_identifier(
        self,
        pro_identifier: int,
        user_is_admin: bool,
        active_offerers_only: bool,
        offerer_id: Optional[Identifier] = None,
        validated_offerer: Optional[bool] = None,
        validated_offerer_for_user: Optional[bool] = None,
    ) -> list[VenueWithOffererName]:
        pass
