import dataclasses
import typing
from datetime import datetime

import pcapi.core.offers.models as offers_models
from pcapi.utils import date as date_utils


@dataclasses.dataclass
class ProvidableInfo:
    type: typing.Type[offers_models.Offer | offers_models.Stock] = offers_models.Offer
    id_at_providers: str = "1"
    new_id_at_provider: str = ""
    date_modified_at_provider: datetime = dataclasses.field(default_factory=date_utils.get_naive_utc_now)
