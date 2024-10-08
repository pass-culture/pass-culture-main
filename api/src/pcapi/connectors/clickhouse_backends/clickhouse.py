"""
To make this work locally :s

# Connect to the data ehp with tsh

# local proxy to clickhouse
# kubectl port-forward clickhouse-shard0-0 8123:8123
"""

from datetime import date

from sqlalchemy import create_engine
from sqlalchemy import engine

from pcapi import settings
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.serialization.statistics_serialize import YearlyAggregatedRevenue
from pcapi.utils import requests

from .base import BaseBackend


class ClickhouseApiException(Exception):
    pass


class ClickhouseBackend(BaseBackend):
    def _get_engine(self) -> engine.Engine:
        ip = settings.CLICKHOUSE_IP
        user = str(settings.CLICKHOUSE_USER)
        password = str(settings.CLICKHOUSE_PASSWORD)
        uri = f"clickhouse://{user}:{password}@{ip}:8123/default?protocol=http"
        return create_engine(uri, pool_pre_ping=True)

    def _results_to_dict(self, results: list[engine.row.Row]) -> dict:
        aggregated_data = dict()
        current_year = date.today().year
        for result in results:
            year = result["year"].year
            aggregated_data.update(
                {
                    year: {
                        "revenue": {
                            "individual": round(result["individual_revenue"], 2),
                            "collective": round(result["collective_revenue"], 2),
                            "total": round(result["total_revenue"], 2),
                        }
                    }
                }
            )
            if year == current_year:
                aggregated_data[year].update(
                    {
                        "expectedRevenue": {
                            "individual": round(result["individual_expected_revenue"], 2),
                            "collective": round(result["collective_expected_revenue"], 2),
                            "total": round(result["total_expected_revenue"], 2),
                        }
                    }
                )
        if len(results) > 0:
            for year in range(min(aggregated_data.keys()), max(aggregated_data.keys()) + 1):
                if aggregated_data.get(year, False) is False:
                    aggregated_data.update({year: None})
        return {"year": aggregated_data}

    def get_yearly_aggregated_venue_revenue(self, venue_ids: list[int]) -> YearlyAggregatedRevenue:
        connection = self._get_engine()

        query = """
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

        values = (tuple(venue_ids),)

        try:
            results = connection.execute(query, values).fetchall()
        except Exception as err:
            if isinstance(err, requests.exceptions.ConnectionError):
                raise ApiErrors(errors={"clickhouse": "Can not connect to clickhouse server"}, status_code=422)
            raise ApiErrors(errors={"clickhouse": f"Error : {err}"}, status_code=400)
        results_dict = self._results_to_dict(results)

        return YearlyAggregatedRevenue.from_orm(results_dict)
