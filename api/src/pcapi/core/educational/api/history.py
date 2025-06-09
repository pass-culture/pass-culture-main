import dataclasses
import datetime
import enum
import logging
import typing

from pcapi.core.educational import models


logger = logging.getLogger(__name__)


CollectiveOfferHistoryStatus = (
    models.CollectiveOfferDisplayedStatus
    | typing.Literal["WAITING_FOR_PREBOOK"]
    | typing.Literal["WAITING_FOR_BOOK"]
    | typing.Literal["WAITING_FOR_REIMBURSEMENT"]
)


class CollectiveOfferHistoryStepStatus(enum.Enum):
    PAST = "PAST"
    CURRENT = "CURRENT"
    FUTURE = "FUTURE"


@dataclasses.dataclass
class CollectiveOfferHistoryStep:
    offer_status: CollectiveOfferHistoryStatus
    step_status: CollectiveOfferHistoryStepStatus
    datetime: datetime.datetime | None


COLLECTIVE_OFFER_NEXT_STATUS_BY_STATUS: typing.Final[
    dict[models.CollectiveOfferDisplayedStatus, models.CollectiveOfferDisplayedStatus | None]
] = {
    models.CollectiveOfferDisplayedStatus.DRAFT: models.CollectiveOfferDisplayedStatus.PUBLISHED,
    models.CollectiveOfferDisplayedStatus.UNDER_REVIEW: models.CollectiveOfferDisplayedStatus.PUBLISHED,
    models.CollectiveOfferDisplayedStatus.REJECTED: None,
    models.CollectiveOfferDisplayedStatus.PUBLISHED: models.CollectiveOfferDisplayedStatus.PREBOOKED,
    models.CollectiveOfferDisplayedStatus.PREBOOKED: models.CollectiveOfferDisplayedStatus.BOOKED,
    models.CollectiveOfferDisplayedStatus.BOOKED: models.CollectiveOfferDisplayedStatus.ENDED,
    models.CollectiveOfferDisplayedStatus.ENDED: models.CollectiveOfferDisplayedStatus.REIMBURSED,
    models.CollectiveOfferDisplayedStatus.REIMBURSED: None,
    models.CollectiveOfferDisplayedStatus.CANCELLED: None,
    models.CollectiveOfferDisplayedStatus.ARCHIVED: None,
    models.CollectiveOfferDisplayedStatus.HIDDEN: None,
}


def _get_status_date(offer: models.CollectiveOffer, status: CollectiveOfferHistoryStatus) -> datetime.datetime | None:
    stock = offer.collectiveStock
    booking = stock.lastBooking if stock is not None else None

    match status:
        case (
            models.CollectiveOfferDisplayedStatus.DRAFT
            | models.CollectiveOfferDisplayedStatus.UNDER_REVIEW
            | "WAITING_FOR_PREBOOK"
            | "WAITING_FOR_BOOK"
            | "WAITING_FOR_REIMBURSEMENT"
        ):
            return None

        case models.CollectiveOfferDisplayedStatus.REJECTED | models.CollectiveOfferDisplayedStatus.PUBLISHED:
            return offer.lastValidationDate

        case models.CollectiveOfferDisplayedStatus.EXPIRED:
            return stock.bookingLimitDatetime

        case models.CollectiveOfferDisplayedStatus.PREBOOKED:
            assert booking is not None
            return booking.dateCreated

        case models.CollectiveOfferDisplayedStatus.BOOKED:
            assert booking is not None
            return booking.confirmationDate

        case models.CollectiveOfferDisplayedStatus.ENDED:
            return stock.endDatetime

        case models.CollectiveOfferDisplayedStatus.REIMBURSED:
            assert booking is not None
            return booking.reimbursementDate

        case models.CollectiveOfferDisplayedStatus.CANCELLED:
            return stock.startDatetime if booking is None else booking.cancellationDate

        case _:
            logger.error("Invalid collective offer history status %s for offer %s", status, offer.id)
            return None


def _get_collective_offer_past_history(
    offer: models.CollectiveOffer,
    from_status: models.CollectiveOfferDisplayedStatus,
    to_status: models.CollectiveOfferDisplayedStatus,
) -> list[CollectiveOfferHistoryStep]:
    steps = []
    next_status: models.CollectiveOfferDisplayedStatus | None = from_status
    while True:
        assert next_status is not None
        steps.append(
            CollectiveOfferHistoryStep(
                offer_status=next_status,
                step_status=CollectiveOfferHistoryStepStatus.PAST,
                datetime=_get_status_date(offer=offer, status=next_status),
            )
        )

        if next_status is None or next_status == to_status:
            break

        next_status = COLLECTIVE_OFFER_NEXT_STATUS_BY_STATUS[next_status]

    return steps


def _get_collective_offer_future_history(
    from_status: models.CollectiveOfferDisplayedStatus,
) -> list[CollectiveOfferHistoryStep]:
    steps = []
    next_status = COLLECTIVE_OFFER_NEXT_STATUS_BY_STATUS[from_status]
    while next_status is not None:
        steps.append(
            CollectiveOfferHistoryStep(
                offer_status=next_status, step_status=CollectiveOfferHistoryStepStatus.FUTURE, datetime=None
            )
        )
        next_status = COLLECTIVE_OFFER_NEXT_STATUS_BY_STATUS[next_status]

    return steps


def get_collective_offer_history(offer: models.CollectiveOffer) -> list[CollectiveOfferHistoryStep]:
    status = offer.displayedStatus
    stock = offer.collectiveStock
    is_two_days_past_end = stock is not None and stock.is_two_days_past_end()
    booking = stock.lastBooking if stock is not None else None
    was_prebooked = booking is not None
    was_booked = booking is not None and booking.confirmationDate is not None

    history: list[CollectiveOfferHistoryStep]
    previous_status = status  # used to fill the history with future steps
    match status:
        case (
            models.CollectiveOfferDisplayedStatus.DRAFT
            | models.CollectiveOfferDisplayedStatus.UNDER_REVIEW
            | models.CollectiveOfferDisplayedStatus.REJECTED
        ):
            history = [
                CollectiveOfferHistoryStep(
                    offer_status=status,
                    step_status=CollectiveOfferHistoryStepStatus.CURRENT,
                    datetime=_get_status_date(offer, status),
                ),
            ]

        case models.CollectiveOfferDisplayedStatus.PUBLISHED:
            history = [
                *_get_collective_offer_past_history(
                    offer=offer,
                    from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                    to_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                ),
                CollectiveOfferHistoryStep(
                    offer_status="WAITING_FOR_PREBOOK",
                    step_status=CollectiveOfferHistoryStepStatus.CURRENT,
                    datetime=_get_status_date(offer, "WAITING_FOR_PREBOOK"),
                ),
            ]

        case models.CollectiveOfferDisplayedStatus.EXPIRED:
            previous_status = (
                models.CollectiveOfferDisplayedStatus.PREBOOKED
                if was_prebooked
                else models.CollectiveOfferDisplayedStatus.PUBLISHED
            )
            history = [
                *_get_collective_offer_past_history(
                    offer=offer,
                    from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                    to_status=previous_status,
                ),
                CollectiveOfferHistoryStep(
                    offer_status=status,
                    step_status=CollectiveOfferHistoryStepStatus.CURRENT,
                    datetime=_get_status_date(offer, status),
                ),
            ]

        case models.CollectiveOfferDisplayedStatus.PREBOOKED:
            history = [
                *_get_collective_offer_past_history(
                    offer=offer,
                    from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                    to_status=models.CollectiveOfferDisplayedStatus.PREBOOKED,
                ),
                CollectiveOfferHistoryStep(
                    offer_status="WAITING_FOR_BOOK",
                    step_status=CollectiveOfferHistoryStepStatus.CURRENT,
                    datetime=_get_status_date(offer, "WAITING_FOR_BOOK"),
                ),
            ]

        case models.CollectiveOfferDisplayedStatus.BOOKED:
            history = [
                *_get_collective_offer_past_history(
                    offer=offer,
                    from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                    to_status=models.CollectiveOfferDisplayedStatus.PREBOOKED,
                ),
                CollectiveOfferHistoryStep(
                    offer_status=status,
                    step_status=CollectiveOfferHistoryStepStatus.CURRENT,
                    datetime=_get_status_date(offer, status),
                ),
            ]

        case models.CollectiveOfferDisplayedStatus.ENDED:
            current_status: CollectiveOfferHistoryStatus
            if is_two_days_past_end:
                previous_status = models.CollectiveOfferDisplayedStatus.ENDED
                current_status = "WAITING_FOR_REIMBURSEMENT"
            else:
                previous_status = models.CollectiveOfferDisplayedStatus.BOOKED
                current_status = models.CollectiveOfferDisplayedStatus.ENDED

            history = [
                *_get_collective_offer_past_history(
                    offer=offer, from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED, to_status=previous_status
                ),
                CollectiveOfferHistoryStep(
                    offer_status=current_status,
                    step_status=CollectiveOfferHistoryStepStatus.CURRENT,
                    datetime=_get_status_date(offer, current_status),
                ),
            ]

        case models.CollectiveOfferDisplayedStatus.REIMBURSED:
            history = _get_collective_offer_past_history(
                offer=offer,
                from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                to_status=models.CollectiveOfferDisplayedStatus.REIMBURSED,
            )

        case models.CollectiveOfferDisplayedStatus.CANCELLED:
            past_status: models.CollectiveOfferDisplayedStatus
            if was_prebooked:
                if was_booked:
                    past_status = models.CollectiveOfferDisplayedStatus.BOOKED
                else:
                    past_status = models.CollectiveOfferDisplayedStatus.PREBOOKED
            else:
                past_status = models.CollectiveOfferDisplayedStatus.PUBLISHED

            history = [
                *_get_collective_offer_past_history(
                    offer=offer,
                    from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                    to_status=past_status,
                ),
                CollectiveOfferHistoryStep(
                    offer_status=status,
                    step_status=CollectiveOfferHistoryStepStatus.CURRENT,
                    datetime=_get_status_date(offer, status),
                ),
            ]

        case models.CollectiveOfferDisplayedStatus.ARCHIVED:
            history = []

        case _:
            logger.error("Invalid collective offer status %s for offer %s", status, offer.id)
            history = []

    history.extend(_get_collective_offer_future_history(previous_status))

    return history
