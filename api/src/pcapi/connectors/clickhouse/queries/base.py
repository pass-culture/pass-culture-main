import typing

import pydantic.v1 as pydantic_v1

import pcapi.connectors.clickhouse as clickhouse_connector


class BaseQuery[ModelType: pydantic_v1.BaseModel]:
    def __init__(self) -> None:
        self.backend = clickhouse_connector.get_backend()

    def _get_rows(self, params: dict) -> typing.Sequence:
        return self.backend.run_query(self.raw_query, params)

    @property
    def raw_query(self) -> str:
        raise NotImplementedError()

    @property
    def model(self) -> type[ModelType]:
        raise NotImplementedError()

    def execute(self, params: dict) -> list[ModelType]:
        rows = self._get_rows(params)
        return [self.model.from_orm(row) for row in rows]
