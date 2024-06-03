from datetime import datetime
from datetime import timedelta
from unittest import mock

import pytest

from pcapi.core.bookings import factories as booking_factories
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingCancellationReasons
from pcapi.core.educational.models import CollectiveBookingStatus
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.testing import assert_num_queries
from pcapi.scripts.booking import handle_expired_bookings


pytestmark = pytest.mark.usefixtures("db_session")


class CancelExpiredBookingsTest:
    def test_should_cancel_old_thing_that_can_expire_booking(self, app) -> None:
        now = datetime.utcnow()
        eleven_days_ago = now - timedelta(days=11)
        two_months_ago = now - timedelta(days=60)
        old_book_booking = booking_factories.BookingFactory(
            stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id, dateCreated=eleven_days_ago
        )
        old_dvd_booking = booking_factories.BookingFactory(
            stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id, dateCreated=two_months_ago
        )

        handle_expired_bookings.cancel_expired_individual_bookings()

        assert old_book_booking.status is BookingStatus.CANCELLED
        assert old_book_booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp(), rel=1)
        assert old_book_booking.cancellationReason == BookingCancellationReasons.EXPIRED
        assert old_book_booking.stock.dnBookedQuantity == 0

        assert old_dvd_booking.status is BookingStatus.CANCELLED
        assert old_dvd_booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp(), rel=1)
        assert old_dvd_booking.cancellationReason == BookingCancellationReasons.EXPIRED
        assert old_dvd_booking.stock.dnBookedQuantity == 0

    def should_not_cancel_new_thing_that_can_expire_booking(self, app) -> None:
        book = ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        book_booking = booking_factories.BookingFactory(stock__offer__product=book)

        handle_expired_bookings.cancel_expired_individual_bookings()

        assert book_booking.status is not BookingStatus.CANCELLED
        assert not book_booking.cancellationDate
        assert not book_booking.cancellationReason

    def should_not_cancel_old_event_booking(self, app) -> None:
        two_months_ago = datetime.utcnow() - timedelta(days=60)
        tomorrow = datetime.utcnow() + timedelta(days=1)
        old_concert_booking = booking_factories.BookingFactory(
            dateCreated=two_months_ago,
            stock__beginningDatetime=tomorrow,
            stock__offer__subcategoryId=subcategories.CONCERT.id,
        )

        handle_expired_bookings.cancel_expired_individual_bookings()

        assert old_concert_booking.status is not BookingStatus.CANCELLED
        assert not old_concert_booking.cancellationDate
        assert not old_concert_booking.cancellationReason

    def should_not_cancel_old_thing_that_cannot_expire_booking(self, app) -> None:
        two_months_ago = datetime.utcnow() - timedelta(days=60)
        old_press_subscription_booking = booking_factories.BookingFactory(
            stock__offer__subcategoryId=subcategories.ABO_PRESSE_EN_LIGNE.id, dateCreated=two_months_ago
        )

        handle_expired_bookings.cancel_expired_individual_bookings()

        assert old_press_subscription_booking.status is not BookingStatus.CANCELLED
        assert not old_press_subscription_booking.cancellationDate
        assert not old_press_subscription_booking.cancellationReason

    def should_not_update_cancelled_old_thing_that_can_expire_booking(self, app) -> None:
        book = ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        old_book_booking = booking_factories.CancelledBookingFactory(stock__offer__product=book)
        initial_cancellation_date = old_book_booking.cancellationDate

        handle_expired_bookings.cancel_expired_individual_bookings()

        assert old_book_booking.status is BookingStatus.CANCELLED
        assert old_book_booking.cancellationDate == initial_cancellation_date
        assert old_book_booking.cancellationReason == BookingCancellationReasons.BENEFICIARY

    def should_only_cancel_old_thing_that_can_expire_bookings_before_start_date(self, app) -> None:
        now = datetime.utcnow()
        two_months_ago = now - timedelta(days=60)
        old_guitar_booking = booking_factories.BookingFactory(
            stock__offer__subcategoryId=subcategories.ACHAT_INSTRUMENT.id, dateCreated=two_months_ago
        )
        old_disc_booking = booking_factories.BookingFactory(
            stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id, dateCreated=two_months_ago
        )
        old_vod_booking = booking_factories.BookingFactory(
            stock__offer__subcategoryId=subcategories.VOD.id, dateCreated=two_months_ago
        )

        handle_expired_bookings.cancel_expired_individual_bookings()

        assert old_guitar_booking.status is BookingStatus.CANCELLED
        assert old_guitar_booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp(), rel=1)
        assert old_guitar_booking.cancellationReason == BookingCancellationReasons.EXPIRED

        assert old_disc_booking.status is BookingStatus.CANCELLED
        assert old_disc_booking.cancellationDate.timestamp() == pytest.approx(datetime.utcnow().timestamp(), rel=1)
        assert old_disc_booking.cancellationReason == BookingCancellationReasons.EXPIRED

        assert old_vod_booking.status is not BookingStatus.CANCELLED
        assert not old_vod_booking.cancellationDate
        assert not old_vod_booking.cancellationReason

    def test_handle_expired_bookings_should_cancel_expired_individual_bookings(self, app) -> None:
        # Given
        now = datetime.utcnow()
        two_months_ago = now - timedelta(days=60)

        dvd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id)
        expired_individual_booking = booking_factories.BookingFactory(
            stock__offer__product=dvd, dateCreated=two_months_ago
        )

        book = ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        book_individual_recent_booking = booking_factories.BookingFactory(stock__offer__product=book)

        # When
        handle_expired_bookings.handle_expired_bookings()

        # Then
        assert expired_individual_booking.status == BookingStatus.CANCELLED
        assert book_individual_recent_booking.status != BookingStatus.CANCELLED

    def test_queries_performance_individual_bookings(self, app) -> None:
        now = datetime.utcnow()
        two_months_ago = now - timedelta(days=60)
        book = ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        booking_factories.BookingFactory.create_batch(size=10, stock__offer__product=book, dateCreated=two_months_ago)
        n_queries = 1  # select initial booking ids
        n_queries += 4 * (1 + 1 + 1)  # update booking  # select booking stockId  # update stock dnBookedQuantity

        with assert_num_queries(n_queries):
            handle_expired_bookings.cancel_expired_individual_bookings(batch_size=3)


class CancelExpiredCollectiveBookingsTest:
    def test_should_cancel_pending_dated_collective_booking_when_confirmation_limit_date_has_passed(self, app) -> None:
        # Given
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        expired_pending_collective_booking: CollectiveBooking = educational_factories.PendingCollectiveBookingFactory(
            confirmationLimitDate=yesterday
        )

        # When
        handle_expired_bookings.cancel_expired_collective_bookings()

        # Then
        assert expired_pending_collective_booking.status == CollectiveBookingStatus.CANCELLED
        assert expired_pending_collective_booking.cancellationDate.timestamp() == pytest.approx(
            datetime.utcnow().timestamp(), rel=1
        )
        assert expired_pending_collective_booking.cancellationReason == CollectiveBookingCancellationReasons.EXPIRED

    def test_should_not_cancel_confirmed_dated_collective_booking_when_confirmation_limit_date_has_passed(
        self, app
    ) -> None:
        # Given
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        confirmed_collective_booking: CollectiveBooking = educational_factories.CollectiveBookingFactory(
            confirmationLimitDate=yesterday
        )

        # When
        handle_expired_bookings.cancel_expired_collective_bookings()

        # Then
        assert confirmed_collective_booking.status == CollectiveBookingStatus.CONFIRMED

    def test_should_not_cancel_pending_dated_collective_booking_when_confirmation_limit_date_has_not_passed(
        self, app
    ) -> None:
        # Given
        now = datetime.utcnow()
        tomorrow = now + timedelta(days=1)
        pending_collective_booking: CollectiveBooking = educational_factories.PendingCollectiveBookingFactory(
            confirmationLimitDate=tomorrow
        )

        # When
        handle_expired_bookings.cancel_expired_collective_bookings()

        # Then
        assert pending_collective_booking.status == CollectiveBookingStatus.PENDING

    def test_handle_expired_bookings_should_cancel_expired_collective_bookings(self, app) -> None:
        # Given
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        expired_pending_collective_booking: CollectiveBooking = educational_factories.PendingCollectiveBookingFactory(
            confirmationLimitDate=yesterday
        )
        non_expired_pending_collective_booking: CollectiveBooking = (
            educational_factories.PendingCollectiveBookingFactory(confirmationLimitDate=tomorrow)
        )

        # When
        handle_expired_bookings.handle_expired_bookings()

        # Then
        assert expired_pending_collective_booking.status == CollectiveBookingStatus.CANCELLED
        assert non_expired_pending_collective_booking.status == CollectiveBookingStatus.PENDING

    def test_queries_performance_collective_bookings(self, app) -> None:
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        educational_factories.PendingCollectiveBookingFactory.create_batch(size=10, confirmationLimitDate=yesterday)
        n_queries = +1 + 4 * (1)  # select collective_booking ids  # update collective_booking

        with assert_num_queries(n_queries):
            handle_expired_bookings.cancel_expired_collective_bookings(batch_size=3)


class NotifyUsersOfExpiredBookingsTest:
    def should_notify_of_todays_expired_bookings(self, app) -> None:
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        long_ago = now - timedelta(days=31)
        very_long_ago = now - timedelta(days=32)
        dvd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id)
        expired_today_dvd_booking = booking_factories.CancelledBookingFactory(
            stock__offer__product=dvd,
            dateCreated=long_ago,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )
        cd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id)
        expired_today_cd_booking = booking_factories.CancelledBookingFactory(
            stock__offer__product=cd,
            dateCreated=long_ago,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )
        painting = ProductFactory(subcategoryId=subcategories.OEUVRE_ART.id)
        booking_factories.CancelledBookingFactory(
            stock__offer__product=painting,
            dateCreated=very_long_ago,
            cancellationReason=BookingCancellationReasons.EXPIRED,
            cancellationDate=yesterday,
        )

        handle_expired_bookings.notify_users_of_expired_individual_bookings()

        outbox = mails_testing.outbox
        email_recaps = {
            (outbox[0]["To"], outbox[0]["params"]["BOOKINGS"][0]["offer_name"]),
            (outbox[1]["To"], outbox[1]["params"]["BOOKINGS"][0]["offer_name"]),
        }

        dvd_user_email = expired_today_dvd_booking.user.email
        dvd_offer_name = expired_today_dvd_booking.stock.offer.name

        cd_user_email = expired_today_cd_booking.user.email
        cd_offer_name = expired_today_cd_booking.stock.offer.name

        assert email_recaps == {(dvd_user_email, dvd_offer_name), (cd_user_email, cd_offer_name)}


class NotifyOfferersOfExpiredBookingsTest:
    @mock.patch("pcapi.core.mails.transactional.send_bookings_expiration_to_pro_email")
    def test_should_notify_of_todays_expired_individual_bookings(self, mocked_send_email_recap, app) -> None:
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        long_ago = now - timedelta(days=31)
        very_long_ago = now - timedelta(days=32)
        dvd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id)
        expired_today_dvd_booking = booking_factories.CancelledBookingFactory(
            stock__offer__product=dvd,
            dateCreated=long_ago,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )
        cd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id)
        expired_today_cd_booking = booking_factories.CancelledBookingFactory(
            stock__offer__product=cd,
            dateCreated=long_ago,
            cancellationReason=BookingCancellationReasons.EXPIRED,
        )
        painting = ProductFactory(subcategoryId=subcategories.OEUVRE_ART.id)
        _expired_yesterday_booking = booking_factories.CancelledBookingFactory(
            stock__offer__product=painting,
            dateCreated=very_long_ago,
            cancellationReason=BookingCancellationReasons.EXPIRED,
            cancellationDate=yesterday,
        )

        handle_expired_bookings.notify_offerers_of_expired_individual_bookings()

        assert mocked_send_email_recap.call_count == 2
        assert mocked_send_email_recap.call_args_list[0][0] == (
            expired_today_dvd_booking.offerer,
            [expired_today_dvd_booking],
        )
        assert mocked_send_email_recap.call_args_list[1][0] == (
            expired_today_cd_booking.offerer,
            [expired_today_cd_booking],
        )

    def test_should_notify_of_todays_expired_collective_bookings(self) -> None:
        # Given
        today = datetime.today()
        date_event_1 = today + timedelta(days=6, hours=21, minutes=53)
        date_event_2 = today + timedelta(days=16, hours=5)
        yesterday = today - timedelta(days=1)
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
            endDatetime=date_event_1,
            collectiveOffer__name="Ma première offre expirée",
        )
        first_expired_booking = educational_factories.CancelledCollectiveBookingFactory(
            cancellationReason=CollectiveBookingCancellationReasons.EXPIRED,
            cancellationDate=today,
            collectiveStock=stock_one,
            educationalRedactor=redactor,
            educationalInstitution=institution,
        )

        stock_two = educational_factories.CollectiveStockFactory(
            collectiveOffer__bookingEmails=["new_test@mail.com", "newer_test@mail.com"],
            startDatetime=date_event_2,
            endDatetime=date_event_2,
            collectiveOffer__name="Ma deuxième offre expirée",
        )
        second_expired_booking = educational_factories.CancelledCollectiveBookingFactory(
            cancellationReason=CollectiveBookingCancellationReasons.EXPIRED,
            cancellationDate=today,
            collectiveStock=stock_two,
            educationalRedactor=redactor,
        )
        educational_factories.CancelledCollectiveBookingFactory(
            cancellationDate=yesterday,
            cancellationReason=CollectiveBookingCancellationReasons.EXPIRED,
        )

        # Given
        handle_expired_bookings.notify_offerers_of_expired_collective_bookings()

        # Then
        assert len(mails_testing.outbox) == 2
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.EDUCATIONAL_BOOKING_CANCELLATION.value.__dict__
        assert mails_testing.outbox[0]["To"] == "test@mail.com"
        assert mails_testing.outbox[0]["Bcc"] == "test2@mail.com"

        assert mails_testing.outbox[0]["params"] == {
            "OFFER_NAME": "Ma première offre expirée",
            "EDUCATIONAL_INSTITUTION_NAME": institution.name,
            "VENUE_NAME": stock_one.collectiveOffer.venue.name,
            "EVENT_DATE": date_event_1.strftime("%d/%m/%Y"),
            "EVENT_HOUR": date_event_1.strftime("%H:%M"),
            "REDACTOR_FIRSTNAME": redactor.firstName,
            "REDACTOR_LASTNAME": redactor.lastName,
            "REDACTOR_EMAIL": redactor.email,
            "EDUCATIONAL_INSTITUTION_CITY": institution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": institution.postalCode,
            "COLLECTIVE_CANCELLATION_REASON": CollectiveBookingCancellationReasons.EXPIRED.value,
            "BOOKING_ID": first_expired_booking.id,
        }

        second_educational_institution = second_expired_booking.educationalInstitution
        assert mails_testing.outbox[1]["To"] == "new_test@mail.com"
        assert mails_testing.outbox[1]["Bcc"] == "newer_test@mail.com"
        assert mails_testing.outbox[1]["params"] == {
            "OFFER_NAME": "Ma deuxième offre expirée",
            "EDUCATIONAL_INSTITUTION_NAME": second_educational_institution.name,
            "VENUE_NAME": stock_two.collectiveOffer.venue.name,
            "EVENT_DATE": date_event_2.strftime("%d/%m/%Y"),
            "EVENT_HOUR": date_event_2.strftime("%H:%M"),
            "REDACTOR_FIRSTNAME": redactor.firstName,
            "REDACTOR_LASTNAME": redactor.lastName,
            "REDACTOR_EMAIL": redactor.email,
            "EDUCATIONAL_INSTITUTION_CITY": second_educational_institution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": second_educational_institution.postalCode,
            "COLLECTIVE_CANCELLATION_REASON": CollectiveBookingCancellationReasons.EXPIRED.value,
            "BOOKING_ID": second_expired_booking.id,
        }
