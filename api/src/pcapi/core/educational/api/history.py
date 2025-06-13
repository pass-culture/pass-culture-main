import dataclasses
import datetime
import logging
import typing

from pcapi.core.educational import models
from pcapi.routes.serialization import collective_offers_serialize as serialize


logger = logging.getLogger(__name__)


NEXT_STATUS_BY_STATUS: typing.Final[
    dict[models.CollectiveOfferDisplayedStatus, models.CollectiveOfferDisplayedStatus | None]
] = {
    models.CollectiveOfferDisplayedStatus.DRAFT: models.CollectiveOfferDisplayedStatus.PUBLISHED,
    models.CollectiveOfferDisplayedStatus.UNDER_REVIEW: models.CollectiveOfferDisplayedStatus.PUBLISHED,
    models.CollectiveOfferDisplayedStatus.PUBLISHED: models.CollectiveOfferDisplayedStatus.PREBOOKED,
    models.CollectiveOfferDisplayedStatus.PREBOOKED: models.CollectiveOfferDisplayedStatus.BOOKED,
    models.CollectiveOfferDisplayedStatus.BOOKED: models.CollectiveOfferDisplayedStatus.ENDED,
    models.CollectiveOfferDisplayedStatus.ENDED: models.CollectiveOfferDisplayedStatus.REIMBURSED,
}


def _get_status_date(offer: models.CollectiveOffer, status: serialize.HistoryStatus) -> datetime.datetime | None:
    stock = offer.collectiveStock
    booking = stock.lastBooking if stock is not None else None

    match status:
        case (
            models.CollectiveOfferDisplayedStatus.DRAFT
            | models.CollectiveOfferDisplayedStatus.UNDER_REVIEW
            | serialize.HistoryTransitionalStatus()
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

        case models.CollectiveOfferDisplayedStatus.ARCHIVED:
            return offer.dateArchived

        case models.CollectiveOfferDisplayedStatus.HIDDEN:
            return None

        case _:
            logger.error("Invalid collective offer history status %s for offer %s", status, offer.id)
            return None


def _get_collective_offer_past_history(
    offer: models.CollectiveOffer,
    from_status: models.CollectiveOfferDisplayedStatus | None,
    to_status: models.CollectiveOfferDisplayedStatus | None,
    current_status: serialize.HistoryStatus,
) -> list[serialize.HistoryStep]:
    current_step = serialize.HistoryStep(
        status=current_status, datetime=_get_status_date(offer=offer, status=current_status)
    )
    if from_status is None or to_status is None:
        return [current_step]

    steps = []
    next_status: models.CollectiveOfferDisplayedStatus | None = from_status
    while next_status is not None:
        steps.append(
            serialize.HistoryStep(status=next_status, datetime=_get_status_date(offer=offer, status=next_status))
        )

        if next_status == to_status:
            break

        next_status = NEXT_STATUS_BY_STATUS.get(next_status)

    steps.append(current_step)
    return steps


def _get_collective_offer_future_history(
    from_status: models.CollectiveOfferDisplayedStatus,
) -> list[models.CollectiveOfferDisplayedStatus]:
    steps = []
    next_status = NEXT_STATUS_BY_STATUS.get(from_status)

    while next_status is not None:
        steps.append(next_status)
        next_status = NEXT_STATUS_BY_STATUS.get(next_status)

    return steps


@dataclasses.dataclass
class HistoryStatusData:
    past_from_status: models.CollectiveOfferDisplayedStatus | None
    past_to_status: models.CollectiveOfferDisplayedStatus | None
    current_status: serialize.HistoryStatus
    future_from_status: models.CollectiveOfferDisplayedStatus


def _get_history_status_data(
    offer: models.CollectiveOffer, status: models.CollectiveOfferDisplayedStatus
) -> HistoryStatusData:
    """
    For each status, determine:
    - the first and last of the previous statuses (past_from_status and past_to_status)
    - the current status (current_status)
    - the status from which the future steps are computed (future_from_status)
    """
    stock = offer.collectiveStock
    is_two_days_past_end = stock is not None and stock.is_two_days_past_end()
    booking = stock.lastBooking if stock is not None else None
    was_prebooked = booking is not None
    was_booked = booking is not None and booking.confirmationDate is not None

    past_to_status: models.CollectiveOfferDisplayedStatus
    match status:
        case (
            models.CollectiveOfferDisplayedStatus.DRAFT
            | models.CollectiveOfferDisplayedStatus.UNDER_REVIEW
            | models.CollectiveOfferDisplayedStatus.REJECTED
        ):
            return HistoryStatusData(
                past_from_status=None,
                past_to_status=None,
                current_status=status,
                future_from_status=status,
            )

        case models.CollectiveOfferDisplayedStatus.PUBLISHED:
            return HistoryStatusData(
                past_from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                past_to_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                current_status=serialize.HistoryTransitionalStatus.WAITING_FOR_PREBOOK,
                future_from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
            )

        case models.CollectiveOfferDisplayedStatus.EXPIRED:
            past_to_status = (
                models.CollectiveOfferDisplayedStatus.PREBOOKED
                if was_prebooked
                else models.CollectiveOfferDisplayedStatus.PUBLISHED
            )

            return HistoryStatusData(
                past_from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                past_to_status=past_to_status,
                current_status=models.CollectiveOfferDisplayedStatus.EXPIRED,
                future_from_status=past_to_status,
            )

        case models.CollectiveOfferDisplayedStatus.PREBOOKED:
            return HistoryStatusData(
                past_from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                past_to_status=models.CollectiveOfferDisplayedStatus.PREBOOKED,
                current_status=serialize.HistoryTransitionalStatus.WAITING_FOR_BOOK,
                future_from_status=models.CollectiveOfferDisplayedStatus.PREBOOKED,
            )

        case models.CollectiveOfferDisplayedStatus.BOOKED:
            return HistoryStatusData(
                past_from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                past_to_status=models.CollectiveOfferDisplayedStatus.PREBOOKED,
                current_status=models.CollectiveOfferDisplayedStatus.BOOKED,
                future_from_status=models.CollectiveOfferDisplayedStatus.BOOKED,
            )

        case models.CollectiveOfferDisplayedStatus.ENDED:
            current_status: serialize.HistoryStatus
            if is_two_days_past_end:
                past_to_status = models.CollectiveOfferDisplayedStatus.ENDED
                current_status = serialize.HistoryTransitionalStatus.WAITING_FOR_REIMBURSEMENT
            else:
                past_to_status = models.CollectiveOfferDisplayedStatus.BOOKED
                current_status = models.CollectiveOfferDisplayedStatus.ENDED

            return HistoryStatusData(
                past_from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                past_to_status=past_to_status,
                current_status=current_status,
                future_from_status=models.CollectiveOfferDisplayedStatus.ENDED,
            )

        case models.CollectiveOfferDisplayedStatus.REIMBURSED:
            return HistoryStatusData(
                past_from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                past_to_status=models.CollectiveOfferDisplayedStatus.ENDED,
                current_status=models.CollectiveOfferDisplayedStatus.REIMBURSED,
                future_from_status=models.CollectiveOfferDisplayedStatus.REIMBURSED,
            )

        case models.CollectiveOfferDisplayedStatus.CANCELLED:
            if was_prebooked:
                if was_booked:
                    past_to_status = models.CollectiveOfferDisplayedStatus.BOOKED
                else:
                    past_to_status = models.CollectiveOfferDisplayedStatus.PREBOOKED
            else:
                past_to_status = models.CollectiveOfferDisplayedStatus.PUBLISHED

            return HistoryStatusData(
                past_from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                past_to_status=past_to_status,
                current_status=models.CollectiveOfferDisplayedStatus.CANCELLED,
                future_from_status=models.CollectiveOfferDisplayedStatus.CANCELLED,
            )

        case _:
            raise ValueError(f"Unexpected status {status}")


def get_collective_offer_history(offer: models.CollectiveOffer) -> serialize.CollectiveOfferHistory:
    status = offer.displayedStatus

    if status in {models.CollectiveOfferDisplayedStatus.ARCHIVED, models.CollectiveOfferDisplayedStatus.HIDDEN}:
        # get the status when the offer is not archived / hidden and compute the history up to this status
        base_status = offer.get_displayed_status(with_archived=False, with_hidden=False)
        base_status_data = _get_history_status_data(offer=offer, status=base_status)
        past_history = _get_collective_offer_past_history(
            offer=offer,
            from_status=base_status_data.past_from_status,
            to_status=base_status_data.past_to_status,
            current_status=base_status_data.current_status,
        )

        # dot not include the step preceding archived / hidden if it is a transitional status
        if base_status_data.current_status in set(serialize.HistoryTransitionalStatus):
            past_history.pop()

        # add the archived / hidden step
        past_history.append(serialize.HistoryStep(status=status, datetime=_get_status_date(offer, status)))

        return serialize.CollectiveOfferHistory(past=past_history, future=[])

    status_data = _get_history_status_data(offer=offer, status=status)
    return serialize.CollectiveOfferHistory(
        past=_get_collective_offer_past_history(
            offer=offer,
            from_status=status_data.past_from_status,
            to_status=status_data.past_to_status,
            current_status=status_data.current_status,
        ),
        future=_get_collective_offer_future_history(from_status=status_data.future_from_status),
    )
