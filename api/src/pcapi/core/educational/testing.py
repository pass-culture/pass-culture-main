from pcapi.core.educational import models
from pcapi.core.educational.adage_backends.serialize import AdageCollectiveOffer
from pcapi.core.educational.adage_backends.serialize import AdageCollectiveRequest
from pcapi.core.educational.schemas import EducationalBookingResponse


AdageRequestItem = (
    str | AdageCollectiveOffer | AdageCollectiveRequest | EducationalBookingResponse | dict[str, int | str | None]
)

adage_requests: list[dict[str, AdageRequestItem | None]] = []


def reset_requests() -> None:
    global adage_requests  # noqa: PLW0603 (global-statement)
    adage_requests = []


PATCH_CAN_CREATE_OFFER_PATH = "pcapi.core.offerers.api.can_offerer_create_educational_offer"

STATUSES_ALLOWING_EDIT_DETAILS = (
    models.CollectiveOfferDisplayedStatus.DRAFT,
    models.CollectiveOfferDisplayedStatus.PUBLISHED,
    models.CollectiveOfferDisplayedStatus.PREBOOKED,
)

STATUSES_NOT_ALLOWING_EDIT_DETAILS = tuple(
    set(models.CollectiveOfferDisplayedStatus)
    - {*STATUSES_ALLOWING_EDIT_DETAILS, models.CollectiveOfferDisplayedStatus.HIDDEN}
)

STATUSES_ALLOWING_EDIT_DETAILS_TEMPLATE = (
    models.CollectiveOfferDisplayedStatus.DRAFT,
    models.CollectiveOfferDisplayedStatus.PUBLISHED,
    models.CollectiveOfferDisplayedStatus.HIDDEN,
    models.CollectiveOfferDisplayedStatus.ENDED,
)

STATUSES_NOT_ALLOWING_EDIT_DETAILS_TEMPLATE = (
    models.CollectiveOfferDisplayedStatus.UNDER_REVIEW,
    models.CollectiveOfferDisplayedStatus.REJECTED,
    models.CollectiveOfferDisplayedStatus.ARCHIVED,
)

STATUSES_ALLOWING_CREATE_BOOKABLE_OFFER = (
    models.CollectiveOfferDisplayedStatus.PUBLISHED,
    models.CollectiveOfferDisplayedStatus.HIDDEN,
    models.CollectiveOfferDisplayedStatus.ENDED,
)

STATUSES_NOT_ALLOWING_CREATE_BOOKABLE_OFFER = (
    models.CollectiveOfferDisplayedStatus.DRAFT,
    models.CollectiveOfferDisplayedStatus.UNDER_REVIEW,
    models.CollectiveOfferDisplayedStatus.REJECTED,
    models.CollectiveOfferDisplayedStatus.ARCHIVED,
)

STATUSES_ALLOWING_ARCHIVE_OFFER = (
    models.CollectiveOfferDisplayedStatus.DRAFT,
    models.CollectiveOfferDisplayedStatus.PUBLISHED,
    models.CollectiveOfferDisplayedStatus.REJECTED,
    models.CollectiveOfferDisplayedStatus.EXPIRED,
    models.CollectiveOfferDisplayedStatus.REIMBURSED,
    models.CollectiveOfferDisplayedStatus.CANCELLED,
)

STATUSES_NOT_ALLOWING_ARCHIVE_OFFER = (
    models.CollectiveOfferDisplayedStatus.UNDER_REVIEW,
    models.CollectiveOfferDisplayedStatus.PREBOOKED,
    models.CollectiveOfferDisplayedStatus.BOOKED,
    models.CollectiveOfferDisplayedStatus.ENDED,
    models.CollectiveOfferDisplayedStatus.ARCHIVED,
)

STATUSES_ALLOWING_ARCHIVE_OFFER_TEMPLATE = (
    models.CollectiveOfferDisplayedStatus.DRAFT,
    models.CollectiveOfferDisplayedStatus.PUBLISHED,
    models.CollectiveOfferDisplayedStatus.REJECTED,
    models.CollectiveOfferDisplayedStatus.HIDDEN,
    models.CollectiveOfferDisplayedStatus.ENDED,
)

STATUSES_NOT_ALLOWING_ARCHIVE_OFFER_TEMPLATE = (
    models.CollectiveOfferDisplayedStatus.UNDER_REVIEW,
    models.CollectiveOfferDisplayedStatus.ARCHIVED,
)

ADDRESS_DICT = {
    "isVenueAddress": False,
    "isManualEdition": False,
    "city": "Paris",
    "label": "My address",
    "latitude": "48.87171",
    "longitude": "2.308289",
    "postalCode": "75001",
    "street": "3 Rue de Valois",
}
