from pcapi.core.offerers.models import Offerer


class PaginatedOfferers:
    def __init__(self, offerers: list[Offerer], total: int):
        self.offerers = offerers
        self.total = total
