from collections.abc import Mapping
import typing

import pydantic.v1 as pydantic_v1

import pcapi.connectors.clickhouse as clickhouse_connector


class BaseQuery:
    def __init__(self) -> None:
        self.backend = clickhouse_connector.get_backend()

    def _get_query_result(self, params: typing.Any) -> typing.Any:
        return self.backend.run_query(self.raw_query, params)

    def execute(self, params: typing.Tuple) -> type[pydantic_v1.BaseModel]:
        rows = self._get_query_result(params)
        results_dict = self._format_result(rows)
        try:
            return self.model(results_dict)
        except (pydantic_v1.ValidationError, TypeError) as err:
            raise Exception(
                "Impossible de valider les résultats de la requête clickhouse avec le modèle pydantic associé."
            )

    def _format_result():
        raise NotImplementedError()

    @property
    def raw_query(self) -> str:
        raise NotImplementedError()

    @property
    def model(self) -> type[pydantic_v1.BaseModel]:
        raise NotImplementedError()
