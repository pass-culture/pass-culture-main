import typing
from collections.abc import Mapping

import pydantic.v1 as pydantic_v1

import pcapi.connectors.big_query as big_query_connector


Row = typing.TypeVar("Row", bound=pydantic_v1.BaseModel)
RowIterator = typing.Generator[Row, None, None]


class MalformedRow(Exception):
    def __init__(self, msg: str, index: int, model: type[pydantic_v1.BaseModel], raw_query: str):
        self.index = index
        self.model = model
        self.raw_query = raw_query
        super().__init__(msg)


class BaseQuery:
    def __init__(self) -> None:
        self.backend = big_query_connector.get_backend()

    def _get_rows(self, page_size: int, **parameters: typing.Any) -> big_query_connector.BigQueryRowIterator:
        return self.backend.run_query(self.raw_query, page_size=page_size, **parameters)

    def execute(self, page_size: int = 1_000, **parameters: typing.Any) -> RowIterator:
        rows = self._get_rows(page_size, **parameters)
        for index, row in enumerate(rows):
            try:
                yield self.model(**typing.cast(Mapping, row))
            except (pydantic_v1.ValidationError, TypeError) as err:
                raise MalformedRow(msg=str(row), index=index, model=self.model, raw_query=self.raw_query) from err

    @property
    def raw_query(self) -> str:
        raise NotImplementedError()

    @property
    def model(self) -> type[pydantic_v1.BaseModel]:
        raise NotImplementedError()
