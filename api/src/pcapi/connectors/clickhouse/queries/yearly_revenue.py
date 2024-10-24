from datetime import date
from decimal import Decimal
from typing import Any

import pydantic.v1 as pydantic_v1
from sqlalchemy import engine
from sqlalchemy.orm import Query

from pcapi import settings
from pcapi.connectors.big_query.queries.base import BaseQuery
from pcapi.serialization.utils import to_camel


class Revenue(pydantic_v1.BaseModel):
    total: Decimal
    individual: Decimal
    collective: Decimal

    class Config:
        extra = "forbid"


class AggregatedRevenue(pydantic_v1.BaseModel):
    revenue: Revenue
    expected_revenue: Revenue | None

    class Config:
        extra = "forbid"
        alias_generator = to_camel


class YearlyAggregatedRevenueModel(pydantic_v1.BaseModel):
    income_by_year: dict[str, AggregatedRevenue | None]


class YearlyAggregatedRevenueQuery(BaseQuery):
    def _format_result(self, result: Query) -> dict:
        aggregated_data = {}
        current_year = date.today().year

        for row in result.fetchall():
            year = row["year"].year
            aggregated_data.update(
                {
                    year: {
                        "revenue": {
                            "individual": round(row["individual_revenue"], 2),
                            "collective": round(row["collective_revenue"], 2),
                            "total": round(row["total_revenue"], 2),
                        }
                    }
                }
            )
            # We have only expected revenues for the current year, it is empty for past years
            if year == current_year:
                aggregated_data[year].update(
                    {
                        "expectedRevenue": {
                            "individual": round(row["individual_expected_revenue"], 2),
                            "collective": round(row["collective_expected_revenue"], 2),
                            "total": round(row["total_expected_revenue"], 2),
                        }
                    }
                )
        if len(result) > 0:
            for year in range(min(aggregated_data.keys()), max(aggregated_data.keys()) + 1):
                if aggregated_data.get(year, False) is False:
                    aggregated_data.update({year: {}})
        return {"income_by_year": aggregated_data}

    @property
    def raw_query(self) -> str:
        return f"""
            SELECT
                creation_year as year,
                SUM(individual_revenue) as individual_revenue,
                SUM(individual_expected_revenue) as individual_expected_revenue,
                SUM(total_revenue) as total_revenue,
                SUM(collective_revenue) as collective_revenue,
                SUM(collective_expected_revenue) as collective_expected_revenue,
                SUM(total_expected_revenue) as total_expected_revenue
            FROM analytics.yearly_aggregated_venue_revenue
            WHERE "venue_id" in %s
            GROUP BY year
        """

    model = YearlyAggregatedRevenueModel
