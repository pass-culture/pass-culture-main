import typing

from .backend import BaseBackend


TestingRow = typing.TypeVar("TestingRow")
TestingRowIterator = typing.Generator[TestingRow, None, None]


class TestingBackend(BaseBackend):
    def run_query(self, query: str, page_size: int) -> TestingRowIterator:
        yield
