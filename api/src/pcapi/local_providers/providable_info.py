import dataclasses
from datetime import datetime

from pcapi.models import Model
from pcapi.models.product import Product


@dataclasses.dataclass
class ProvidableInfo:
    type: Model = Product
    id_at_providers: str = "1"
    new_id_at_provider: str = ""
    date_modified_at_provider: datetime = dataclasses.field(default_factory=datetime.utcnow)
