import os

from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics


FLASK_PROMETHEUS_EXPORTER_PORT = int(os.environ.get("FLASK_PROMETHEUS_EXPORTER_PORT", "5002"))


def when_ready(server):
    if int(os.environ.get("ENABLE_FLASK_PROMETHEUS_EXPORTER", "0")):
        GunicornPrometheusMetrics.start_http_server_when_ready(FLASK_PROMETHEUS_EXPORTER_PORT)
        print(f"started Prometheus export server on port {FLASK_PROMETHEUS_EXPORTER_PORT}")


def child_exit(server, worker):
    if int(os.environ.get("ENABLE_FLASK_PROMETHEUS_EXPORTER", "0")):
        GunicornPrometheusMetrics.mark_process_dead_on_child_exit(worker.pid)
