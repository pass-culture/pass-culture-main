import dataclasses
import datetime
import typing

import pcapi.core.offers.models as offers_models


@dataclasses.dataclass
class ProvidableInfo:
    type: typing.Type[offers_models.Product | offers_models.Offer | offers_models.Stock] = offers_models.Product
    id_at_providers: str = "1"
    new_id_at_provider: str = ""
    date_modified_at_provider: datetime.datetime = dataclasses.field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
