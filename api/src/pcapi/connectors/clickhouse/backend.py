import logging
import typing

from sqlalchemy import create_engine
from sqlalchemy import engine

from pcapi import settings
from pcapi.models.api_errors import ApiErrors
from pcapi.utils import requests
from pcapi.utils.module_loading import import_string


logger = logging.getLogger(__name__)


def get_backend() -> "BaseBackend":
    backend_class = import_string(settings.CLICKHOUSE_BACKEND)
    return backend_class()


class BaseBackend:
    def __init__(self) -> None:
        self._engine: engine.Engine | None = None

    def _get_engine(self) -> engine.Engine:
        raise NotImplementedError

    @property
    def engine(self) -> engine.Engine:
        if not self._engine:
            self._engine = self._get_engine()
        return self._engine

    def run_query(self, query: str, params: typing.Tuple) -> list:
        try:
            results = self.engine.execute(query, params).fetchall()
        except Exception as err:
            logger.error("%s when querying Clickhouse: %s", type(err), str(err))
            if isinstance(err, requests.exceptions.ConnectionError):
                raise ApiErrors(errors={"clickhouse": "Can not connect to clickhouse server"}, status_code=422)
            raise ApiErrors(errors={"clickhouse": f"Error : {err}"}, status_code=400)
        return results


class ClickhouseBackend(BaseBackend):
    def _get_engine(self) -> engine.Engine:
        ip = settings.CLICKHOUSE_IP
        user = settings.CLICKHOUSE_USER
        password = settings.CLICKHOUSE_PASSWORD
        uri = f"clickhouse://{user}:{password}@{ip}:8123/default?protocol=http"
        return create_engine(uri, pool_pre_ping=True)
