from pcapi.local_providers.local_provider import LocalProvider
from pcapi.models import Model


class CGRStocks(LocalProvider):
    name = "CGR"
    can_create = True

    def __next__(self) -> None:
        pass

    def fill_object_attributes(self, pc_object: Model) -> None:
        pass
