from typing import List

from models import Offerer
from routes.serialization import as_dict
from utils.includes import OFFERER_INCLUDES


class PaginatedOfferers:
    def __init__(self, offerers: List[Offerer], total: int):
        self.offerers = [as_dict(offerer, includes=OFFERER_INCLUDES) for offerer in offerers]
        self.total = total
        self.headers = {
            'Total-Data-Count': total,
            'Access-Control-Expose-Headers': 'Total-Data-Count'
        }
