import logging
import os
import pathlib

from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics


FLASK_PROMETHEUS_EXPORTER_PORT = int(os.environ.get("FLASK_PROMETHEUS_EXPORTER_PORT", "5002"))
ENABLE_FLASK_PROMETHEUS_EXPORTER = int(os.environ.get("ENABLE_FLASK_PROMETHEUS_EXPORTER", "0"))
FLASK_PROMETHEUS_EXPORTER_METRICS_DIR = os.environ.get("PROMETHEUS_MULTIPROC_DIR")

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
        except:
            logger.exception("Got error while cleaning up Prometheus metrics directory")


def _clean_up_prometheus_metrics_directory(worker):
    directory = pathlib.Path(FLASK_PROMETHEUS_EXPORTER_METRICS_DIR)
    for path in directory.glob(f"*_{worker.pid}.db"):
        path.unlink(missing_ok=True)
