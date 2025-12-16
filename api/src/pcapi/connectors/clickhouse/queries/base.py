import typing

import pydantic as pydantic_v2

import pcapi.connectors.clickhouse as clickhouse_connector


class ClickHouseBaseModel(pydantic_v2.BaseModel):
    model_config = pydantic_v2.ConfigDict(
        from_attributes=True,
        extra="forbid",
    )


class BaseQuery[ModelType: ClickHouseBaseModel, Row]:
    def __init__(self) -> None:
        self.backend = clickhouse_connector.get_backend()

    def _get_rows(self, params: dict) -> typing.Sequence[Row]:
        return self.backend.run_query(self.raw_query, params)

    @property
    def raw_query(self) -> str:
        raise NotImplementedError()

    @property
    def model(self) -> type[ModelType]:
        raise NotImplementedError()

    def _serialize_row(self, row: Row) -> ModelType:
        return self.model.model_validate(row)

    def execute(self, params: dict) -> list[ModelType]:
        rows = self._get_rows(params)
        return [self._serialize_row(row) for row in rows]
