# Decide what worker class we are going to use and apply the relevant settings
# Since using the gevent worker class is only a test for now, only settings related to that
# are applied here. If we decide to go through with this, we should choose if we setup
# gunicorn configuration here or in entrypoint.sh but not both.
# We should do that as early as possible because gevent needs to patch the standard library before importing stuff that calls
# blocking IO
import os


worker_class = os.environ.get("GUNICORN_WORKER_CLASS", "gthread")

if worker_class == "gevent":
    import gevent.monkey

    gevent.monkey.patch_all()
    if "GUNICORN_WORKER_CONNECTIONS" in os.environ:
        workers = os.environ["GUNICORN_WORKER_CONNECTIONS"]
elif worker_class == "gthread":
    if "GUNICORN_WORKERS" in os.environ:
        workers = os.environ["GUNICORN_WORKERS"]
    if "GUNICORN_THREADS" in os.environ:
        threads = os.environ["GUNICORN_THREADS"]
else:
    raise ValueError("specified gunicorn worker type is not supported")

# mypy: disable-error-code="no-untyped-def"
import logging  # noqa: E402
import pathlib  # noqa: E402

import gunicorn.config  # noqa: E402
import prometheus_client  # noqa: E402
from prometheus_client import multiprocess  # noqa: E402
from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics  # noqa: E402

from pcapi.flask_app import app  # noqa: E402
from pcapi.models import db  # noqa: E402
from pcapi.utils import kubernetes as kubernetes_utils  # noqa: E402


FLASK_PROMETHEUS_EXPORTER_PORT = int(os.environ.get("FLASK_PROMETHEUS_EXPORTER_PORT", "5002"))
ENABLE_FLASK_PROMETHEUS_EXPORTER = int(os.environ.get("ENABLE_FLASK_PROMETHEUS_EXPORTER", "0"))
FLASK_PROMETHEUS_EXPORTER_METRICS_DIR = os.environ.get("PROMETHEUS_MULTIPROC_DIR")
KUBERNETES_DEPLOYMENT = kubernetes_utils.get_deployment()

logger = logging.getLogger(__name__)


def when_ready(server):
    if ENABLE_FLASK_PROMETHEUS_EXPORTER:
        GunicornPrometheusMetrics.start_http_server_when_ready(FLASK_PROMETHEUS_EXPORTER_PORT)
        print(f"started Prometheus export server on port {FLASK_PROMETHEUS_EXPORTER_PORT}")


def child_exit(server, worker):
    if not ENABLE_FLASK_PROMETHEUS_EXPORTER:
        return

    _mark_dead_worker(worker.pid)

    try:
        _clean_up_prometheus_metrics_directory(worker.pid)
    except Exception:
        logger.exception("Got error while cleaning up Prometheus metrics directory")


def worker_exit(server, worker):
    if not ENABLE_FLASK_PROMETHEUS_EXPORTER:
        return

    _mark_dead_worker(worker.pid)

    try:
        _clean_up_prometheus_metrics_directory(worker.pid)
    except Exception:
        logger.exception("Got error while cleaning up Prometheus metrics directory")


def _mark_dead_worker(pid: int) -> None:
    # Mark dead through both helper and official prom client call
    # so that collectors using live modes and dead markers behave correctly.
    try:
        GunicornPrometheusMetrics.mark_process_dead_on_child_exit(pid)
    except Exception:
        logger.exception("Failed to mark worker dead via GunicornPrometheusMetrics")

    try:
        multiprocess.mark_process_dead(pid)
    except Exception:
        logger.exception("Failed to mark worker dead via prometheus_client.multiprocess")


def _clean_up_prometheus_metrics_directory(pid: int) -> None:
    if not FLASK_PROMETHEUS_EXPORTER_METRICS_DIR:
        return
    directory = pathlib.Path(FLASK_PROMETHEUS_EXPORTER_METRICS_DIR)
    for path in directory.glob(f"*_{pid}.db"):
        path.unlink(missing_ok=True)


def pre_fork(server, worker):
    """Called before a Gunicorn worker is forked."""
    # We need to drop all connections to the database to prevent those
    # from being shared among dfferent workers processes once all initialisation
    # have been made
    # See https://docs.sqlalchemy.org/en/14/core/pooling.html#using-connection-pools-with-multiprocessing-or-os-fork
    with app.app_context():
        if db and db.engine:
            db.engine.dispose()


def post_fork(server, worker):
    """Called when a Gunicorn worker is started."""
    if not ENABLE_FLASK_PROMETHEUS_EXPORTER:
        return

    # Use livesum so only live worker processes contribute, even if stale files exist.
    threads = int(worker.cfg.settings["threads"].value or 1)

    worker.total_threads = prometheus_client.Gauge(
        "gunicorn_total_threads",
        "Number of total Gunicorn threads running",
        multiprocess_mode="livesum",
    )
    worker.available_threads = prometheus_client.Gauge(
        "gunicorn_available_threads",
        "Number of Gunicorn threads that are not busy processing a request",
        multiprocess_mode="livesum",
    )

    worker.total_threads.set(threads)
    worker.available_threads.set(threads)


def pre_request(worker, req):
    gunicorn.config.PreRequest.default(worker, req)
    if ENABLE_FLASK_PROMETHEUS_EXPORTER:
        worker.available_threads.dec()


def post_request(worker, req, environ, resp):
    if ENABLE_FLASK_PROMETHEUS_EXPORTER:
        worker.available_threads.inc()
