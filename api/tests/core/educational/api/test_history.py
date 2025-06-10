import pytest

from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.educational.api import history as api


pytestmark = pytest.mark.usefixtures("db_session")

PAST = api.CollectiveOfferHistoryStepStatus.PAST
CURRENT = api.CollectiveOfferHistoryStepStatus.CURRENT
FUTURE = api.CollectiveOfferHistoryStepStatus.FUTURE


class HistoryTest:
    def test_under_review(self):
        offer = factories.UnderReviewCollectiveOfferFactory()
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.UNDER_REVIEW, step_status=CURRENT, datetime=None
            ),
            *(
                api.CollectiveOfferHistoryStep(offer_status=status, step_status=FUTURE, datetime=None)
                for status in (
                    models.CollectiveOfferDisplayedStatus.PUBLISHED,
                    models.CollectiveOfferDisplayedStatus.PREBOOKED,
                    models.CollectiveOfferDisplayedStatus.BOOKED,
                    models.CollectiveOfferDisplayedStatus.ENDED,
                    models.CollectiveOfferDisplayedStatus.REIMBURSED,
                )
            ),
        ]

    def test_published(self):
        offer = factories.PublishedCollectiveOfferFactory()
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                step_status=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=api.HistoryTransitionalStatus.WAITING_FOR_PREBOOK,
                step_status=CURRENT,
                datetime=None,
            ),
            *(
                api.CollectiveOfferHistoryStep(offer_status=status, step_status=FUTURE, datetime=None)
                for status in (
                    models.CollectiveOfferDisplayedStatus.PREBOOKED,
                    models.CollectiveOfferDisplayedStatus.BOOKED,
                    models.CollectiveOfferDisplayedStatus.ENDED,
                    models.CollectiveOfferDisplayedStatus.REIMBURSED,
                )
            ),
        ]

    def test_prebooked(self):
        offer = factories.PrebookedCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                step_status=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.PREBOOKED,
                step_status=PAST,
                datetime=booking.dateCreated,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=api.HistoryTransitionalStatus.WAITING_FOR_BOOK,
                step_status=CURRENT,
                datetime=None,
            ),
            *(
                api.CollectiveOfferHistoryStep(offer_status=status, step_status=FUTURE, datetime=None)
                for status in (
                    models.CollectiveOfferDisplayedStatus.BOOKED,
                    models.CollectiveOfferDisplayedStatus.ENDED,
                    models.CollectiveOfferDisplayedStatus.REIMBURSED,
                )
            ),
        ]

    def test_booked(self):
        offer = factories.BookedCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                step_status=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.PREBOOKED,
                step_status=PAST,
                datetime=booking.dateCreated,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.BOOKED,
                step_status=CURRENT,
                datetime=booking.confirmationDate,
            ),
            *(
                api.CollectiveOfferHistoryStep(offer_status=status, step_status=FUTURE, datetime=None)
                for status in (
                    models.CollectiveOfferDisplayedStatus.ENDED,
                    models.CollectiveOfferDisplayedStatus.REIMBURSED,
                )
            ),
        ]

    def test_ended_less_than_two_days_ago(self):
        offer = factories.EndedCollectiveOfferFactory(booking_is_confirmed=True)
        [booking] = offer.collectiveStock.collectiveBookings
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                step_status=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.PREBOOKED,
                step_status=PAST,
                datetime=booking.dateCreated,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.BOOKED,
                step_status=PAST,
                datetime=booking.confirmationDate,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.ENDED,
                step_status=CURRENT,
                datetime=offer.collectiveStock.endDatetime,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.REIMBURSED, step_status=FUTURE, datetime=None
            ),
        ]

    def test_ended_more_than_two_days_ago(self):
        offer = factories.EndedCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                step_status=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.PREBOOKED,
                step_status=PAST,
                datetime=booking.dateCreated,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.BOOKED,
                step_status=PAST,
                datetime=booking.confirmationDate,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.ENDED,
                step_status=PAST,
                datetime=offer.collectiveStock.endDatetime,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=api.HistoryTransitionalStatus.WAITING_FOR_REIMBURSEMENT,
                step_status=CURRENT,
                datetime=None,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.REIMBURSED, step_status=FUTURE, datetime=None
            ),
        ]

    def test_reimbursed(self):
        offer = factories.ReimbursedCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                step_status=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.PREBOOKED,
                step_status=PAST,
                datetime=booking.dateCreated,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.BOOKED,
                step_status=PAST,
                datetime=booking.confirmationDate,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.ENDED,
                step_status=PAST,
                datetime=offer.collectiveStock.endDatetime,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.REIMBURSED,
                step_status=CURRENT,
                datetime=booking.reimbursementDate,
            ),
        ]


class HistoryExpiredTest:
    def test_expired_published(self):
        offer = factories.ExpiredWithoutBookingCollectiveOfferFactory()
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                step_status=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.EXPIRED,
                step_status=CURRENT,
                datetime=offer.collectiveStock.bookingLimitDatetime,
            ),
            *(
                api.CollectiveOfferHistoryStep(offer_status=status, step_status=FUTURE, datetime=None)
                for status in (
                    models.CollectiveOfferDisplayedStatus.PREBOOKED,
                    models.CollectiveOfferDisplayedStatus.BOOKED,
                    models.CollectiveOfferDisplayedStatus.ENDED,
                    models.CollectiveOfferDisplayedStatus.REIMBURSED,
                )
            ),
        ]

    def test_expired_prebooked(self):
        offer = factories.ExpiredWithBookingCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                step_status=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.PREBOOKED,
                step_status=PAST,
                datetime=booking.dateCreated,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.EXPIRED,
                step_status=CURRENT,
                datetime=offer.collectiveStock.bookingLimitDatetime,
            ),
            *(
                api.CollectiveOfferHistoryStep(offer_status=status, step_status=FUTURE, datetime=None)
                for status in (
                    models.CollectiveOfferDisplayedStatus.BOOKED,
                    models.CollectiveOfferDisplayedStatus.ENDED,
                    models.CollectiveOfferDisplayedStatus.REIMBURSED,
                )
            ),
        ]


class HistoryCancelledTest:
    def test_cancelled_published(self):
        offer = factories.CancelledWithoutBookingCollectiveOfferFactory()
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                step_status=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.CANCELLED,
                step_status=CURRENT,
                datetime=offer.collectiveStock.startDatetime,
            ),
        ]

    def test_cancelled_prebooked(self):
        offer = factories.CancelledWithPendingBookingCollectiveOfferFactory()
        [booking] = offer.collectiveStock.collectiveBookings
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                step_status=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.PREBOOKED,
                step_status=PAST,
                datetime=booking.dateCreated,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.CANCELLED,
                step_status=CURRENT,
                datetime=booking.cancellationDate,
            ),
        ]

    def test_cancelled_booked(self):
        offer = factories.CancelledWithBookingCollectiveOfferFactory()
        history = api.get_collective_offer_history(offer)
        [booking] = offer.collectiveStock.collectiveBookings

        assert history == [
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                step_status=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.PREBOOKED,
                step_status=PAST,
                datetime=booking.dateCreated,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.BOOKED,
                step_status=PAST,
                datetime=booking.confirmationDate,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.CANCELLED,
                step_status=CURRENT,
                datetime=booking.cancellationDate,
            ),
        ]


class HistoryHiddenTest:
    # TODO: for now it is possible to have a HIDDEN offer, with the public api only
    # once the new statuses are applied to the public api, there should be no HIDDEN offer
    def test_published_hidden(self):
        offer = factories.HiddenCollectiveOfferFactory()
        history = api.get_collective_offer_history(offer)

        assert history == [
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.PUBLISHED,
                step_status=PAST,
                datetime=offer.lastValidationDate,
            ),
            api.CollectiveOfferHistoryStep(
                offer_status=models.CollectiveOfferDisplayedStatus.HIDDEN,
                step_status=CURRENT,
                datetime=None,
            ),
        ]
