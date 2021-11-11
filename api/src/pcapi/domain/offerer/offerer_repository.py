from abc import ABC
from abc import abstractmethod

from pcapi.domain.offerer.offerer import Offerer


class OffererRepository(ABC):
    @abstractmethod
    def find_by_siren(self, siren: str) -> Offerer:
        pass
