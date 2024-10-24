"""
To make this work locally :s

# Connect to the data ehp with tsh

# local proxy to clickhouse
# kubectl port-forward clickhouse-shard0-0 8123:8123
"""

from sqlalchemy import create_engine
from sqlalchemy import engine

from pcapi import settings
from pcapi.routes.serialization.statistics_serialize import YearlyAggregatedRevenue
from pcapi.utils.module_loading import import_string

from .base import BaseBackend


class ClickhouseApiException(Exception):
    pass


def get_backend() -> "BaseBackend":
    backend_class = import_string(settings.CLICKHOUSE_BACKEND)
    return backend_class()


class ClickhouseBackend(BaseBackend):
    def _get_engine(self) -> engine.Engine:
        ip = settings.CLICKHOUSE_IP
        user = str(settings.CLICKHOUSE_USER)
        password = str(settings.CLICKHOUSE_PASSWORD)
        uri = f"clickhouse://{user}:{password}@{ip}:8123/default?protocol=http"
        return create_engine(uri, pool_pre_ping=True)
