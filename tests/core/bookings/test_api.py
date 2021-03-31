from datetime import datetime
from datetime import timedelta
from unittest import mock

from freezegun import freeze_time
import pytest
from sqlalchemy import create_engine
import sqlalchemy.exc
from sqlalchemy.sql import text

from pcapi.core.bookings import api
from pcapi.core.bookings import exceptions
from pcapi.core.bookings import factories
from pcapi.core.bookings import models
from pcapi.core.bookings.models import BookingCancellationReasons
import pcapi.core.mails.testing as mails_testing
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.payments.factories as payments_factories
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
from pcapi.models import api_errors
import pcapi.notifications.push.testing as push_testing
from pcapi.utils.token import random_token

from tests.conftest import clean_database


class BookOfferConcurrencyTest:
    @clean_database
    def test_create_booking(self, app):
        user = users_factories.UserFactory()
        stock = offers_factories.StockFactory(price=10, dnBookedQuantity=5)
        assert models.Booking.query.count() == 0

        # open a second connection on purpose and lock the stock
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        with engine.connect() as connection:
            connection.execute(text("""SELECT * FROM stock WHERE stock.id = :stock_id FOR UPDATE"""), stock_id=stock.id)

            with pytest.raises(sqlalchemy.exc.OperationalError):
                api.book_offer(beneficiary=user, stock_id=stock.id, quantity=1)

        assert models.Booking.query.count() == 0
        assert offers_models.Stock.query.filter_by(id=stock.id, dnBookedQuantity=5).count() == 1

    @clean_database
    def test_cancel_booking(self, app):
        booking = factories.BookingFactory(stock__dnBookedQuantity=1)

        # open a second connection on purpose and lock the stock
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        with engine.connect() as connection:
            connection.execute(
                text("""SELECT * FROM stock WHERE stock.id = :stock_id FOR UPDATE"""), stock_id=booking.stockId
            )

            with pytest.raises(sqlalchemy.exc.OperationalError):
                api.cancel_booking_by_beneficiary(booking.user, booking)

        assert models.Booking.query.filter().count() == 1
        assert models.Booking.query.filter(models.Booking.isCancelled == True).count() == 0

    @clean_database
    def test_cancel_all_bookings_from_stock(self, app):
        stock = offers_factories.StockFactory(dnBookedQuantity=1)
        factories.BookingFactory(stock=stock)
        factories.BookingFactory(stock=stock)
        factories.BookingFactory(stock=stock, isUsed=True)
        factories.BookingFactory(stock=stock, isCancelled=True)

        # open a second connection on purpose and lock the stock
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        with engine.connect() as connection:
            connection.execute(text("""SELECT * FROM stock WHERE stock.id = :stock_id FOR UPDATE"""), stock_id=stock.id)

            with pytest.raises(sqlalchemy.exc.OperationalError):
                api.cancel_bookings_when_offerer_deletes_stock(stock)

        assert models.Booking.query.filter().count() == 4
        assert models.Booking.query.filter(models.Booking.isCancelled == True).count() == 1


@pytest.mark.usefixtures("db_session")
class BookOfferTest:
    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_create_booking(self, mocked_add_offer_id, app):
        user = users_factories.UserFactory()
        stock = offers_factories.StockFactory(price=10, dnBookedQuantity=5)

        booking = api.book_offer(beneficiary=user, stock_id=stock.id, quantity=1)

        assert booking.quantity == 1
        assert booking.amount == 10
        assert booking.stock == stock
        assert len(booking.token) == 6
        assert not booking.isCancelled
        assert not booking.isUsed
        assert booking.confirmationDate is None
        assert stock.dnBookedQuantity == 6

        mocked_add_offer_id.assert_called_once_with(client=app.redis_client, offer_id=stock.offer.id)

        assert len(mails_testing.outbox) == 2
        email_data1 = mails_testing.outbox[0].sent_data
        assert email_data1["MJ-TemplateID"] == 2418750  # to offerer
        email_data2 = mails_testing.outbox[1].sent_data
        assert email_data2["MJ-TemplateID"] == 1163067  # to beneficiary

    def test_create_event_booking(self):
        ten_days_from_now = datetime.utcnow() + timedelta(days=10)
        user = users_factories.UserFactory()
        stock = offers_factories.StockFactory(price=10, beginningDatetime=ten_days_from_now, dnBookedQuantity=5)

        booking = api.book_offer(beneficiary=user, stock_id=stock.id, quantity=1)
        two_days_after_booking = booking.dateCreated + timedelta(days=2)
        assert booking.quantity == 1
        assert booking.amount == 10
        assert booking.stock == stock
        assert stock.dnBookedQuantity == 6
        assert len(booking.token) == 6
        assert not booking.isCancelled
        assert not booking.isUsed
        assert booking.confirmationDate == two_days_after_booking

    @override_features(SYNCHRONIZE_ALGOLIA=False)
    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_do_not_sync_algolia_if_feature_is_disabled(self, mocked_add_offer_id):
        user = users_factories.UserFactory()
        stock = offers_factories.StockFactory()

        api.book_offer(beneficiary=user, stock_id=stock.id, quantity=1)
        mocked_add_offer_id.assert_not_called()

    def test_raise_if_is_admin(self):
        user = users_factories.UserFactory(isAdmin=True)
        stock = offers_factories.StockFactory()

        with pytest.raises(exceptions.UserHasInsufficientFunds):
            api.book_offer(beneficiary=user, stock_id=stock.id, quantity=1)

    def test_raise_if_pro_user(self):
        user = users_factories.UserFactory(isBeneficiary=False, isAdmin=False)
        stock = offers_factories.StockFactory()

        with pytest.raises(exceptions.UserHasInsufficientFunds):
            api.book_offer(beneficiary=user, stock_id=stock.id, quantity=1)

    def test_raise_if_no_more_stock(self):
        booking = factories.BookingFactory(stock__quantity=1)
        with pytest.raises(exceptions.StockIsNotBookable):
            api.book_offer(
                beneficiary=users_factories.UserFactory(),
                stock_id=booking.stock.id,
                quantity=1,
            )

    def test_raise_if_user_has_already_booked(self):
        booking = factories.BookingFactory()
        with pytest.raises(exceptions.OfferIsAlreadyBooked):
            api.book_offer(
                beneficiary=booking.user,
                stock_id=booking.stock.id,
                quantity=1,
            )

    def test_raise_if_user_has_no_more_money(self):
        stock = offers_factories.StockFactory(price=800)
        with pytest.raises(exceptions.UserHasInsufficientFunds):
            api.book_offer(
                beneficiary=users_factories.UserFactory(),
                stock_id=stock.id,
                quantity=1,
            )

    def test_raise_if_invalid_quantity(self):
        with pytest.raises(exceptions.QuantityIsInvalid):
            api.book_offer(
                beneficiary=users_factories.UserFactory(),
                stock_id=offers_factories.StockFactory().id,
                quantity=2,
            )


@pytest.mark.usefixtures("db_session")
class CancelByBeneficiaryTest:
    def test_cancel_booking(self):
        booking = factories.BookingFactory()

        api.cancel_booking_by_beneficiary(booking.user, booking)

        assert booking.isCancelled
        assert booking.cancellationReason == BookingCancellationReasons.BENEFICIARY
        assert len(mails_testing.outbox) == 2
        email_data1 = mails_testing.outbox[0].sent_data
        assert email_data1["Mj-TemplateID"] == 1091464  # to beneficiary
        email_data2 = mails_testing.outbox[1].sent_data
        assert email_data2["MJ-TemplateID"] == 780015  # to offerer

    @override_features(SYNCHRONIZE_ALGOLIA=False)
    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_do_not_sync_algolia_if_feature_is_disabled(self, mocked_add_offer_id):
        booking = factories.BookingFactory()
        api.cancel_booking_by_beneficiary(booking.user, booking)
        mocked_add_offer_id.assert_not_called()

    def test_raise_if_booking_is_already_used(self):
        booking = factories.BookingFactory(isUsed=True)

        with pytest.raises(exceptions.BookingIsAlreadyUsed):
            api.cancel_booking_by_beneficiary(booking.user, booking)
        assert not booking.isCancelled

    def test_raise_if_event_too_close(self):
        event_date_too_close_to_cancel_booking = datetime.now() + timedelta(days=1)
        booking = factories.BookingFactory(
            stock__beginningDatetime=event_date_too_close_to_cancel_booking,
        )
        with pytest.raises(exceptions.CannotCancelConfirmedBooking) as exc:
            api.cancel_booking_by_beneficiary(booking.user, booking)
        assert not booking.isCancelled
        assert not booking.cancellationReason
        assert exc.value.errors["booking"] == [
            "Impossible d'annuler une réservation plus de 48h après l'avoir "
            "réservée et moins de 48h avant le début de l'événement"
        ]

    def test_raise_if_booking_created_too_long_ago_to_cancel_booking(self):
        event_date_far_enough_to_cancel_booking = datetime.now() + timedelta(days=2, minutes=1)
        booking_date_too_long_ago_to_cancel_booking = datetime.utcnow() - timedelta(days=2, minutes=1)
        booking = factories.BookingFactory(
            stock__beginningDatetime=event_date_far_enough_to_cancel_booking,
            dateCreated=booking_date_too_long_ago_to_cancel_booking,
        )
        with pytest.raises(exceptions.CannotCancelConfirmedBooking) as exc:
            api.cancel_booking_by_beneficiary(booking.user, booking)
        assert not booking.isCancelled
        assert not booking.cancellationReason
        assert exc.value.errors["booking"] == [
            "Impossible d'annuler une réservation plus de 48h après l'avoir réservée"
            " et moins de 48h avant le début de l'événement"
        ]

    def test_raise_if_event_too_close_and_booked_long_ago(self):
        booking_date_too_long_ago_to_cancel_booking = datetime.utcnow() - timedelta(days=2, minutes=1)
        event_date_too_close_to_cancel_booking = datetime.now() + timedelta(days=1)
        booking = factories.BookingFactory(
            stock__beginningDatetime=event_date_too_close_to_cancel_booking,
            dateCreated=booking_date_too_long_ago_to_cancel_booking,
        )
        with pytest.raises(exceptions.CannotCancelConfirmedBooking) as exc:
            api.cancel_booking_by_beneficiary(booking.user, booking)
        assert not booking.isCancelled
        assert not booking.cancellationReason
        assert exc.value.errors["booking"] == [
            "Impossible d'annuler une réservation plus de 48h après l'avoir "
            "réservée et moins de 48h avant le début de l'événement"
        ]

    def test_raise_if_trying_to_cancel_someone_else_s_booking(self):
        booking = factories.BookingFactory()
        other_user = users_factories.UserFactory()
        with pytest.raises(exceptions.BookingDoesntExist):
            api.cancel_booking_by_beneficiary(other_user, booking)
        assert not booking.isCancelled
        assert not booking.cancellationReason


@pytest.mark.usefixtures("db_session")
class CancelByOffererTest:
    def test_cancel(self):
        booking = factories.BookingFactory()
        api.cancel_booking_by_offerer(booking)
        assert booking.isCancelled
        assert booking.cancellationReason == BookingCancellationReasons.OFFERER

        assert push_testing.requests == [
            {
                "group_id": "Cancel_booking",
                "message": {
                    "body": f"""Ta commande "{booking.stock.offer.name}" a été annulée par l\'offreur.""",
                    "title": "Commande annulée",
                },
                "user_ids": [booking.userId],
            },
        ]

    def test_raise_if_already_cancelled(self):
        booking = factories.BookingFactory(isCancelled=True, cancellationReason=BookingCancellationReasons.BENEFICIARY)
        with pytest.raises(api_errors.ResourceGoneError):
            api.cancel_booking_by_offerer(booking)
        assert booking.isCancelled
        assert booking.cancellationReason == BookingCancellationReasons.BENEFICIARY

        assert push_testing.requests == []

    def test_raise_if_already_used(self):
        booking = factories.BookingFactory(isUsed=True)
        with pytest.raises(api_errors.ForbiddenError):
            api.cancel_booking_by_offerer(booking)
        assert booking.isUsed
        assert not booking.isCancelled
        assert not booking.cancellationReason

        assert not booking.isCancelled

        assert push_testing.requests == []

    def test_cancel_all_bookings_from_stock(self, app):
        stock = offers_factories.StockFactory(dnBookedQuantity=1)
        booking_1 = factories.BookingFactory(stock=stock)
        booking_2 = factories.BookingFactory(stock=stock)
        used_booking = factories.BookingFactory(stock=stock, isUsed=True)
        cancelled_booking = factories.BookingFactory(
            stock=stock, isCancelled=True, cancellationReason=BookingCancellationReasons.BENEFICIARY
        )

        api.cancel_bookings_when_offerer_deletes_stock(stock)

        assert models.Booking.query.filter().count() == 4
        assert models.Booking.query.filter(models.Booking.isCancelled == True).count() == 3
        assert models.Booking.query.filter(models.Booking.isUsed == True).count() == 1
        assert booking_1.isCancelled
        assert booking_1.cancellationReason == BookingCancellationReasons.OFFERER
        assert booking_2.isCancelled
        assert booking_2.cancellationReason == BookingCancellationReasons.OFFERER
        assert not used_booking.isCancelled
        assert not used_booking.cancellationReason
        assert cancelled_booking.isCancelled
        assert cancelled_booking.cancellationReason == BookingCancellationReasons.BENEFICIARY


@pytest.mark.usefixtures("db_session")
class CancelForFraudTest:
    def test_cancel(self):
        booking = factories.BookingFactory()
        api.cancel_booking_for_fraud(booking)
        assert booking.isCancelled
        assert booking.cancellationReason == BookingCancellationReasons.FRAUD


@pytest.mark.usefixtures("db_session")
class MarkAsUsedTest:
    def test_mark_as_used(self):
        booking = factories.BookingFactory()
        api.mark_as_used(booking)
        assert booking.isUsed

    def test_mark_as_used_with_uncancel(self):
        booking = factories.BookingFactory(isCancelled=True, cancellationReason="BENEFICIARY")
        api.mark_as_used(booking, uncancel=True)
        assert booking.isUsed
        assert not booking.isCancelled
        assert not booking.cancellationReason

    def test_mark_as_used_when_stock_starts_soon(self):
        booking = factories.BookingFactory(stock__beginningDatetime=datetime.now() + timedelta(days=1))
        api.mark_as_used(booking)
        assert booking.isUsed

    def test_raise_if_already_used(self):
        booking = factories.BookingFactory(isUsed=True)
        with pytest.raises(api_errors.ResourceGoneError):
            api.mark_as_used(booking)
        assert booking.isUsed  # unchanged

    def test_raise_if_cancelled(self):
        booking = factories.BookingFactory(isCancelled=True)
        with pytest.raises(api_errors.ForbiddenError):
            api.mark_as_used(booking)
        assert not booking.isUsed

    def test_raise_if_refunded(self):
        booking = factories.BookingFactory(isUsed=True)
        payments_factories.PaymentFactory(booking=booking)
        with pytest.raises(api_errors.ForbiddenError):
            api.mark_as_used(booking)
        assert booking.isUsed

    def test_raise_if_too_soon_to_mark_as_used(self):
        booking = factories.BookingFactory(stock__beginningDatetime=datetime.now() + timedelta(days=4))
        with pytest.raises(api_errors.ForbiddenError):
            api.mark_as_used(booking)
        assert not booking.isUsed


@pytest.mark.usefixtures("db_session")
class MarkAsUnusedTest:
    def test_mark_as_unused(self):
        booking = factories.BookingFactory(isUsed=True)
        api.mark_as_unused(booking)
        assert not booking.isUsed

    def test_raise_if_not_yet_used(self):
        booking = factories.BookingFactory(isUsed=False)
        with pytest.raises(api_errors.ResourceGoneError):
            api.mark_as_unused(booking)
        assert not booking.isUsed  # unchanged

    def test_raise_if_cancelled(self):
        booking = factories.BookingFactory(isUsed=True, isCancelled=True)
        with pytest.raises(api_errors.ForbiddenError):
            api.mark_as_unused(booking)
        assert booking.isUsed  # unchanged

    def test_raise_if_has_payment(self):
        booking = factories.BookingFactory(isUsed=True)
        payments_factories.PaymentFactory(booking=booking)
        with pytest.raises(api_errors.ResourceGoneError):
            api.mark_as_unused(booking)
        assert booking.isUsed  # unchanged


class GenerateQrCodeTest:
    @mock.patch("qrcode.QRCode")
    def test_correct_technical_parameters(self, build_qr_code):
        api.generate_qr_code(random_token(), offer_extra_data={})
        build_qr_code.assert_called_once_with(
            version=2,
            error_correction=3,
            box_size=5,
            border=1,
        )

    @mock.patch("qrcode.QRCode.make_image")
    def test_should_build_qr_code_with_correct_image_parameters(self, build_qr_code_image_parameters):
        api.generate_qr_code(booking_token="ABCDE", offer_extra_data={})
        build_qr_code_image_parameters.assert_called_once_with(
            back_color="white",
            fill_color="black",
        )

    @mock.patch("qrcode.QRCode.add_data")
    def test_include_product_isbn_if_provided(self, build_qr_code_booking_info):
        api.generate_qr_code("ABCDE", offer_extra_data={})
        build_qr_code_booking_info.assert_called_once_with("PASSCULTURE:v2;TOKEN:ABCDE")

        build_qr_code_booking_info.reset_mock()
        api.generate_qr_code("ABCDE", offer_extra_data={"isbn": "123456789"})
        build_qr_code_booking_info.assert_called_once_with("PASSCULTURE:v2;EAN13:123456789;TOKEN:ABCDE")

    def test_generated_qr_code(self):
        qr_code = api.generate_qr_code("ABCDE", offer_extra_data={})
        assert isinstance(qr_code, str)
        assert qr_code == (
            "data:image/png;base64,"
            "iVBORw0KGgoAAAANSUhEUgAAAJsAAACbAQAAAABdGtQhAAABs0lEQVR4nL1XMY7bMBCcFQXQqagf0EDeYSlp8o/8w7Hko/8VyfcR6gdURw"
            "KSJ4VdxYc0580WJDDFDHZJzoBCPNVcPWPAZ8EiIlKq5ZcUkWEWkfrTnB+DHRnRukDHBJAclIQoNeyI8758wwVFmhdwflD1fWMF2HNjXsL5"
            "b9BEdBw0hYQrIAkoXXOEZdIRQgaA3LoQc+tCBGCiihBJkiMMLVNPklQSmsiIjqvPrVs9mbQ6mpLhY2GI6BiUhG5uBW8uRDu6QMDpjK4uP3"
            "DxkLR9LSds+/wlKV1v+wYz4brYyGnmBGp5Xfk+r750zXEulav9ruOq5QxOxI6uhh2x7e3bSzifqwaW1QscPNikvuzQ/9Tp6ODDxBu2fekT"
            "AKFWHgFbhytMtL+bC3ZYdM4IWRJgR0daJkN7czoPtsLBD76cgDnTD8jvSS0m5nUGFtlLhU3ktOhE+d29c5d6kskwt0qje+SRcPBoXYhZy+"
            "uQOzJydCFaJsMsWnmUW5jIKT16g9boHuChMbyn31XpHT3AK46wZwlx176M829QuKL0Cdi1rp7t6HQs6H4yvOGIDPR6t07+12/iD1lz9hCJ"
            "WM0gAAAAAElFTkSuQmCC"
        )


@pytest.mark.parametrize(
    "booking_date",
    [datetime(2020, 7, 14, 15, 30), datetime(2020, 10, 25, 1, 45), datetime.now()],
    ids=["14 Jul", "Daylight Saving Switch", "Now"],
)
@pytest.mark.usefixtures("db_session")
class ComputeConfirmationDateTest:
    def test_returns_none_if_no_event_beginning(self, booking_date):
        event_beginning = None
        booking_creation = booking_date
        assert api.compute_confirmation_date(event_beginning, booking_creation) is None

    def test_returns_creation_date_if_event_begins_too_soon(self, booking_date):
        event_date_too_close_to_cancel_booking = booking_date + timedelta(days=1)
        booking_creation = booking_date
        assert (
            api.compute_confirmation_date(event_date_too_close_to_cancel_booking, booking_creation) == booking_creation
        )

    def test_returns_two_days_after_booking_creation_if_event_begins_in_more_than_four_days(self, booking_date):
        event_date_more_ten_days_from_now = booking_date + timedelta(days=6)
        booking_creation = booking_date
        assert api.compute_confirmation_date(
            event_date_more_ten_days_from_now, booking_creation
        ) == booking_creation + timedelta(days=2)

    def test_returns_two_days_before_event_if_event_begins_between_two_and_four_days_from_now(self, booking_date):
        event_date_four_days_from_now = booking_date + timedelta(days=4)
        booking_creation = booking_date
        assert api.compute_confirmation_date(
            event_date_four_days_from_now, booking_creation
        ) == event_date_four_days_from_now - timedelta(days=2)


@freeze_time("2020-11-17 15:00:00")
@pytest.mark.usefixtures("db_session")
class UpdateConfirmationDatesTest:
    def should_update_bookings_confirmation_dates_for_event_beginning_tomorrow(self):
        #  Given
        recent_booking = factories.BookingFactory(stock__beginningDatetime=datetime.now() + timedelta(days=90))
        old_booking = factories.BookingFactory(
            stock=recent_booking.stock, dateCreated=(datetime.now() - timedelta(days=7))
        )
        # When
        updated_bookings = api.update_confirmation_dates(
            bookings_to_update=[recent_booking, old_booking], new_beginning_datetime=datetime.now() + timedelta(days=1)
        )
        # Then
        assert updated_bookings == [recent_booking, old_booking]
        assert recent_booking.confirmationDate == old_booking.confirmationDate == datetime(2020, 11, 17, 15)

    def should_update_bookings_confirmation_dates_for_event_beginning_in_three_days(self):
        #  Given
        recent_booking = factories.BookingFactory(stock__beginningDatetime=datetime.now() + timedelta(days=90))
        old_booking = factories.BookingFactory(
            stock=recent_booking.stock, dateCreated=(datetime.now() - timedelta(days=7))
        )
        # When
        updated_bookings = api.update_confirmation_dates(
            bookings_to_update=[recent_booking, old_booking], new_beginning_datetime=datetime.now() + timedelta(days=3)
        )
        # Then
        assert updated_bookings == [recent_booking, old_booking]
        assert recent_booking.confirmationDate == old_booking.confirmationDate == datetime(2020, 11, 18, 15)

    def should_update_bookings_confirmation_dates_for_event_beginning_in_a_week(self):
        #  Given
        recent_booking = factories.BookingFactory(stock__beginningDatetime=datetime.now() + timedelta(days=90))
        old_booking = factories.BookingFactory(
            stock=recent_booking.stock, dateCreated=(datetime.now() - timedelta(days=7))
        )
        # When
        updated_bookings = api.update_confirmation_dates(
            bookings_to_update=[recent_booking, old_booking], new_beginning_datetime=datetime.now() + timedelta(days=7)
        )
        # Then
        assert updated_bookings == [recent_booking, old_booking]
        assert recent_booking.confirmationDate == old_booking.confirmationDate == datetime(2020, 11, 19, 15)
