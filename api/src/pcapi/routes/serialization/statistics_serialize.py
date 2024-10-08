from decimal import Decimal
from typing import Any

from pydantic.v1.utils import GetterDict

from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class Revenue(BaseModel):
    total: Decimal
    individual: Decimal
    collective: Decimal

    class Config:
        extra = "forbid"


class AggregatedRevenue(BaseModel):
    revenue: Revenue
    expected_revenue: Revenue | None

    class Config:
        extra = "forbid"
        alias_generator = to_camel


class YearlyAggregatedRevenueGetterDict(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        if key == "year":
            return self._obj["year"]
        return super().get(key, default)


class YearlyAggregatedRevenue(BaseModel):
    year: dict[str, AggregatedRevenue | None]

    class Config:
        orm_mode = True
        getter_dict = YearlyAggregatedRevenueGetterDict
