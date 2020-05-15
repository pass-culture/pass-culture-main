from abc import ABC, abstractmethod

from domain.offerer.offerer import Offerer


class OffererRepository(ABC):
    @abstractmethod
    def find_by_siren(self, siren: str) -> Offerer:
        pass
