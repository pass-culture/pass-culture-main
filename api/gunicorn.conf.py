# mypy: disable-error-code="no-untyped-def"
import logging
import os
import pathlib

import gunicorn.config
import prometheus_client
from prometheus_client import multiprocess
from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics

from pcapi.flask_app import app
from pcapi.models import db
from pcapi.utils import kubernetes as kubernetes_utils


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
