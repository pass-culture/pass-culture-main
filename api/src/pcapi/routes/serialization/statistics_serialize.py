from pcapi.connectors.clickhouse.queries import YearlyAggregatedRevenueModel
from pcapi.routes.serialization import BaseModel


class StatisticsQueryModel(BaseModel):
    venue_ids: list[int] | int = []


class StatisticsModel(BaseModel, YearlyAggregatedRevenueModel):
    @classmethod
    def from_query(cls, income_by_year: dict) -> "StatisticsModel":
        if income_by_year.keys():
            min_year = int(min(income_by_year.keys()))
            max_year = int(max(income_by_year.keys()))

            for year in range(min_year, max_year + 1):
                if str(year) not in income_by_year:
                    income_by_year[str(year)] = {}
        return cls(**{"incomeByYear": income_by_year})

    class Config:
        extra = "forbid"
