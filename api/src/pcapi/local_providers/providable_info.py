from dataclasses import dataclass
from datetime import datetime

from pcapi.models import Model
from pcapi.models.product import Product


@dataclass
class ProvidableInfo:
    type: Model = Product
    id_at_providers: str = ""
    new_id_at_provider: str = ""
    date_modified_at_provider: datetime = datetime(1900, 1, 1)
