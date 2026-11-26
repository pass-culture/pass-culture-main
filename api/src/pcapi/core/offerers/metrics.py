from prometheus_client import Counter


venue_requests_counter = Counter(
    "venue_requests_total",
    "Total number of venue requests",
)

venue_requests_error_counter = Counter(
    "venue_requests_error_total",
    "Total number of venue errors",
    labelnames=["error_type"],
)
