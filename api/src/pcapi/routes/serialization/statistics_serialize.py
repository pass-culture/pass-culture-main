from decimal import Decimal

from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class Revenue(BaseModel):
    total: Decimal
    individual: Decimal | None
    collective: Decimal | None

    class Config:
        extra = "forbid"


class AggregatedRevenue(BaseModel):
    revenue: Revenue
    expected_revenue: Revenue | None

    class Config:
        extra = "forbid"
        # alias_generator = to_camel


class YearlyAggregatedRevenue(BaseModel):
    year: dict[str, AggregatedRevenue]
