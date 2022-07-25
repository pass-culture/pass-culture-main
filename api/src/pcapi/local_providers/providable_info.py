import dataclasses
from datetime import datetime

import pcapi.core.offers.models as offers_models
from pcapi.models import Model


@dataclasses.dataclass
class ProvidableInfo:
    type: Model = offers_models.Product  # type: ignore [valid-type]
    id_at_providers: str = "1"
    new_id_at_provider: str = ""
    date_modified_at_provider: datetime = dataclasses.field(default_factory=datetime.utcnow)
