import typing

from google.cloud import bigquery
from google.cloud.bigquery import ScalarQueryParameter

from pcapi import settings
from pcapi.utils.module_loading import import_string


def get_backend() -> "BaseBackend":
    backend_class = import_string(settings.GOOGLE_BIG_QUERY_BACKEND)
    return backend_class()


Row = bigquery.table.Row
BigQueryRowIterator = typing.Generator[Row, None, None]


class BaseBackend:
    def __init__(self) -> None:
        self._client: bigquery.Client | None = None

    @property
    def client(self) -> bigquery.Client:
        if not self._client:
            self._client = bigquery.Client()
        return self._client

    def run_query(self, query: str, page_size: int, **parameters: typing.Any) -> BigQueryRowIterator:
        query_parameters: list[ScalarQueryParameter] = []
        for name, value in parameters.items():
            if isinstance(value, int):
                query_parameters.append(ScalarQueryParameter(name, "INT64", value))
            elif isinstance(value, str):
                query_parameters.append(ScalarQueryParameter(name, "STRING", value))
            else:
                raise ValueError(f"Unexpected type {type(value)} for value {value} of parameter {name}")

        job_config = bigquery.QueryJobConfig(query_parameters=query_parameters)

        query_job = self.client.query(query, job_config=job_config)
        return (row for row in query_job.result(page_size))
