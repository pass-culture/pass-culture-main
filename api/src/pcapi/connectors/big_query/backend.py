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
            import os

            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow

            scopes = [
                "https://www.googleapis.com/auth/bigquery",
                "https://www.googleapis.com/auth/cloud-platform",
            ]

            creds = None
            if os.path.exists("token.json"):
                creds = Credentials.from_authorized_user_file("token.json", scopes=scopes)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scopes=scopes)
                    creds = flow.run_local_server(port=5002)
                # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

            self._client = bigquery.Client(project="passculture-metier-ehp", credentials=creds, location="europe-west1")
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
