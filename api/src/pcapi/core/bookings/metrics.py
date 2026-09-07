from prometheus_client import Counter
from prometheus_client import Histogram


bookings_succeeded_counter = Counter(
    "bookings_succeeded_total",
    "Total number of bookings that succeeded",
    labelnames=["provider_id", "provider_label", "subcategory_id"],
)

bookings_failed_counter = Counter(
    "bookings_failed_total",
    "Total number of bookings that failed",
    labelnames=["provider_id", "provider_label", "subcategory_id", "error_code", "error_message"],
)

external_bookings_execution_time_histogram = Histogram(
    "external_bookings_execution_time",
    "Time needed to run external booking (cinema or event)",
    labelnames=["provider_id", "provider_label", "subcategory_id"],
)
