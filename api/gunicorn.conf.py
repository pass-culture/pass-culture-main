# mypy: disable-error-code="no-untyped-def"
import logging
import os
import pathlib

import gunicorn.config
import prometheus_client
import prometheus_client.registry
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
    if ENABLE_FLASK_PROMETHEUS_EXPORTER:
        GunicornPrometheusMetrics.mark_process_dead_on_child_exit(worker.pid)
        try:
            _clean_up_prometheus_metrics_directory(worker)
        except Exception:
            logger.exception("Got error while cleaning up Prometheus metrics directory")


def _clean_up_prometheus_metrics_directory(worker):
    directory = pathlib.Path(FLASK_PROMETHEUS_EXPORTER_METRICS_DIR)
    for path in directory.glob(f"*_{worker.pid}.db"):
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
    if ENABLE_FLASK_PROMETHEUS_EXPORTER:
        registry = prometheus_client.registry.CollectorRegistry()
        # We could export a ratio (percentage) of availability (number
        # of available threads divided by total threads), but each pod
        # would export a value, which would have to be averaged to
        # calculate the overall ratio. Instead, we export 2 metrics
        # (total and available) and let Grafana and Alert Manager
        # calculate the ratio.

        # Use those metrics instead
        worker.total_threads = prometheus_client.Gauge(
            "gunicorn_total_threads",
            "Number of total Gunicorn threads running",
            registry=registry,
            multiprocess_mode="sum",
        )
        worker.total_threads.set(worker.cfg.settings["threads"].value)
        worker.available_threads = prometheus_client.Gauge(
            "gunicorn_available_threads",
            "Number of Gunicorn threads that are not busy processing a request",
            registry=registry,
            multiprocess_mode="sum",
        )
        worker.available_threads.set(worker.cfg.settings["threads"].value)


def pre_request(worker, req):
    gunicorn.config.PreRequest.default(worker, req)
    if ENABLE_FLASK_PROMETHEUS_EXPORTER:
        worker.available_threads.dec()


def post_request(worker, req, environ, resp):
    if ENABLE_FLASK_PROMETHEUS_EXPORTER:
        worker.available_threads.inc()
