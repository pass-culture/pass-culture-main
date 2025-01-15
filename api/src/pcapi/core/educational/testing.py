from pcapi.core.educational import models
from pcapi.core.educational.adage_backends.serialize import AdageCollectiveOffer
from pcapi.core.educational.adage_backends.serialize import AdageCollectiveRequest
from pcapi.core.educational.schemas import EducationalBookingResponse


AdageRequestItem = (
    str | AdageCollectiveOffer | AdageCollectiveRequest | EducationalBookingResponse | dict[str, int | str | None]
)

adage_requests: list[dict[str, AdageRequestItem | None]] = []


def reset_requests() -> None:
    global adage_requests  # pylint: disable=global-statement
    adage_requests = []


STATUSES_ALLOWING_EDIT_DETAILS = (
    models.CollectiveOfferDisplayedStatus.DRAFT,
    models.CollectiveOfferDisplayedStatus.ACTIVE,
    models.CollectiveOfferDisplayedStatus.PREBOOKED,
)

STATUSES_NOT_ALLOWING_EDIT_DETAILS = tuple(
    set(models.CollectiveOfferDisplayedStatus)
    - {*STATUSES_ALLOWING_EDIT_DETAILS, models.CollectiveOfferDisplayedStatus.INACTIVE}
)
