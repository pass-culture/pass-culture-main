from pcapi import settings
from pcapi.connectors.clickhouse_backends.base import BaseBackend
from pcapi.utils.module_loading import import_string


clickhouse_backend: BaseBackend = import_string(settings.CLICKHOUSE_BACKEND)()
