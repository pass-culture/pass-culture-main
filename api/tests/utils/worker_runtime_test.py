import sys
import types
from unittest import mock

import pytest

from pcapi.utils import worker_runtime


class GetWorkerConcurrencyTest:
    def test_gthread_uses_threads(self):
        assert (
            worker_runtime.get_worker_concurrency("gthread", threads=5, worker_connections=1000, db_pool_capacity=30)
            == 5
        )

    def test_gevent_is_bounded_by_db_pool(self):
        """Requests needing the database wait for a pool connection: autoscaling must see that limit, not 1000."""
        assert (
            worker_runtime.get_worker_concurrency("gevent", threads=5, worker_connections=1000, db_pool_capacity=30)
            == 30
        )

    def test_gevent_is_bounded_by_worker_connections(self):
        assert (
            worker_runtime.get_worker_concurrency("gevent", threads=5, worker_connections=20, db_pool_capacity=30) == 20
        )


class PatchForGeventTest:
    def test_installs_psycopg_and_grpc_hooks(self):
        """Both hooks are needed, otherwise SQL or gRPC calls block the whole gevent worker."""
        calls = []
        psycogreen_gevent = types.ModuleType("psycogreen.gevent")
        psycogreen_gevent.patch_psycopg = lambda: calls.append("psycopg")
        grpc_gevent = types.ModuleType("grpc.experimental.gevent")
        grpc_gevent.init_gevent = lambda: calls.append("grpc")
        psycogreen = types.ModuleType("psycogreen")
        psycogreen.gevent = psycogreen_gevent

        with mock.patch.dict(
            sys.modules,
            {
                "psycogreen": psycogreen,
                "psycogreen.gevent": psycogreen_gevent,
                "grpc.experimental.gevent": grpc_gevent,
            },
        ):
            worker_runtime.patch_for_gevent()

        assert sorted(calls) == ["grpc", "psycopg"]

    def test_fails_loudly_when_psycogreen_is_missing(self):
        """A gevent worker without the psycopg2 hook would block on every SQL query: refuse to start instead."""
        with mock.patch.dict(sys.modules, {"psycogreen": None, "psycogreen.gevent": None}):
            with pytest.raises(ImportError):
                worker_runtime.patch_for_gevent()
