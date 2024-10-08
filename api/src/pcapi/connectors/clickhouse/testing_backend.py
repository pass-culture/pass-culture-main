import typing

from sqlalchemy import engine

from .backend import BaseBackend


class TestingBackend(BaseBackend):

    def _get_engine(self) -> engine.Engine:
        raise NotImplementedError

    def run_query(self, query: str, params: typing.Tuple) -> list:
        return []
