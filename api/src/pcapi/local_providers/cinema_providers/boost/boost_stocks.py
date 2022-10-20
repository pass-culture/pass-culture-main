from pcapi.local_providers.local_provider import LocalProvider
from pcapi.local_providers.providable_info import ProvidableInfo
from pcapi.models import Model


class BoostStocks(LocalProvider):
    name = "Boost"
    can_create = True

    def __next__(self) -> list[ProvidableInfo]:
        pass

    def fill_object_attributes(self, pc_object: Model) -> None:
        pass
