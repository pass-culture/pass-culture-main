from datetime import date

from pcapi.connectors.clickhouse.queries import YearlyAggregatedRevenueModel
from pcapi.routes.serialization import BaseModel


class StatisticsQueryModel(BaseModel):
    venue_ids: list[int] | int = []


class StatisticsModel(BaseModel, YearlyAggregatedRevenueModel):
    @classmethod
    def from_query(cls, income_by_year: dict) -> "StatisticsModel":
        current_year = date.today().year
        if income_by_year.keys():
            min_year = int(min(income_by_year.keys()))
            max_year = int(max(income_by_year.keys()))

            for year in range(min_year, max_year + 1):
                if str(year) not in income_by_year:
                    income_by_year[str(year)] = {}
                # we don't need to serialize expected_revenue for previous years
                elif year < current_year and hasattr(income_by_year[str(year)], "expected_revenue"):
                    delattr(income_by_year[str(year)], "expected_revenue")
        return cls(**{"incomeByYear": income_by_year})

    class Config:
        extra = "forbid"
