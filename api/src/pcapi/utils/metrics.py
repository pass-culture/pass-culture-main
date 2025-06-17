"""Prometheus metrics utilities for HTTP requests and other operations."""

import time
from typing import Any
from urllib.parse import urlparse

import prometheus_client


# Global metrics registry to avoid re-registering metrics
_metrics_registry: dict[str, tuple[prometheus_client.Histogram, prometheus_client.Counter]] = {}


def get_or_create_http_metrics(prefix: str) -> tuple[prometheus_client.Histogram, prometheus_client.Counter]:
    """Get or create Prometheus metrics for HTTP requests with the given prefix."""
    if prefix in _metrics_registry:
        return _metrics_registry[prefix]

    # Create histogram for request duration
    duration_histogram = prometheus_client.Histogram(
        name=f"{prefix}_http_request_duration_seconds",
        documentation=f"Duration of HTTP requests for {prefix} in seconds",
        labelnames=["method", "url_pattern", "status_code"],
        buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, float("inf")),
    )

    # Create counter for request count by status code
    status_counter = prometheus_client.Counter(
        name=f"{prefix}_http_requests_total",
        documentation=f"Total number of HTTP requests for {prefix}",
        labelnames=["method", "url_pattern", "status_code"],
    )

    _metrics_registry[prefix] = (duration_histogram, status_counter)
    return duration_histogram, status_counter


def get_url_pattern(url: str) -> str:
    """Extract a label-friendly URL pattern from the full URL to avoid high cardinality."""
    try:
        parsed = urlparse(url)
        # Use just the host and first path segment to avoid high cardinality
        host = parsed.netloc
        path_parts = parsed.path.strip("/").split("/")
        if path_parts and path_parts[0]:
            return f"{host}/{path_parts[0]}"
        return host
    except Exception:
        return "unknown"


class HttpMetricsContext:
    """Context manager for recording HTTP request metrics."""

    def __init__(self, prefix: str, method: str, url: str):
        self.prefix = prefix
        self.method = method
        self.url = url
        self.start_time: float | None = None
        self.duration_histogram: prometheus_client.Histogram | None = None
        self.status_counter: prometheus_client.Counter | None = None

    def __enter__(self) -> "HttpMetricsContext":
        if self.prefix:
            self.duration_histogram, self.status_counter = get_or_create_http_metrics(self.prefix)
            self.start_time = time.time()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if not self.duration_histogram or not self.status_counter or self.start_time is None:
            return

        duration = time.time() - self.start_time
        url_pattern = get_url_pattern(self.url)
        method = self.method or "UNKNOWN"

        # Use status code 0 for connection errors, timeouts, etc.
        status_code = "0" if exc_type else getattr(self, "_status_code", "0")

        self.duration_histogram.labels(method=method, url_pattern=url_pattern, status_code=status_code).observe(
            duration
        )

        self.status_counter.labels(method=method, url_pattern=url_pattern, status_code=status_code).inc()

    def record_response(self, status_code: int) -> None:
        """Record the response status code for successful requests."""
        self._status_code = str(status_code)
