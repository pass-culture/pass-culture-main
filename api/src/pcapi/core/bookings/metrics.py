from prometheus_client import Counter
from prometheus_client import Histogram


booking_requests_counter = Counter(
    "booking_requests_total",
    "Total number of booking requests",
    labelnames=["provider_id", "provider_label", "subcategory_id", "status", "error_code"],
)

external_bookings_execution_time_histogram = Histogram(
    "external_bookings_execution_time",
    "Time needed to run external booking (cinema or event)",
    labelnames=["provider_id", "provider_label", "subcategory_id"],
)
