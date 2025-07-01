"""
Prometheus metrics utilities for outgoing HTTP requests.

**NOTE:**
We are using the request `host` as a label for the metrics created here.
For webhooks this carries a risk: as the number of external vendors increase, so will the cardinality (number of different values) of this label,
increasing Prometheus storage space and slowing down crawling.
See https://grafana.com/blog/2022/10/20/how-to-manage-high-cardinality-metrics-in-prometheus-and-kubernetes/

We made this choice because we only have ~40 external vendors and it would likely be fine up to a few hundred;
but this decision might need to be revisited as the number increases.

"""

import time
from typing import Any
from urllib.parse import urlparse

from prometheus_client import Counter
from prometheus_client import Histogram


# Global metrics registry to avoid re-registering metrics
_metrics_registry: dict[str, tuple[Histogram, Counter]] = {}


def get_or_create_http_metrics(name_suffix: str) -> tuple[Histogram, Counter]:
    """Get or create Prometheus metrics for HTTP requests with the given prefix."""
    if name_suffix in _metrics_registry:
        return _metrics_registry[name_suffix]

    # Create histogram for request duration
    duration_histogram = Histogram(
        name=f"http_request_duration_seconds_{name_suffix}",
        documentation=f"Duration of HTTP requests for {name_suffix} in seconds",
        labelnames=["method", "url_pattern", "status_code"],
        buckets=(0.05, 0.25, 1.0, 5.0, 10.0, 60.0, float("inf")),
    )

    # Create counter for request count by status code
    status_counter = Counter(
        name=f"http_requests_total_{name_suffix}",
        documentation=f"Total number of HTTP requests for {name_suffix}",
        labelnames=["method", "url_pattern", "status_code"],
    )

    _metrics_registry[name_suffix] = (duration_histogram, status_counter)
    return duration_histogram, status_counter


def get_host(url: str) -> str:
    """Extract URL host"""
    try:
        parsed = urlparse(url)
        host = parsed.netloc
        return host
    except Exception:
        return "unknown"


class HttpMetricsContext:
    """Context manager for recording HTTP request metrics."""

    def __init__(self, name_suffix: str, method: str, url: str):
        self.name_suffix = name_suffix
        self.method = method
        self.url = url
        self.start_time: float | None = None
        self.duration_histogram: Histogram | None = None
        self.status_counter: Counter | None = None

    def __enter__(self) -> "HttpMetricsContext":
        if self.name_suffix:
            self.duration_histogram, self.status_counter = get_or_create_http_metrics(self.name_suffix)
            self.start_time = time.time()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if not self.duration_histogram or not self.status_counter or self.start_time is None:
            return

        duration_seconds = time.time() - self.start_time
        host = get_host(self.url)
        method = self.method or "UNKNOWN"

        # Use status code 0 for connection errors, timeouts, etc.
        status_code = "0" if exc_type else getattr(self, "_status_code", "0")

        self.duration_histogram.labels(method=method, host=host, status_code=status_code).observe(duration_seconds)

        self.status_counter.labels(method=method, host=host, status_code=status_code).inc()

    def record_response(self, status_code: int) -> None:
        """Record the response status code for successful requests."""
        self._status_code = str(status_code)
