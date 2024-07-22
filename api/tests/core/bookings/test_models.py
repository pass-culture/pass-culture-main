from datetime import datetime
from datetime import timedelta
from decimal import Decimal

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.bookings import factories
from pcapi.core.bookings import models
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
import pcapi.core.users.factories as users_factories
from pcapi.core.users.factories import BeneficiaryGrant18Factory
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository


pytestmark = pytest.mark.usefixtures("db_session")


def test_total_amount():
    booking = factories.BookingFactory(amount=1.2, quantity=2)
    assert booking.total_amount == Decimal("2.4")


def test_reimbursement_rate():
    booking = factories.UsedBookingFactory(amount=12.3, quantity=2)
    finance_factories.PricingFactory(booking=booking, status=finance_models.PricingStatus.INVOICED)

    assert booking.reimbursement_rate == 100.0


def test_save_cancellation_date_postgresql_function():
    # In this test, we manually perform an `INSERT` so that the
    # `save_cancellation_date` PotsgreSQL function is triggered.
    booking = factories.BookingFactory()
    assert booking.cancellationDate is None

    booking.status = BookingStatus.CANCELLED
    db.session.flush()
    db.session.refresh(booking)
    assert booking.cancellationDate is not None

    # `cancellationDate` should not be changed when another attribute
    # is updated.
    previous = booking.cancellationDate
    booking.cancellationReason = "FRAUD"
    db.session.flush()
    db.session.refresh(booking)
    assert booking.cancellationDate == previous

    booking.status = BookingStatus.CONFIRMED
    db.session.flush()
    db.session.refresh(booking)
    assert booking.cancellationDate is None


def test_booking_completed_url_gets_normalized():
    booking = factories.BookingFactory(
        token="ABCDEF",
        user__email="1@example.com",
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


def test_too_many_bookings_postgresql_exception_not_executed():
    booking1 = factories.BookingFactory(stock__quantity=1)
    booking2 = factories.BookingFactory(
        status=models.BookingStatus.USED,
        user=users_factories.BeneficiaryGrant18Factory(),
        offerer=booking1.offerer,
        quantity=1,
        amount=booking1.stock.price,
        token="123456",
    )
    booking2.stock = booking1.stock
    booking2.quantity = 2

    with pytest.raises(ApiErrors) as exc:
        repository.save(booking2)
        assert exc.value.errors["global"] == ["La quantité disponible pour cette offre est atteinte."]

    booking2.quantity = 2
    booking2.status = models.BookingStatus.REIMBURSED
    # → Shouldn't raise an error as the new status is reimbursed and the check shouldn't take place
    repository.save(booking2)
    assert booking2.quantity == 2


@pytest.mark.parametrize(
    "booking_date_created, email_at_booking_created_date",
    [
        (datetime.utcnow() - relativedelta(days=7), "first@example.com"),
        (datetime.utcnow() - relativedelta(days=5), "second@example.fr"),
        (datetime.utcnow() - relativedelta(days=3), "third@example.team"),
        (datetime.utcnow() - relativedelta(days=1), "fourth@example.app"),
    ],
)
def test_email_at_booking_date_with_mail_history(booking_date_created, email_at_booking_created_date):
    user = users_factories.BeneficiaryGrant18Factory(
        dateCreated=datetime.utcnow() - relativedelta(days=8), email="fourth@example.app"
    )
    users_factories.EmailValidationEntryFactory(
        user=user,
        oldUserEmail="first",
        oldDomainEmail="example.com",
        newUserEmail="second",
        newDomainEmail="example.fr",
        creationDate=datetime.utcnow() - relativedelta(days=6),
    )
    users_factories.EmailValidationEntryFactory(
        user=user,
        oldUserEmail="second",
        oldDomainEmail="example.fr",
        newUserEmail="third",
        newDomainEmail="example.team",
        creationDate=datetime.utcnow() - relativedelta(days=4),
    )
    users_factories.EmailValidationEntryFactory(
        user=user,
        oldUserEmail="third",
        oldDomainEmail="example.team",
        newUserEmail="fourth",
        newDomainEmail="example.app",
        creationDate=datetime.utcnow() - relativedelta(days=2),
    )


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
    def test_booking_expiration_date_after_new_rules_start_date(self):
        user = BeneficiaryGrant18Factory()
        book_booking = factories.BookingFactory(
            user=user,
            dateCreated=datetime.utcnow(),
            stock__price=10,
            stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        dvd_booking = factories.BookingFactory(
            user=user,
            dateCreated=datetime.utcnow(),
            stock__price=10,
            stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        digital_book_booking = factories.BookingFactory(
            user=user,
            dateCreated=datetime.utcnow(),
            stock__price=10,
            stock__offer__subcategoryId=subcategories.LIVRE_NUMERIQUE.id,
        )

        assert book_booking.expirationDate.strftime("%d/%m/%Y") == (
            datetime.utcnow() + relativedelta(days=10)
        ).strftime("%d/%m/%Y")
        assert dvd_booking.expirationDate.strftime("%d/%m/%Y") == (datetime.utcnow() + relativedelta(days=30)).strftime(
            "%d/%m/%Y"
        )
        assert not digital_book_booking.expirationDate
