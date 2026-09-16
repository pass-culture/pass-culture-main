import enum
import time
import typing
from dataclasses import dataclass

from google.cloud.logging_v2.services.logging_service_v2 import LoggingServiceV2Client
from google.cloud.logging_v2.services.logging_service_v2.pagers import ListLogEntriesPager
from google.cloud.logging_v2.types import ListLogEntriesRequest

from pcapi import settings
from pcapi.utils.module_loading import import_string


class Severity(enum.Enum):
    DEFAULT = 0
    DEBUG = 100
    INFO = 200
    NOTICE = 300
    WARNING = 400
    ERROR = 500
    CRITICAL = 600
    ALERT = 700
    EMERGENCY = 800


@dataclass(frozen=True, slots=True)
class Log:
    insert_id: str
    timestamp: float
    text: str
    user_id: int | None
    impersonator_id: int | None
    severity: Severity
    extra: dict


def get_backend(project_id: str = settings.GCP_PROJECT) -> "BaseBackend":
    backend_class = import_string(settings.GCP_LOGS_BACKEND)
    return backend_class(project_id=project_id)


class BaseBackend:
    def __init__(self, project_id: str = settings.GCP_PROJECT):
        raise NotImplementedError()

    def get_logs(self, filters: str, limit: int = 50) -> typing.Generator[Log]:
        raise NotImplementedError()


class TestingBackend(BaseBackend):
    def __init__(self, project_id: str = settings.GCP_PROJECT):
        self.project_id = project_id

    def get_logs(self, filters: str, limit: int = 50) -> typing.Generator[Log]:
        chunk_start = time.time()
        time.sleep(1)  # simulate api call
        yield Log(
            insert_id=f"insert_id_{int(chunk_start)}",
            timestamp=chunk_start,
            text=f"message {chunk_start}",
            user_id=int(chunk_start) % 10,
            impersonator_id=None,
            severity=Severity((int(chunk_start) % 9) * 100),
            extra={
                "generator": "testing backend",
                "inside_dict": {
                    "key1": "value 1",
                    "key2": "value 2",
                    "key3": "value 3",
                    "key4": "value 4",
                    "key5": "value 5",
                },
                "search_filters": filters,
            },
        )


class GoogleLogsBackend(BaseBackend):
    def __init__(self, project_id: str = settings.GCP_PROJECT):
        self.project_id = project_id

    @property
    def client(self) -> LoggingServiceV2Client:
        if not hasattr(self, "_client"):
            self._client = LoggingServiceV2Client()
        return self._client

    def _list_log_entries(self, filters: str, page_size: int = 50) -> ListLogEntriesPager:
        return self.client.list_log_entries(
            ListLogEntriesRequest(
                resource_names=["projects/pc-backend-tst"],
                filter=filters,
                order_by="timestamp desc",
                page_size=page_size,
            )
        )

    def get_logs(self, filters: str, limit: int = 50) -> typing.Generator[Log]:
        for _, log in zip(range(limit), self._list_log_entries(filters, page_size=limit)):
            payload = log.json_payload
            yield Log(
                insert_id=log.insert_id,
                timestamp=log.timestamp.timestamp(),  # type: ignore [attr-defined]
                text=payload.get("message", ""),  # type: ignore [attr-defined]
                user_id=int(payload["user_id"]) if "user_id" in payload else None,  # type: ignore [arg-type]
                impersonator_id=int(payload["impersonator_id"]) if "impersonator_id" in payload else None,  # type: ignore [arg-type]
                severity=Severity(log.severity),
                extra=dict(payload.get("extra", {})),  # type: ignore [attr-defined]
            )
