import typing

from .backend import BaseBackend


TestingRow = typing.TypeVar("TestingRow")
TestingRowIterator = typing.Generator[TestingRow]


class TestingBackend(BaseBackend):
    def run_query(self, query: str, page_size: int, **parameters: typing.Any) -> TestingRowIterator:
        yield from ()
