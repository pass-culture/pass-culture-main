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


PATCH_CAN_CREATE_OFFER_PATH = "pcapi.core.offerers.api.can_offerer_create_educational_offer"

STATUSES_ALLOWING_EDIT_DETAILS = (
    models.CollectiveOfferDisplayedStatus.DRAFT,
    models.CollectiveOfferDisplayedStatus.ACTIVE,
    models.CollectiveOfferDisplayedStatus.PREBOOKED,
)

STATUSES_NOT_ALLOWING_EDIT_DETAILS = tuple(
    set(models.CollectiveOfferDisplayedStatus)
    - {*STATUSES_ALLOWING_EDIT_DETAILS, models.CollectiveOfferDisplayedStatus.INACTIVE}
)

STATUSES_ALLOWING_EDIT_DETAILS_TEMPLATE = (
    models.CollectiveOfferDisplayedStatus.DRAFT,
    models.CollectiveOfferDisplayedStatus.ACTIVE,
    models.CollectiveOfferDisplayedStatus.INACTIVE,
    models.CollectiveOfferDisplayedStatus.ENDED,
)

STATUSES_NOT_ALLOWING_EDIT_DETAILS_TEMPLATE = (
    models.CollectiveOfferDisplayedStatus.PENDING,
    models.CollectiveOfferDisplayedStatus.REJECTED,
    models.CollectiveOfferDisplayedStatus.ARCHIVED,
)

STATUSES_ALLOWING_CREATE_BOOKABLE_OFFER = (
    models.CollectiveOfferDisplayedStatus.ACTIVE,
    models.CollectiveOfferDisplayedStatus.INACTIVE,
    models.CollectiveOfferDisplayedStatus.ENDED,
)

STATUSES_NOT_ALLOWING_CREATE_BOOKABLE_OFFER = (
    models.CollectiveOfferDisplayedStatus.DRAFT,
    models.CollectiveOfferDisplayedStatus.PENDING,
    models.CollectiveOfferDisplayedStatus.REJECTED,
    models.CollectiveOfferDisplayedStatus.ARCHIVED,
)

STATUSES_ALLOWING_ARCHIVE_OFFER = (
    models.CollectiveOfferDisplayedStatus.DRAFT,
    models.CollectiveOfferDisplayedStatus.ACTIVE,
    models.CollectiveOfferDisplayedStatus.INACTIVE,
    models.CollectiveOfferDisplayedStatus.REJECTED,
    models.CollectiveOfferDisplayedStatus.ENDED,
)

STATUSES_NOT_ALLOWING_ARCHIVE_OFFER = (
    models.CollectiveOfferDisplayedStatus.PENDING,
    models.CollectiveOfferDisplayedStatus.ARCHIVED,
)
