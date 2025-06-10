import datetime

import pytest

from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.educational.api import history as api


pytestmark = pytest.mark.usefixtures("db_session")

PAST = api.HistoryTime.PAST
CURRENT = api.HistoryTime.CURRENT
FUTURE = api.HistoryTime.FUTURE

OfferStatus = models.CollectiveOfferDisplayedStatus


class HistoryTest:
    def test_under_review(self):
        offer = factories.UnderReviewCollectiveOfferFactory()
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.HistoryStep(status=OfferStatus.UNDER_REVIEW, time=CURRENT, datetime=None),
            *(
                api.HistoryStep(status=status, time=FUTURE, datetime=None)
                for status in (
                    OfferStatus.PUBLISHED,
                    OfferStatus.PREBOOKED,
                    OfferStatus.BOOKED,
                    OfferStatus.ENDED,
                    OfferStatus.REIMBURSED,
                )
            ),
        ]

    def test_published(self):
        offer = factories.PublishedCollectiveOfferFactory()
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.HistoryStep(
                status=OfferStatus.PUBLISHED,
                time=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.HistoryStep(
                status=api.HistoryTransitionalStatus.WAITING_FOR_PREBOOK,
                time=CURRENT,
                datetime=None,
            ),
            *(
                api.HistoryStep(status=status, time=FUTURE, datetime=None)
                for status in (
                    OfferStatus.PREBOOKED,
                    OfferStatus.BOOKED,
                    OfferStatus.ENDED,
                    OfferStatus.REIMBURSED,
                )
            ),
        ]

    def test_prebooked(self):
        offer = factories.PrebookedCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.HistoryStep(
                status=OfferStatus.PUBLISHED,
                time=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.PREBOOKED,
                time=PAST,
                datetime=booking.dateCreated,
            ),
            api.HistoryStep(
                status=api.HistoryTransitionalStatus.WAITING_FOR_BOOK,
                time=CURRENT,
                datetime=None,
            ),
            *(
                api.HistoryStep(status=status, time=FUTURE, datetime=None)
                for status in (
                    OfferStatus.BOOKED,
                    OfferStatus.ENDED,
                    OfferStatus.REIMBURSED,
                )
            ),
        ]

    def test_booked(self):
        offer = factories.BookedCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.HistoryStep(
                status=OfferStatus.PUBLISHED,
                time=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.PREBOOKED,
                time=PAST,
                datetime=booking.dateCreated,
            ),
            api.HistoryStep(
                status=OfferStatus.BOOKED,
                time=CURRENT,
                datetime=booking.confirmationDate,
            ),
            *(
                api.HistoryStep(status=status, time=FUTURE, datetime=None)
                for status in (
                    OfferStatus.ENDED,
                    OfferStatus.REIMBURSED,
                )
            ),
        ]

    def test_ended_less_than_two_days_ago(self):
        offer = factories.EndedCollectiveOfferFactory(booking_is_confirmed=True)
        [booking] = offer.collectiveStock.collectiveBookings
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.HistoryStep(
                status=OfferStatus.PUBLISHED,
                time=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.PREBOOKED,
                time=PAST,
                datetime=booking.dateCreated,
            ),
            api.HistoryStep(
                status=OfferStatus.BOOKED,
                time=PAST,
                datetime=booking.confirmationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.ENDED,
                time=CURRENT,
                datetime=offer.collectiveStock.endDatetime,
            ),
            api.HistoryStep(status=OfferStatus.REIMBURSED, time=FUTURE, datetime=None),
        ]

    def test_ended_more_than_two_days_ago(self):
        offer = factories.EndedCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.HistoryStep(
                status=OfferStatus.PUBLISHED,
                time=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.PREBOOKED,
                time=PAST,
                datetime=booking.dateCreated,
            ),
            api.HistoryStep(
                status=OfferStatus.BOOKED,
                time=PAST,
                datetime=booking.confirmationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.ENDED,
                time=PAST,
                datetime=offer.collectiveStock.endDatetime,
            ),
            api.HistoryStep(
                status=api.HistoryTransitionalStatus.WAITING_FOR_REIMBURSEMENT,
                time=CURRENT,
                datetime=None,
            ),
            api.HistoryStep(status=OfferStatus.REIMBURSED, time=FUTURE, datetime=None),
        ]

    def test_reimbursed(self):
        offer = factories.ReimbursedCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.HistoryStep(
                status=OfferStatus.PUBLISHED,
                time=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.PREBOOKED,
                time=PAST,
                datetime=booking.dateCreated,
            ),
            api.HistoryStep(
                status=OfferStatus.BOOKED,
                time=PAST,
                datetime=booking.confirmationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.ENDED,
                time=PAST,
                datetime=offer.collectiveStock.endDatetime,
            ),
            api.HistoryStep(
                status=OfferStatus.REIMBURSED,
                time=CURRENT,
                datetime=booking.reimbursementDate,
            ),
        ]


class HistoryExpiredTest:
    def test_expired_published(self):
        offer = factories.ExpiredWithoutBookingCollectiveOfferFactory()
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.HistoryStep(
                status=OfferStatus.PUBLISHED,
                time=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.EXPIRED,
                time=CURRENT,
                datetime=offer.collectiveStock.bookingLimitDatetime,
            ),
            *(
                api.HistoryStep(status=status, time=FUTURE, datetime=None)
                for status in (
                    OfferStatus.PREBOOKED,
                    OfferStatus.BOOKED,
                    OfferStatus.ENDED,
                    OfferStatus.REIMBURSED,
                )
            ),
        ]

    def test_expired_prebooked(self):
        offer = factories.ExpiredWithBookingCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.HistoryStep(
                status=OfferStatus.PUBLISHED,
                time=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.PREBOOKED,
                time=PAST,
                datetime=booking.dateCreated,
            ),
            api.HistoryStep(
                status=OfferStatus.EXPIRED,
                time=CURRENT,
                datetime=offer.collectiveStock.bookingLimitDatetime,
            ),
            *(
                api.HistoryStep(status=status, time=FUTURE, datetime=None)
                for status in (
                    OfferStatus.BOOKED,
                    OfferStatus.ENDED,
                    OfferStatus.REIMBURSED,
                )
            ),
        ]


class HistoryCancelledTest:
    def test_cancelled_published(self):
        offer = factories.CancelledWithoutBookingCollectiveOfferFactory()
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.HistoryStep(
                status=OfferStatus.PUBLISHED,
                time=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.CANCELLED,
                time=CURRENT,
                datetime=offer.collectiveStock.startDatetime,
            ),
        ]

    def test_cancelled_prebooked(self):
        offer = factories.CancelledWithPendingBookingCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.HistoryStep(
                status=OfferStatus.PUBLISHED,
                time=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.PREBOOKED,
                time=PAST,
                datetime=booking.dateCreated,
            ),
            api.HistoryStep(
                status=OfferStatus.CANCELLED,
                time=CURRENT,
                datetime=booking.cancellationDate,
            ),
        ]

    def test_cancelled_booked(self):
        offer = factories.CancelledWithBookingCollectiveOfferFactory()
        history = api.get_collective_offer_history(offer)
        [booking] = offer.collectiveStock.collectiveBookings

        assert history == [
            api.HistoryStep(
                status=OfferStatus.PUBLISHED,
                time=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.PREBOOKED,
                time=PAST,
                datetime=booking.dateCreated,
            ),
            api.HistoryStep(
                status=OfferStatus.BOOKED,
                time=PAST,
                datetime=booking.confirmationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.CANCELLED,
                time=CURRENT,
                datetime=booking.cancellationDate,
            ),
        ]


def _archive_offer(offer: models.CollectiveOffer):
    offer.isActive = False
    offer.dateArchived = datetime.datetime.utcnow()


class HistoryArchivedTest:
    def test_draft_archived(self):
        offer = factories.DraftCollectiveOfferFactory()
        _archive_offer(offer)
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.HistoryStep(
                status=OfferStatus.DRAFT,
                time=PAST,
                datetime=None,
            ),
            api.HistoryStep(
                status=OfferStatus.ARCHIVED,
                time=CURRENT,
                datetime=offer.dateArchived,
            ),
        ]

    def test_rejected_archived(self):
        offer = factories.RejectedCollectiveOfferFactory()
        _archive_offer(offer)
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.HistoryStep(
                status=OfferStatus.REJECTED,
                time=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.ARCHIVED,
                time=CURRENT,
                datetime=offer.dateArchived,
            ),
        ]

    def test_published_archived(self):
        offer = factories.PublishedCollectiveOfferFactory()
        _archive_offer(offer)
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.HistoryStep(
                status=OfferStatus.PUBLISHED,
                time=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.ARCHIVED,
                time=CURRENT,
                datetime=offer.dateArchived,
            ),
        ]

    def test_reimbursed_archived(self):
        offer = factories.ReimbursedCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        _archive_offer(offer)
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.HistoryStep(
                status=OfferStatus.PUBLISHED,
                time=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.PREBOOKED,
                time=PAST,
                datetime=booking.dateCreated,
            ),
            api.HistoryStep(
                status=OfferStatus.BOOKED,
                time=PAST,
                datetime=booking.confirmationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.ENDED,
                time=PAST,
                datetime=offer.collectiveStock.endDatetime,
            ),
            api.HistoryStep(
                status=OfferStatus.REIMBURSED,
                time=PAST,
                datetime=booking.reimbursementDate,
            ),
            api.HistoryStep(
                status=OfferStatus.ARCHIVED,
                time=CURRENT,
                datetime=offer.dateArchived,
            ),
        ]

    def test_expired_archived(self):
        offer = factories.ExpiredWithoutBookingCollectiveOfferFactory()
        _archive_offer(offer)
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.HistoryStep(
                status=OfferStatus.PUBLISHED,
                time=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.EXPIRED,
                time=PAST,
                datetime=offer.collectiveStock.bookingLimitDatetime,
            ),
            api.HistoryStep(
                status=OfferStatus.ARCHIVED,
                time=CURRENT,
                datetime=offer.dateArchived,
            ),
        ]

    def test_cancelled_archived(self):
        offer = factories.CancelledWithPendingBookingCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        _archive_offer(offer)
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.HistoryStep(
                status=OfferStatus.PUBLISHED,
                time=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.PREBOOKED,
                time=PAST,
                datetime=booking.dateCreated,
            ),
            api.HistoryStep(
                status=OfferStatus.CANCELLED,
                time=PAST,
                datetime=booking.cancellationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.ARCHIVED,
                time=CURRENT,
                datetime=offer.dateArchived,
            ),
        ]


class HistoryHiddenTest:
    # TODO: for now it is possible to have a HIDDEN offer, with the public api only
    # once the new statuses are applied to the public api, there should be no HIDDEN offer
    def test_published_hidden(self):
        offer = factories.HiddenCollectiveOfferFactory()
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.HistoryStep(
                status=OfferStatus.PUBLISHED,
                time=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.HistoryStep(
                status=OfferStatus.HIDDEN,
                time=CURRENT,
                datetime=None,
            ),
        ]
