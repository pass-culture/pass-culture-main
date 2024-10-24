import typing

from sqlalchemy import engine

from pcapi import settings
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.serialization.statistics_serialize import YearlyAggregatedRevenue
from pcapi.utils import requests
from pcapi.utils.module_loading import import_string


class BaseBackend:
    def __init__(self) -> None:
        self._engine: engine.Engine | None = None

    @property
    def engine(self) -> engine.Engine:
        if not self._engine:
            self._engine = self._get_engine()
        return self._engine

    def _get_engine(self) -> engine.Engine:
        raise NotImplementedError

    def run_query(self, query: str, params: typing.Tuple) -> row.Row:
        try:
            results = self.engine.execute(query, params)
        except Exception as err:
            if isinstance(err, requests.exceptions.ConnectionError):
                raise ApiErrors(errors={"clickhouse": "Can not connect to clickhouse server"}, status_code=422)
            raise ApiErrors(errors={"clickhouse": f"Error : {err}"}, status_code=400)
        return results
