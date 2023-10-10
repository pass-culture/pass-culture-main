import dataclasses
from datetime import datetime
import enum


def serialize_offer_type_educational_or_individual(offer_is_educational: bool) -> str:
    return "offre collective" if offer_is_educational else "offre grand public"


class CollectiveOfferType(enum.Enum):
    offer = "offer"
    template = "template"


@dataclasses.dataclass
class StocksStats:
    oldest_stock: datetime | None
    newest_stock: datetime | None
    stock_count: int | None
    remaining_quantity: int | None
