"""
Ensure that the BaseQuery runs well: data is fetched, rows are
properly serialized and yielded.
"""

from unittest.mock import patch

import pydantic.v1 as pydantic_v1
import pytest

from pcapi.connectors.big_query.queries import base


class FooModel(pydantic_v1.BaseModel):
    id: int
    name: str


class FooQuery(base.BaseQuery):
    raw_query = "SELECT * FROM table"
    model = FooModel


def test_get_rows():
    rows = [{"id": 1, "name": "aa"}, {"id": 2, "name": "bb"}]

    with patch("pcapi.connectors.big_query.TestingBackend.run_query") as mock_run_query:
        query = FooQuery()
        mock_run_query.return_value = rows
        assert list(query.execute()) == [FooModel(id=1, name="aa"), FooModel(id=2, name="bb")]


def test_unexpected_row():
    rows_with_error = [{"id": 1, "name": "aa"}, {"unexpectedKey": "someValue"}]

    with patch("pcapi.connectors.big_query.TestingBackend.run_query") as mock_run_query:
        query = FooQuery()
        mock_run_query.return_value = rows_with_error

        with pytest.raises(base.MalformedRow):
            list(query.execute())
