import datetime

import pytest

import pcapi.core.educational.api.booking as educational_booking_api
import pcapi.core.educational.exceptions as educational_exceptions
import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.testing import assert_num_queries
from pcapi.utils import date as date_utils
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.mailing import get_event_datetime


pytestmark = pytest.mark.usefixtures("db_session")


class CancelCollectiveBookingTest:
    def test_can_cancel_before_it_is_used(self):
        booking = educational_factories.CollectiveBookingFactory()

        educational_booking_api.cancel_collective_booking(
            booking,
            educational_models.CollectiveBookingCancellationReasons.OFFERER,
        )
        assert booking.status == educational_models.CollectiveBookingStatus.CANCELLED

    def test_can_cancel_already_used(self):
        finance_event = finance_factories.UsedCollectiveBookingFinanceEventFactory()
        booking = finance_event.collectiveBooking

        educational_booking_api.cancel_collective_booking(
            booking,
            educational_models.CollectiveBookingCancellationReasons.OFFERER,
        )
        assert booking.status == educational_models.CollectiveBookingStatus.CANCELLED
        assert finance_event.status == finance_models.FinanceEventStatus.CANCELLED

    def test_cannot_cancel_already_reimbursed(self):
        finance_event = finance_factories.UsedCollectiveBookingFinanceEventFactory(
            status=finance_models.FinanceEventStatus.PRICED,
            collectiveBooking__status=educational_models.CollectiveBookingStatus.REIMBURSED,
            collectiveBooking__collectiveStock__collectiveOffer__venue__pricing_point="self",
        )
        booking = finance_event.collectiveBooking

        with pytest.raises(educational_exceptions.BookingIsAlreadyRefunded):
            educational_booking_api.cancel_collective_booking(
                booking,
                educational_models.CollectiveBookingCancellationReasons.OFFERER,
            )
        assert booking.status == educational_models.CollectiveBookingStatus.REIMBURSED
        assert finance_event.status == finance_models.FinanceEventStatus.PRICED


class CancelExpiredCollectiveBookingsTest:
    def test_should_cancel_pending_dated_collective_booking_when_confirmation_limit_date_has_passed(self, app) -> None:
        # Given
        now = date_utils.get_naive_utc_now()
        yesterday = now - datetime.timedelta(days=1)
        expired_pending_collective_booking: educational_models.CollectiveBooking = (
            educational_factories.PendingCollectiveBookingFactory(confirmationLimitDate=yesterday)
        )

        # When
        educational_booking_api._cancel_expired_collective_bookings()

        # Then
        assert expired_pending_collective_booking.status == educational_models.CollectiveBookingStatus.CANCELLED
        assert expired_pending_collective_booking.cancellationDate.timestamp() == pytest.approx(
            date_utils.get_naive_utc_now().timestamp(), rel=1
        )
        assert (
            expired_pending_collective_booking.cancellationReason
            == educational_models.CollectiveBookingCancellationReasons.EXPIRED
        )

    def test_should_not_cancel_confirmed_dated_collective_booking_when_confirmation_limit_date_has_passed(
        self, app
    ) -> None:
        # Given
        now = date_utils.get_naive_utc_now()
        yesterday = now - datetime.timedelta(days=1)
        confirmed_collective_booking: educational_models.CollectiveBooking = (
            educational_factories.CollectiveBookingFactory(confirmationLimitDate=yesterday)
        )

        # When
        educational_booking_api._cancel_expired_collective_bookings()

        # Then
        assert confirmed_collective_booking.status == educational_models.CollectiveBookingStatus.CONFIRMED

    def test_should_not_cancel_pending_dated_collective_booking_when_confirmation_limit_date_has_not_passed(
        self, app
    ) -> None:
        # Given
        now = date_utils.get_naive_utc_now()
        tomorrow = now + datetime.timedelta(days=1)
        pending_collective_booking: educational_models.CollectiveBooking = (
            educational_factories.PendingCollectiveBookingFactory(confirmationLimitDate=tomorrow)
        )

        # When
        educational_booking_api._cancel_expired_collective_bookings()

        # Then
        assert pending_collective_booking.status == educational_models.CollectiveBookingStatus.PENDING

    def test_handle_expired_bookings_should_cancel_expired_collective_bookings(self, app) -> None:
        # Given
        now = date_utils.get_naive_utc_now()
        yesterday = now - datetime.timedelta(days=1)
        tomorrow = now + datetime.timedelta(days=1)

        expired_pending_collective_booking: educational_models.CollectiveBooking = (
            educational_factories.PendingCollectiveBookingFactory(confirmationLimitDate=yesterday)
        )
        non_expired_pending_collective_booking: educational_models.CollectiveBooking = (
            educational_factories.PendingCollectiveBookingFactory(confirmationLimitDate=tomorrow)
        )

        # When
        educational_booking_api.handle_expired_collective_bookings()

        # Then
        assert expired_pending_collective_booking.status == educational_models.CollectiveBookingStatus.CANCELLED
        assert non_expired_pending_collective_booking.status == educational_models.CollectiveBookingStatus.PENDING

    def test_queries_performance_collective_bookings(self, app) -> None:
        now = date_utils.get_naive_utc_now()
        yesterday = now - datetime.timedelta(days=1)
        educational_factories.PendingCollectiveBookingFactory.create_batch(size=10, confirmationLimitDate=yesterday)
        n_queries = +1 + 4 * (1)  # select collective_booking ids  # update collective_booking

        with assert_num_queries(n_queries):
            educational_booking_api._cancel_expired_collective_bookings(batch_size=3)


class NotifyOfferersOfExpiredBookingsTest:
    def test_should_notify_of_todays_expired_collective_bookings(self) -> None:
        today = datetime.datetime.today()
        date_event_1 = today + datetime.timedelta(days=6, hours=21, minutes=53)
        date_event_2 = today + datetime.timedelta(days=16, hours=5)
        yesterday = today - datetime.timedelta(days=1)
        redactor = educational_factories.EducationalRedactorFactory(
            civility="M.",
            firstName="Jean",
            lastName="Doudou",
            email="jean.doux@example.com",
        )
        institution = educational_factories.EducationalInstitutionFactory(
            name="Collège Dupont", city="Tourcoing", postalCode=59200
        )
        stock_one = educational_factories.CollectiveStockFactory(
            collectiveOffer__bookingEmails=["test@mail.com", "test2@mail.com"],
            startDatetime=date_event_1,
            collectiveOffer__name="Ma première offre expirée",
        )
        first_expired_booking = educational_factories.CancelledCollectiveBookingFactory(
            cancellationReason=educational_models.CollectiveBookingCancellationReasons.EXPIRED,
            cancellationDate=today,
            collectiveStock=stock_one,
            educationalRedactor=redactor,
            educationalInstitution=institution,
        )

        stock_two = educational_factories.CollectiveStockFactory(
            collectiveOffer__bookingEmails=["new_test@mail.com", "newer_test@mail.com"],
            startDatetime=date_event_2,
            collectiveOffer__name="Ma deuxième offre expirée",
        )
        second_expired_booking = educational_factories.CancelledCollectiveBookingFactory(
            cancellationReason=educational_models.CollectiveBookingCancellationReasons.EXPIRED,
            cancellationDate=today,
            collectiveStock=stock_two,
            educationalRedactor=redactor,
        )
        educational_factories.CancelledCollectiveBookingFactory(
            cancellationDate=yesterday,
            cancellationReason=educational_models.CollectiveBookingCancellationReasons.EXPIRED,
        )

        educational_booking_api._notify_offerers_of_expired_collective_bookings()

        assert len(mails_testing.outbox) == 2
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.EDUCATIONAL_BOOKING_CANCELLATION.value.__dict__
        assert mails_testing.outbox[0]["To"] == "test@mail.com"
        assert mails_testing.outbox[0]["Bcc"] == "test2@mail.com"

        assert mails_testing.outbox[0]["params"] == {
            "OFFER_NAME": "Ma première offre expirée",
            "EDUCATIONAL_INSTITUTION_NAME": institution.name,
            "VENUE_NAME": stock_one.collectiveOffer.venue.name,
            "EVENT_DATE": get_date_formatted_for_email(get_event_datetime(first_expired_booking.collectiveStock)),
            "EVENT_HOUR": get_time_formatted_for_email(get_event_datetime(first_expired_booking.collectiveStock)),
            "REDACTOR_FIRSTNAME": redactor.firstName,
            "REDACTOR_LASTNAME": redactor.lastName,
            "REDACTOR_EMAIL": redactor.email,
            "EDUCATIONAL_INSTITUTION_CITY": institution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": institution.postalCode,
            "COLLECTIVE_CANCELLATION_REASON": educational_models.CollectiveBookingCancellationReasons.EXPIRED.value,
            "BOOKING_ID": first_expired_booking.id,
            "COLLECTIVE_OFFER_ID": stock_one.collectiveOfferId,
            "COLLECTIVE_OFFER_ADDRESS": "À déterminer avec l'enseignant",
        }

        second_educational_institution = second_expired_booking.educationalInstitution
        assert mails_testing.outbox[1]["To"] == "new_test@mail.com"
        assert mails_testing.outbox[1]["Bcc"] == "newer_test@mail.com"
        assert mails_testing.outbox[1]["params"] == {
            "OFFER_NAME": "Ma deuxième offre expirée",
            "EDUCATIONAL_INSTITUTION_NAME": second_educational_institution.name,
            "VENUE_NAME": stock_two.collectiveOffer.venue.name,
            "EVENT_DATE": get_date_formatted_for_email(get_event_datetime(second_expired_booking.collectiveStock)),
            "EVENT_HOUR": get_time_formatted_for_email(get_event_datetime(second_expired_booking.collectiveStock)),
            "REDACTOR_FIRSTNAME": redactor.firstName,
            "REDACTOR_LASTNAME": redactor.lastName,
            "REDACTOR_EMAIL": redactor.email,
            "EDUCATIONAL_INSTITUTION_CITY": second_educational_institution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": second_educational_institution.postalCode,
            "COLLECTIVE_CANCELLATION_REASON": educational_models.CollectiveBookingCancellationReasons.EXPIRED.value,
            "BOOKING_ID": second_expired_booking.id,
            "COLLECTIVE_OFFER_ID": stock_two.collectiveOfferId,
            "COLLECTIVE_OFFER_ADDRESS": "À déterminer avec l'enseignant",
        }
