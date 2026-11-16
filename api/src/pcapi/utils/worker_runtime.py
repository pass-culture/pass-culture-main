"""Runtime adjustments that depend on the Gunicorn worker class.

gevent only helps if every blocking call yields to its event loop: the standard
library is monkey-patched in `gunicorn.conf.py`, but psycopg2 (a C extension) and
gRPC (used by Google Cloud client libraries) need their own hooks.
"""

GEVENT_WORKER_CLASS = "gevent"


def patch_for_gevent() -> None:
    """Make psycopg2 and gRPC cooperative with gevent.

    Must be called after `gevent.monkey.patch_all()` and before any database
    connection or gRPC object is created.
    """
    from grpc.experimental import gevent as grpc_gevent
    from psycogreen import gevent as psycogreen_gevent

    psycogreen_gevent.patch_psycopg()
    grpc_gevent.init_gevent()


def get_worker_concurrency(worker_class: str, threads: int, worker_connections: int, db_pool_capacity: int) -> int:
    """Return how many requests a single worker can handle concurrently.

    gthread workers are bounded by their thread count. gevent ignores `threads`:
    a worker accepts up to `worker_connections` clients, but requests needing the
    database wait for one of its `db_pool_capacity` connections, which is the
    binding limit for capacity metrics and autoscaling.
    """
    if worker_class == GEVENT_WORKER_CLASS:
        return min(worker_connections, db_pool_capacity)
    return threads
