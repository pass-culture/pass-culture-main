import datetime

import pytest

from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.routes.serialization.collective_history_serialize import CollectiveOfferHistory
from pcapi.routes.serialization.collective_history_serialize import HistoryStep
from pcapi.routes.serialization.collective_history_serialize import get_collective_offer_history


pytestmark = pytest.mark.usefixtures("db_session")


OfferStatus = models.CollectiveOfferDisplayedStatus


class HistoryTest:
    def test_under_review(self):
        offer = factories.UnderReviewCollectiveOfferFactory()
        history = get_collective_offer_history(offer)

        assert history == CollectiveOfferHistory(
            past=[HistoryStep(status=OfferStatus.UNDER_REVIEW, datetime=None)],
            future=[
                OfferStatus.PUBLISHED,
                OfferStatus.PREBOOKED,
                OfferStatus.BOOKED,
                OfferStatus.ENDED,
                OfferStatus.REIMBURSED,
            ],
        )

    def test_published(self):
        offer = factories.PublishedCollectiveOfferFactory()
        history = get_collective_offer_history(offer)

        assert history == CollectiveOfferHistory(
            past=[HistoryStep(status=OfferStatus.PUBLISHED, datetime=offer.lastValidationDate)],
            future=[
                OfferStatus.PREBOOKED,
                OfferStatus.BOOKED,
                OfferStatus.ENDED,
                OfferStatus.REIMBURSED,
            ],
        )

    def test_prebooked(self):
        offer = factories.PrebookedCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        history = get_collective_offer_history(offer)

        assert history == CollectiveOfferHistory(
            past=[
                HistoryStep(status=OfferStatus.PUBLISHED, datetime=offer.lastValidationDate),
                HistoryStep(status=OfferStatus.PREBOOKED, datetime=booking.dateCreated),
            ],
            future=[
                OfferStatus.BOOKED,
                OfferStatus.ENDED,
                OfferStatus.REIMBURSED,
            ],
        )

    def test_booked(self):
        offer = factories.BookedCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        history = get_collective_offer_history(offer)

        assert history == CollectiveOfferHistory(
            past=[
                HistoryStep(status=OfferStatus.PUBLISHED, datetime=offer.lastValidationDate),
                HistoryStep(status=OfferStatus.PREBOOKED, datetime=booking.dateCreated),
                HistoryStep(status=OfferStatus.BOOKED, datetime=booking.confirmationDate),
            ],
            future=[
                OfferStatus.ENDED,
                OfferStatus.REIMBURSED,
            ],
        )

    def test_ended(self):
        offer = factories.EndedCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        history = get_collective_offer_history(offer)

        assert history == CollectiveOfferHistory(
            past=[
                HistoryStep(status=OfferStatus.PUBLISHED, datetime=offer.lastValidationDate),
                HistoryStep(status=OfferStatus.PREBOOKED, datetime=booking.dateCreated),
                HistoryStep(status=OfferStatus.BOOKED, datetime=booking.confirmationDate),
                HistoryStep(status=OfferStatus.ENDED, datetime=offer.collectiveStock.endDatetime),
            ],
            future=[OfferStatus.REIMBURSED],
        )

    def test_reimbursed(self):
        offer = factories.ReimbursedCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        history = get_collective_offer_history(offer)

        assert history == CollectiveOfferHistory(
            past=[
                HistoryStep(status=OfferStatus.PUBLISHED, datetime=offer.lastValidationDate),
                HistoryStep(status=OfferStatus.PREBOOKED, datetime=booking.dateCreated),
                HistoryStep(status=OfferStatus.BOOKED, datetime=booking.confirmationDate),
                HistoryStep(status=OfferStatus.ENDED, datetime=offer.collectiveStock.endDatetime),
                HistoryStep(status=OfferStatus.REIMBURSED, datetime=booking.reimbursementDate),
            ],
            future=[],
        )


class HistoryExpiredTest:
    def test_expired_published(self):
        offer = factories.ExpiredWithoutBookingCollectiveOfferFactory()
        history = get_collective_offer_history(offer)

        assert history == CollectiveOfferHistory(
            past=[
                HistoryStep(status=OfferStatus.PUBLISHED, datetime=offer.lastValidationDate),
                HistoryStep(status=OfferStatus.EXPIRED, datetime=offer.collectiveStock.bookingLimitDatetime),
            ],
            future=[
                OfferStatus.PREBOOKED,
                OfferStatus.BOOKED,
                OfferStatus.ENDED,
                OfferStatus.REIMBURSED,
            ],
        )

    def test_expired_prebooked(self):
        offer = factories.ExpiredWithBookingCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        history = get_collective_offer_history(offer)

        assert history == CollectiveOfferHistory(
            past=[
                HistoryStep(status=OfferStatus.PUBLISHED, datetime=offer.lastValidationDate),
                HistoryStep(status=OfferStatus.PREBOOKED, datetime=booking.dateCreated),
                HistoryStep(status=OfferStatus.EXPIRED, datetime=offer.collectiveStock.bookingLimitDatetime),
            ],
            future=[
                OfferStatus.BOOKED,
                OfferStatus.ENDED,
                OfferStatus.REIMBURSED,
            ],
        )


class HistoryCancelledTest:
    def test_cancelled_published(self):
        offer = factories.CancelledWithoutBookingCollectiveOfferFactory()
        history = get_collective_offer_history(offer)

        assert history == CollectiveOfferHistory(
            past=[
                HistoryStep(status=OfferStatus.PUBLISHED, datetime=offer.lastValidationDate),
                HistoryStep(status=OfferStatus.CANCELLED, datetime=offer.collectiveStock.startDatetime),
            ],
            future=[],
        )

    def test_cancelled_prebooked(self):
        offer = factories.CancelledWithPendingBookingCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        history = get_collective_offer_history(offer)

        assert history == CollectiveOfferHistory(
            past=[
                HistoryStep(status=OfferStatus.PUBLISHED, datetime=offer.lastValidationDate),
                HistoryStep(status=OfferStatus.PREBOOKED, datetime=booking.dateCreated),
                HistoryStep(status=OfferStatus.CANCELLED, datetime=booking.cancellationDate),
            ],
            future=[],
        )

    def test_cancelled_booked(self):
        offer = factories.CancelledWithBookingCollectiveOfferFactory()
        history = get_collective_offer_history(offer)
        [booking] = offer.collectiveStock.collectiveBookings

        assert history == CollectiveOfferHistory(
            past=[
                HistoryStep(status=OfferStatus.PUBLISHED, datetime=offer.lastValidationDate),
                HistoryStep(status=OfferStatus.PREBOOKED, datetime=booking.dateCreated),
                HistoryStep(status=OfferStatus.BOOKED, datetime=booking.confirmationDate),
                HistoryStep(status=OfferStatus.CANCELLED, datetime=booking.cancellationDate),
            ],
            future=[],
        )


def _archive_offer(offer: models.CollectiveOffer):
    offer.publicationDatetime = None
    offer.dateArchived = datetime.datetime.utcnow()


class HistoryArchivedTest:
    def test_draft_archived(self):
        offer = factories.DraftCollectiveOfferFactory()
        _archive_offer(offer)
        history = get_collective_offer_history(offer)

        assert history == CollectiveOfferHistory(
            past=[
                HistoryStep(status=OfferStatus.DRAFT, datetime=None),
                HistoryStep(status=OfferStatus.ARCHIVED, datetime=offer.dateArchived),
            ],
            future=[],
        )

    def test_rejected_archived(self):
        offer = factories.RejectedCollectiveOfferFactory()
        _archive_offer(offer)
        history = get_collective_offer_history(offer)

        assert history == CollectiveOfferHistory(
            past=[
                HistoryStep(status=OfferStatus.REJECTED, datetime=offer.lastValidationDate),
                HistoryStep(status=OfferStatus.ARCHIVED, datetime=offer.dateArchived),
            ],
            future=[],
        )

    def test_published_archived(self):
        offer = factories.PublishedCollectiveOfferFactory()
        _archive_offer(offer)
        history = get_collective_offer_history(offer)

        assert history == CollectiveOfferHistory(
            past=[
                HistoryStep(status=OfferStatus.PUBLISHED, datetime=offer.lastValidationDate),
                HistoryStep(status=OfferStatus.ARCHIVED, datetime=offer.dateArchived),
            ],
            future=[],
        )

    def test_reimbursed_archived(self):
        offer = factories.ReimbursedCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        _archive_offer(offer)
        history = get_collective_offer_history(offer)

        assert history == CollectiveOfferHistory(
            past=[
                HistoryStep(status=OfferStatus.PUBLISHED, datetime=offer.lastValidationDate),
                HistoryStep(status=OfferStatus.PREBOOKED, datetime=booking.dateCreated),
                HistoryStep(status=OfferStatus.BOOKED, datetime=booking.confirmationDate),
                HistoryStep(status=OfferStatus.ENDED, datetime=offer.collectiveStock.endDatetime),
                HistoryStep(status=OfferStatus.REIMBURSED, datetime=booking.reimbursementDate),
                HistoryStep(status=OfferStatus.ARCHIVED, datetime=offer.dateArchived),
            ],
            future=[],
        )

    def test_expired_archived(self):
        offer = factories.ExpiredWithoutBookingCollectiveOfferFactory()
        _archive_offer(offer)
        history = get_collective_offer_history(offer)

        assert history == CollectiveOfferHistory(
            past=[
                HistoryStep(status=OfferStatus.PUBLISHED, datetime=offer.lastValidationDate),
                HistoryStep(status=OfferStatus.EXPIRED, datetime=offer.collectiveStock.bookingLimitDatetime),
                HistoryStep(status=OfferStatus.ARCHIVED, datetime=offer.dateArchived),
            ],
            future=[],
        )

    def test_cancelled_archived(self):
        offer = factories.CancelledWithPendingBookingCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        _archive_offer(offer)
        history = get_collective_offer_history(offer)

        assert history == CollectiveOfferHistory(
            past=[
                HistoryStep(status=OfferStatus.PUBLISHED, datetime=offer.lastValidationDate),
                HistoryStep(status=OfferStatus.PREBOOKED, datetime=booking.dateCreated),
                HistoryStep(status=OfferStatus.CANCELLED, datetime=booking.cancellationDate),
                HistoryStep(status=OfferStatus.ARCHIVED, datetime=offer.dateArchived),
            ],
            future=[],
        )


class HistoryHiddenTest:
    # TODO: for now it is possible to have a HIDDEN offer, with the public api only
    # once the new statuses are applied to the public api, there should be no HIDDEN offer
    def test_published_hidden(self):
        offer = factories.HiddenCollectiveOfferFactory()
        history = get_collective_offer_history(offer)

        assert history == CollectiveOfferHistory(
            past=[
                HistoryStep(status=OfferStatus.PUBLISHED, datetime=offer.lastValidationDate),
                HistoryStep(status=OfferStatus.HIDDEN, datetime=None),
            ],
            future=[],
        )
