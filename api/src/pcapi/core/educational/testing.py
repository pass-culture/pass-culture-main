from pcapi.core.educational.adage_backends.serialize import AdageCollectiveOffer
from pcapi.core.educational.adage_backends.serialize import AdageCollectiveRequest
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse


AdageRequestItem = (
    str | AdageCollectiveOffer | AdageCollectiveRequest | EducationalBookingResponse | dict[str, int | str | None]
)

adage_requests: list[dict[str, AdageRequestItem | None]] = []


def reset_requests() -> None:
    global adage_requests  # pylint: disable=global-statement
    adage_requests = []
