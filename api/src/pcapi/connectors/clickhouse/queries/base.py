import typing

import pydantic.v1 as pydantic_v1

import pcapi.connectors.clickhouse as clickhouse_connector


class BaseQuery:
    def __init__(self) -> None:
        self.backend = clickhouse_connector.get_backend()

    def _get_rows(self, params: typing.Tuple) -> list:
        return self.backend.run_query(self.raw_query, params)

    def _format_result(self, rows: list) -> dict:
        raise NotImplementedError()

    @property
    def raw_query(self) -> str:
        raise NotImplementedError()

    @property
    def model(self) -> type[pydantic_v1.BaseModel]:
        raise NotImplementedError()

    def execute(self, params: typing.Tuple) -> pydantic_v1.BaseModel:
        rows = self._get_rows(params)
        results_dict = self._format_result(rows)
        return self.model(**results_dict)
