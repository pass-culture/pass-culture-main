import datetime
import logging
import typing

from pcapi.core.educational import models
from pcapi.routes.serialization import BaseModel
from pcapi.utils.date import format_into_utc_date


logger = logging.getLogger(__name__)


class HistoryStep(BaseModel):
    status: models.CollectiveOfferDisplayedStatus
    datetime: datetime.datetime | None


class CollectiveOfferHistory(BaseModel):
    past: list[HistoryStep]
    future: list[models.CollectiveOfferDisplayedStatus]

    class Config:
        json_encoders = {datetime: format_into_utc_date}
        use_enum_values = True


NEXT_STATUS_BY_STATUS: typing.Final[
    dict[models.CollectiveOfferDisplayedStatus, models.CollectiveOfferDisplayedStatus]
] = {
    models.CollectiveOfferDisplayedStatus.DRAFT: models.CollectiveOfferDisplayedStatus.PUBLISHED,
    models.CollectiveOfferDisplayedStatus.UNDER_REVIEW: models.CollectiveOfferDisplayedStatus.PUBLISHED,
    models.CollectiveOfferDisplayedStatus.PUBLISHED: models.CollectiveOfferDisplayedStatus.PREBOOKED,
    models.CollectiveOfferDisplayedStatus.PREBOOKED: models.CollectiveOfferDisplayedStatus.BOOKED,
    models.CollectiveOfferDisplayedStatus.BOOKED: models.CollectiveOfferDisplayedStatus.ENDED,
    models.CollectiveOfferDisplayedStatus.ENDED: models.CollectiveOfferDisplayedStatus.REIMBURSED,
}


def _get_status_date(
    offer: models.CollectiveOffer, status: models.CollectiveOfferDisplayedStatus
) -> datetime.datetime | None:
    stock = offer.collectiveStock
    booking = stock.lastBooking if stock is not None else None

    match status:
        case (
            models.CollectiveOfferDisplayedStatus.DRAFT
            | models.CollectiveOfferDisplayedStatus.UNDER_REVIEW
            | models.CollectiveOfferDisplayedStatus.HIDDEN
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

        case _:
            logger.error("Invalid collective offer history status %s for offer %s", status, offer.id)
            return None


def _get_past_history(
    offer: models.CollectiveOffer,
    from_status: models.CollectiveOfferDisplayedStatus,
    to_status: models.CollectiveOfferDisplayedStatus,
) -> list[HistoryStep]:
    steps = []
    next_status: models.CollectiveOfferDisplayedStatus | None = from_status
    while next_status is not None:
        steps.append(HistoryStep(status=next_status, datetime=_get_status_date(offer=offer, status=next_status)))

        if next_status == to_status:
            break

        next_status = NEXT_STATUS_BY_STATUS.get(next_status)

    return steps


def _get_future_history(
    from_status: models.CollectiveOfferDisplayedStatus,
) -> list[models.CollectiveOfferDisplayedStatus]:
    steps = []
    next_status = NEXT_STATUS_BY_STATUS.get(from_status)

    while next_status is not None:
        steps.append(next_status)
        next_status = NEXT_STATUS_BY_STATUS.get(next_status)

    return steps


def _get_offer_past_history(
    offer: models.CollectiveOffer, status: models.CollectiveOfferDisplayedStatus
) -> list[HistoryStep]:
    stock = offer.collectiveStock
    booking = stock.lastBooking if stock is not None else None
    was_prebooked = booking is not None
    was_booked = booking is not None and booking.confirmationDate is not None

    past_history: list[HistoryStep]
    match status:
        case (
            models.CollectiveOfferDisplayedStatus.DRAFT
            | models.CollectiveOfferDisplayedStatus.UNDER_REVIEW
            | models.CollectiveOfferDisplayedStatus.REJECTED
            | models.CollectiveOfferDisplayedStatus.PUBLISHED
        ):
            past_history = []

        case models.CollectiveOfferDisplayedStatus.EXPIRED:
            to_status = (
                models.CollectiveOfferDisplayedStatus.PREBOOKED
                if was_prebooked
                else models.CollectiveOfferDisplayedStatus.PUBLISHED
            )

            past_history = _get_past_history(
                offer=offer,
                from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                to_status=to_status,
            )

        case models.CollectiveOfferDisplayedStatus.PREBOOKED:
            past_history = _get_past_history(
                offer=offer,
                from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                to_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
            )

        case models.CollectiveOfferDisplayedStatus.BOOKED:
            past_history = _get_past_history(
                offer=offer,
                from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                to_status=models.CollectiveOfferDisplayedStatus.PREBOOKED,
            )

        case models.CollectiveOfferDisplayedStatus.ENDED:
            past_history = _get_past_history(
                offer=offer,
                from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                to_status=models.CollectiveOfferDisplayedStatus.BOOKED,
            )

        case models.CollectiveOfferDisplayedStatus.REIMBURSED:
            past_history = _get_past_history(
                offer=offer,
                from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                to_status=models.CollectiveOfferDisplayedStatus.ENDED,
            )

        case models.CollectiveOfferDisplayedStatus.CANCELLED:
            if was_prebooked:
                to_status = (
                    models.CollectiveOfferDisplayedStatus.BOOKED
                    if was_booked
                    else models.CollectiveOfferDisplayedStatus.PREBOOKED
                )
            else:
                to_status = models.CollectiveOfferDisplayedStatus.PUBLISHED

            past_history = _get_past_history(
                offer=offer,
                from_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                to_status=to_status,
            )

        case models.CollectiveOfferDisplayedStatus.ARCHIVED | models.CollectiveOfferDisplayedStatus.HIDDEN:
            # for an archived or hidden offer, compute the history until the status preceding archived or hidden
            base_status, _, _ = offer.get_base_displayed_status()
            past_history = _get_offer_past_history(offer=offer, status=base_status)

        case _:
            raise ValueError(f"Unexpected status {status}")

    past_history.append(HistoryStep(status=status, datetime=_get_status_date(offer=offer, status=status)))

    return past_history


def get_collective_offer_history(offer: models.CollectiveOffer) -> CollectiveOfferHistory:
    status = offer.displayedStatus

    past_history = _get_offer_past_history(offer=offer, status=status)

    if status == models.CollectiveOfferDisplayedStatus.EXPIRED:
        # in the EXPIRED case, compute the future history starting from the status preceding EXPIRED
        was_prebooked = offer.lastBooking is not None
        from_status = (
            models.CollectiveOfferDisplayedStatus.PREBOOKED
            if was_prebooked
            else models.CollectiveOfferDisplayedStatus.PUBLISHED
        )
    else:
        from_status = status

    return CollectiveOfferHistory(past=past_history, future=_get_future_history(from_status=from_status))
