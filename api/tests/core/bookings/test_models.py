from datetime import datetime
from datetime import timedelta
from decimal import Decimal

from freezegun import freeze_time
import pytest

from pcapi.core.bookings import exceptions
from pcapi.core.bookings import factories
from pcapi.core.bookings import models
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
from pcapi.core.offers.factories import MediationFactory
import pcapi.core.users.factories as users_factories
from pcapi.models import ApiErrors
from pcapi.models import db
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


def test_total_amount():
    booking = factories.BookingFactory(amount=1.2, quantity=2)
    assert booking.total_amount == Decimal("2.4")


def test_save_cancellation_date_postgresql_function():
    # In this test, we manually COMMIT so that save_cancellation_date
    # PotsgreSQL function is triggered.
    booking = factories.BookingFactory()
    assert booking.cancellationDate is None

    booking.isCancelled = True
    db.session.commit()
    assert booking.cancellationDate is not None

    # `cancellationDate` should not be changed when another attribute
    # is updated.
    previous = booking.cancellationDate
    booking.cancellationReason = "FRAUD"
    db.session.commit()
    assert booking.cancellationDate == previous

    booking.isCancelled = False
    db.session.commit()
    assert booking.cancellationDate is None


def test_booking_completed_url_gets_normalized():
    booking = factories.IndividualBookingFactory(
        token="ABCDEF",
        individualBooking__user__email="1@example.com",
        stock__offer__url="example.com?token={token}&email={email}",
    )
    assert booking.completedUrl == "http://example.com?token=ABCDEF&email=1@example.com"


def test_too_many_bookings_postgresql_exception():
    booking1 = factories.BookingFactory(stock__quantity=1)
    with db.session.no_autoflush:
        booking2 = models.Booking()
        booking2.user = users_factories.BeneficiaryGrant18Factory()
        booking2.stock = booking1.stock
        booking2.offerer = booking1.offerer
        booking2.venue = booking1.venue
        booking2.quantity = 1
        booking2.amount = booking1.stock.price
        booking2.token = "123456"
        with pytest.raises(ApiErrors) as exc:
            repository.save(booking2)
        assert exc.value.errors["global"] == ["La quantité disponible pour cette offre est atteinte."]


class BookingThumbUrlTest:
    def test_thumb_url_use_mediation_if_exists(self):
        mediation = MediationFactory(thumbCount=1)
        booking = factories.BookingFactory(
            stock__offer=mediation.offer,
        )
        mediation_id = humanize(mediation.id)
        assert booking.thumbUrl == f"http://localhost/storage/thumbs/mediations/{mediation_id}"

    def test_thumb_url_use_product_if_no_mediation(self):
        booking = factories.BookingFactory(stock__offer__product__thumbCount=1)
        product_id = humanize(booking.stock.offer.product.id)
        assert booking.thumbUrl == f"http://localhost/storage/thumbs/products/{product_id}"

    def test_no_thumb_if_no_mediation_and_product_thumb_count_is_zero(self):
        booking = factories.BookingFactory(stock__offer__product__thumbCount=0)
        assert booking.thumbUrl is None

    def test_no_thumb_if_mediation_thumb_count_is_zero(self):
        mediation = MediationFactory(thumbCount=0)
        booking = factories.BookingFactory(
            stock__offer=mediation.offer,
        )
        assert booking.thumbUrl is None


class BookingQrCodeTest:
    def test_event_return_qr_code_if_event_is_not_expired_nor_cancelled(self):
        booking = factories.BookingFactory(
            stock__offer__product__subcategoryId=subcategories.SEANCE_CINE.id,
        )
        assert isinstance(booking.qrCode, str)

    def test_event_return_none_if_event_is_expired(self):
        booking = factories.BookingFactory(
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
            stock__beginningDatetime=datetime.now() - timedelta(days=1),
        )
        assert booking.qrCode is None

    def test_event_return_none_if_booking_is_cancelled(self):
        booking = factories.CancelledBookingFactory(
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
        )
        assert booking.qrCode is None

    def test_thing_return_qr_code_if_not_used_nor_cancelled(self):
        booking = factories.BookingFactory(
            stock__offer__subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
        )
        assert isinstance(booking.qrCode, str)

    def test_thing_return_none_if_booking_is_used(self):
        booking = factories.UsedBookingFactory(
            stock__offer__subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
        )
        assert booking.qrCode is None

    def test_thing_return_none_if_booking_is_cancelled(self):
        booking = factories.CancelledBookingFactory(
            stock__offer__subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
        )
        assert booking.qrCode is None


class BookingIsConfirmedPropertyTest:
    def test_booking_is_confirmed_when_cancellation_limit_date_is_in_the_past(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = factories.BookingFactory(cancellation_limit_date=yesterday)

        assert booking.isConfirmed is True

    def test_booking_is_not_confirmed_when_cancellation_limit_date_is_in_the_future(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        booking = factories.BookingFactory(cancellation_limit_date=tomorrow)

        assert booking.isConfirmed is False

    def test_booking_is_not_confirmed_when_no_cancellation_limit_date_exists(self):
        booking = factories.BookingFactory()

        assert booking.isConfirmed is False


class BookingIsConfirmedSqlQueryTest:
    def test_booking_is_confirmed_when_cancellation_limit_date_is_in_the_past(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        factories.BookingFactory(cancellation_limit_date=yesterday)

        query_result = Booking.query.filter(Booking.isConfirmed.is_(True)).all()

        assert len(query_result) == 1

    def test_booking_is_not_confirmed_when_cancellation_limit_date_is_in_the_future(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        factories.BookingFactory(cancellation_limit_date=tomorrow)

        query_result = Booking.query.filter(Booking.isConfirmed.is_(False)).all()

        assert len(query_result) == 1

    def test_booking_is_not_confirmed_when_no_cancellation_limit_date_exists(self):
        factories.BookingFactory()

        query_result = Booking.query.filter(Booking.isConfirmed.is_(False)).all()

        assert len(query_result) == 1


class BookingExpirationDateTest:
    @freeze_time("2021-08-05 15:00:00")
    def test_booking_expiration_date_after_new_rules_start_date(self):
        book_booking = factories.BookingFactory(
            dateCreated=datetime.utcnow(), stock__offer__product__subcategoryId=subcategories.LIVRE_PAPIER.id
        )
        dvd_booking = factories.BookingFactory(
            dateCreated=datetime.utcnow(),
            stock__offer__product__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        digital_book_booking = factories.BookingFactory(
            dateCreated=datetime.utcnow(),
            stock__offer__product__subcategoryId=subcategories.LIVRE_NUMERIQUE.id,
        )

        assert book_booking.expirationDate == datetime(2021, 8, 15, 15, 0, 0)
        assert dvd_booking.expirationDate == datetime(2021, 9, 4, 15, 0, 0)
        assert not digital_book_booking.expirationDate


class BookingMarkAsConfirmedTest:
    @freeze_time("2021-08-05 15:00:00")
    def test_confirm_when_confirmation_limit_date_has_not_passed(self) -> None:
        booking: Booking = factories.EducationalBookingFactory(
            educationalBooking__confirmationLimitDate=datetime(2021, 8, 5, 16)
        )

        booking.mark_as_confirmed()
        db.session.flush()

        assert booking.status == BookingStatus.CONFIRMED

    @freeze_time("2021-08-05 15:00:00")
    def test_confirm_when_has_confirmation_limit_date_passed(self) -> None:
        booking: Booking = factories.EducationalBookingFactory(
            educationalBooking__confirmationLimitDate=datetime(2021, 8, 5, 14),
            status=models.BookingStatus.PENDING,
        )

        with pytest.raises(exceptions.ConfirmationLimitDateHasPassed):
            booking.mark_as_confirmed()

        assert booking.status == BookingStatus.PENDING

    def test_when_booking_is_not_educational(self) -> None:
        booking: Booking = factories.IndividualBookingFactory(
            status=models.BookingStatus.PENDING,
        )

        with pytest.raises(exceptions.CannotMarkAsConfirmedIndividualBooking):
            booking.mark_as_confirmed()

        assert booking.status == BookingStatus.PENDING
