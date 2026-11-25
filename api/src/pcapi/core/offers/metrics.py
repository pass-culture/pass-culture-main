from prometheus_client import Counter


offer_requests_counter = Counter(
    "offer_requests_total",
    "Total number of offer requests",
    labelnames=["api_version", "endpoint"],
)

offer_requests_error_counter = Counter(
    "offer_requests_error_total",
    "Total number of offer errors",
    labelnames=["api_version", "endpoint", "error_type"],
)
