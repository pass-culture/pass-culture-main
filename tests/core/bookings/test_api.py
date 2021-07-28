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
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.mails.testing as mails_testing
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.payments.factories as payments_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
from pcapi.models import api_errors
from pcapi.models.db import db
import pcapi.notifications.push.testing as push_testing
from pcapi.notifications.push.user_attributes_updates import BATCH_DATETIME_FORMAT
from pcapi.utils.token import random_token

from tests.conftest import clean_database


class BookOfferConcurrencyTest:
    @clean_database
    def test_create_booking(self, app):
        beneficiary = users_factories.BeneficiaryFactory()
        stock = offers_factories.StockFactory(price=10, dnBookedQuantity=5)
        assert models.Booking.query.count() == 0

        # open a second connection on purpose and lock the stock
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        with engine.connect() as connection:
            connection.execute(text("""SELECT * FROM stock WHERE stock.id = :stock_id FOR UPDATE"""), stock_id=stock.id)

            with pytest.raises(sqlalchemy.exc.OperationalError):
                api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

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

    @pytest.mark.usefixtures("db_session")
    def test_cancel_booking_with_concurrent_cancel(self, app):
        booking = factories.BookingFactory(stock__dnBookedQuantity=1)
        booking_id = booking.id
        dnBookedQuantity = booking.stock.dnBookedQuantity

        # simulate concurent change
        db.session.query(Booking).filter(Booking.id == booking_id).update(
            {Booking.isCancelled: True, Booking.cancellationReason: BookingCancellationReasons.BENEFICIARY},
            synchronize_session=False,
        )

        # Cancelling the booking (that appears as not cancelled as verified) should
        # not alter dnBookedQuantity due to the concurrent cancellation
        assert not booking.isCancelled
        assert booking.status is not BookingStatus.CANCELLED
        api._cancel_booking(booking, BookingCancellationReasons.BENEFICIARY)
        assert booking.stock.dnBookedQuantity == dnBookedQuantity

    @clean_database
    def test_cancel_all_bookings_from_stock(self, app):
        stock = offers_factories.StockFactory(dnBookedQuantity=1)
        factories.BookingFactory(stock=stock)
        factories.BookingFactory(stock=stock)
        factories.BookingFactory(stock=stock, isUsed=True, status=BookingStatus.USED)
        factories.BookingFactory(stock=stock, isCancelled=True, status=BookingStatus.CANCELLED)

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
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_create_booking(self, mocked_async_index_offer_ids, app):
        beneficiary = users_factories.BeneficiaryFactory()
        stock = offers_factories.StockFactory(price=10, dnBookedQuantity=5, offer__bookingEmail="offerer@example.com")

        booking = api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

        # One request should have been sent to Batch with the user's
        # updated attributes
        assert len(push_testing.requests) == 1

        data = push_testing.requests[0]
        assert data["attribute_values"]["u.credit"] == 49_000  # values in cents
        assert data["attribute_values"]["ut.booking_categories"] == [stock.offer.type]

        expected_date = booking.dateCreated.strftime(BATCH_DATETIME_FORMAT)
        assert data["attribute_values"]["date(u.last_booking_date)"] == expected_date

        expected_date = booking.dateCreated.strftime(BATCH_DATETIME_FORMAT)
        assert data["attribute_values"]["date(u.last_booking_date)"] == expected_date

        assert booking.quantity == 1
        assert booking.amount == 10
        assert booking.stock == stock
        assert len(booking.token) == 6
        assert not booking.isCancelled
        assert not booking.isUsed
        assert booking.status not in [BookingStatus.CANCELLED, BookingStatus.USED]
        assert booking.cancellationLimitDate is None
        assert stock.dnBookedQuantity == 6

        mocked_async_index_offer_ids.assert_called_once_with([stock.offer.id])

        assert len(mails_testing.outbox) == 2
        email_data1 = mails_testing.outbox[0].sent_data
        assert email_data1["MJ-TemplateID"] == 2843165  # to offerer
        email_data2 = mails_testing.outbox[1].sent_data
        assert email_data2["MJ-TemplateID"] == 2996790  # to beneficiary

    def test_booked_categories_are_sent_to_batch_backend(self, app):
        offer1 = offers_factories.OfferFactory(type="ThingType.AUDIOVISUEL")
        offer2 = offers_factories.OfferFactory(type="ThingType.CINEMA_ABO")
        offers_factories.OfferFactory(type="ThingType.INSTRUMENT")

        stock1 = offers_factories.StockFactory(price=10, dnBookedQuantity=5, offer=offer1)
        stock2 = offers_factories.StockFactory(price=10, dnBookedQuantity=5, offer=offer2)

        beneficiary = users_factories.BeneficiaryFactory()
        date_created = datetime.now() - timedelta(days=5)
        factories.BookingFactory.create_batch(3, user=beneficiary, dateCreated=date_created, stock=stock2)

        booking = api.book_offer(beneficiary=beneficiary, stock_id=stock1.id, quantity=1)

        # One request should have been sent to Batch with the user's
        # updated attributes
        assert len(push_testing.requests) == 1

        data = push_testing.requests[0]
        expected_date = booking.dateCreated.strftime(BATCH_DATETIME_FORMAT)
        assert data["attribute_values"]["date(u.last_booking_date)"] == expected_date

        expected_categories = ["ThingType.AUDIOVISUEL", "ThingType.CINEMA_ABO"]
        assert sorted(data["attribute_values"]["ut.booking_categories"]) == expected_categories

    @override_features(AUTO_ACTIVATE_DIGITAL_BOOKINGS=True, ENABLE_ACTIVATION_CODES=True)
    def test_booking_on_digital_offer_with_activation_stock(self):
        offer = offers_factories.OfferFactory(product=offers_factories.DigitalProductFactory())
        stock = offers_factories.StockWithActivationCodesFactory(price=10, dnBookedQuantity=3, offer=offer)
        beneficiary = users_factories.BeneficiaryFactory()

        booking = api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

        assert booking.isUsed
        assert booking.status is BookingStatus.USED

    @override_features(AUTO_ACTIVATE_DIGITAL_BOOKINGS=True, ENABLE_ACTIVATION_CODES=True)
    def test_booking_on_digital_offer_without_activation_stock(self):
        offer = offers_factories.OfferFactory(product=offers_factories.DigitalProductFactory())
        stock = offers_factories.StockFactory(price=10, dnBookedQuantity=5, offer=offer)
        beneficiary = users_factories.BeneficiaryFactory()

        booking = api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

        assert not booking.isUsed
        assert booking.status is not BookingStatus.USED

    def test_create_event_booking(self):
        ten_days_from_now = datetime.utcnow() + timedelta(days=10)
        beneficiary = users_factories.BeneficiaryFactory()
        stock = offers_factories.StockFactory(price=10, beginningDatetime=ten_days_from_now, dnBookedQuantity=5)

        booking = api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

        # One request should have been sent to Batch with the user's
        # updated attributes
        assert len(push_testing.requests) == 1

        data = push_testing.requests[0]
        assert data["attribute_values"]["u.credit"] == 49_000  # values in cents

        expected_date = booking.dateCreated.strftime(BATCH_DATETIME_FORMAT)
        assert data["attribute_values"]["date(u.last_booking_date)"] == expected_date

        two_days_after_booking = booking.dateCreated + timedelta(days=2)
        assert booking.quantity == 1
        assert booking.amount == 10
        assert booking.stock == stock
        assert stock.dnBookedQuantity == 6
        assert len(booking.token) == 6
        assert not booking.isCancelled
        assert not booking.isUsed
        assert booking.status not in [BookingStatus.CANCELLED, BookingStatus.USED]
        assert booking.cancellationLimitDate == two_days_after_booking

    def test_raise_if_is_admin(self):
        user = users_factories.AdminFactory()
        stock = offers_factories.StockFactory()

        with pytest.raises(exceptions.UserHasInsufficientFunds):
            api.book_offer(beneficiary=user, stock_id=stock.id, quantity=1)

    def test_raise_if_pro_user(self):
        pro = users_factories.ProFactory()
        stock = offers_factories.StockFactory()

        with pytest.raises(exceptions.UserHasInsufficientFunds):
            api.book_offer(beneficiary=pro, stock_id=stock.id, quantity=1)

    def test_raise_if_no_more_stock(self):
        booking = factories.BookingFactory(stock__quantity=1)
        with pytest.raises(exceptions.StockIsNotBookable):
            api.book_offer(
                beneficiary=users_factories.BeneficiaryFactory(),
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
                beneficiary=users_factories.BeneficiaryFactory(),
                stock_id=stock.id,
                quantity=1,
            )

    def test_raise_if_invalid_quantity(self):
        with pytest.raises(exceptions.QuantityIsInvalid):
            api.book_offer(
                beneficiary=users_factories.BeneficiaryFactory(),
                stock_id=offers_factories.StockFactory().id,
                quantity=2,
            )

    class WhenBookingWithActivationCodeTest:
        @override_features(ENABLE_ACTIVATION_CODES=True)
        def test_book_offer_with_first_activation_code_available(self):
            # Given
            beneficiary = users_factories.BeneficiaryFactory()
            stock = offers_factories.StockWithActivationCodesFactory()
            first_activation_code = stock.activationCodes[0]

            # When
            booking = api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

            # Then
            assert booking.activationCode == first_activation_code

        @override_features(ENABLE_ACTIVATION_CODES=True)
        def test_ignore_activation_that_is_already_used_for_booking(self):
            # Given
            beneficiary = users_factories.BeneficiaryFactory()
            booking = factories.BookingFactory(isUsed=True, status=BookingStatus.USED, token="ABCDEF")
            stock = offers_factories.StockWithActivationCodesFactory(
                activationCodes=["code-vgya451afvyux", "code-bha45k15fuz"]
            )
            stock.activationCodes[0].booking = booking

            # When
            booking = api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

            # Then
            assert booking.activationCode.code == "code-bha45k15fuz"

        @override_features(ENABLE_ACTIVATION_CODES=True)
        def test_raise_when_no_activation_code_available(self):
            # Given
            beneficiary = users_factories.BeneficiaryFactory()
            booking = factories.BookingFactory(isUsed=True, status=BookingStatus.USED, token="ABCDEF")
            stock = offers_factories.StockWithActivationCodesFactory(activationCodes=["code-vgya451afvyux"])
            stock.activationCodes[0].booking = booking

            # When
            with pytest.raises(exceptions.NoActivationCodeAvailable) as error:
                api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

            # Then
            assert Booking.query.count() == 1
            assert error.value.errors == {
                "noActivationCodeAvailable": ["Ce stock ne contient plus de code d'activation disponible."]
            }

        @override_features(ENABLE_ACTIVATION_CODES=True)
        def test_raise_when_activation_codes_are_expired(self):
            # Given
            beneficiary = users_factories.BeneficiaryFactory()
            stock = offers_factories.StockWithActivationCodesFactory(
                activationCodes__expirationDate=datetime(2000, 1, 1)
            )

            # When
            with pytest.raises(exceptions.NoActivationCodeAvailable) as error:
                api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

            # Then
            assert error.value.errors == {
                "noActivationCodeAvailable": ["Ce stock ne contient plus de code d'activation disponible."]
            }


@pytest.mark.usefixtures("db_session")
class CancelByBeneficiaryTest:
    def test_cancel_booking(self):
        stock = offers_factories.StockFactory(offer__bookingEmail="offerer@example.com")
        booking = factories.BookingFactory.create_batch(20, stock=stock)[0]

        queries = 1  # select booking
        queries += 1  # select user
        queries += 1  # select stock for update
        queries += 1  # refresh booking
        queries += 3  # update stock ; update booking ; release savepoint
        queries += 4  # (update batch attributes): select booking ; user ; user.bookings ; deposit
        queries += 1  # select offer
        queries += 2  # insert email ; release savepoint
        queries += 4  # (TODO: optimize) select booking ; stock ; offer ; user
        queries += 1  # select bookings of same stock with users joinedloaded to avoid N+1 requests
        queries += 2  # select venue ; offerer
        queries += 2  # insert email ; release savepoint
        with assert_num_queries(queries):
            api.cancel_booking_by_beneficiary(booking.user, booking)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

        assert booking.isCancelled
        assert booking.status is BookingStatus.CANCELLED
        assert booking.cancellationReason == BookingCancellationReasons.BENEFICIARY
        assert len(mails_testing.outbox) == 2
        email_data1 = mails_testing.outbox[0].sent_data
        assert email_data1["Mj-TemplateID"] == 1091464  # to beneficiary
        email_data2 = mails_testing.outbox[1].sent_data
        assert email_data2["MJ-TemplateID"] == 780015  # to offerer

    def test_cancel_booking_twice(self):
        booking = factories.BookingFactory()
        initial_quantity = booking.stock.dnBookedQuantity

        api.cancel_booking_by_beneficiary(booking.user, booking)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

        assert booking.isCancelled
        assert booking.status is BookingStatus.CANCELLED
        assert booking.stock.dnBookedQuantity == (initial_quantity - 1)

        api.cancel_booking_by_beneficiary(booking.user, booking)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

        assert booking.isCancelled
        assert booking.status is BookingStatus.CANCELLED
        assert booking.stock.dnBookedQuantity == (initial_quantity - 1)

    def test_raise_if_booking_is_already_used(self):
        booking = factories.BookingFactory(isUsed=True, status=BookingStatus.USED)

        with pytest.raises(exceptions.BookingIsAlreadyUsed):
            api.cancel_booking_by_beneficiary(booking.user, booking)
        assert not booking.isCancelled
        assert booking.status is not BookingStatus.CANCELLED

    def test_raise_if_event_too_close(self):
        event_date_too_close_to_cancel_booking = datetime.now() + timedelta(days=1)
        booking = factories.BookingFactory(
            stock__beginningDatetime=event_date_too_close_to_cancel_booking,
        )
        with pytest.raises(exceptions.CannotCancelConfirmedBooking) as exc:
            api.cancel_booking_by_beneficiary(booking.user, booking)
        assert not booking.isCancelled
        assert booking.status is not BookingStatus.CANCELLED
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
        assert booking.status is not BookingStatus.CANCELLED
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
        assert booking.status is not BookingStatus.CANCELLED
        assert not booking.cancellationReason
        assert exc.value.errors["booking"] == [
            "Impossible d'annuler une réservation plus de 48h après l'avoir "
            "réservée et moins de 48h avant le début de l'événement"
        ]

    def test_raise_if_trying_to_cancel_someone_else_s_booking(self):
        booking = factories.BookingFactory()
        other_beneficiary = users_factories.BeneficiaryFactory()
        with pytest.raises(exceptions.BookingDoesntExist):
            api.cancel_booking_by_beneficiary(other_beneficiary, booking)
        assert not booking.isCancelled
        assert booking.status is not BookingStatus.CANCELLED
        assert not booking.cancellationReason


@pytest.mark.usefixtures("db_session")
class CancelByOffererTest:
    def test_cancel(self):
        booking = factories.BookingFactory()

        api.cancel_booking_by_offerer(booking)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

        assert booking.isCancelled
        assert booking.status is BookingStatus.CANCELLED
        assert booking.cancellationReason == BookingCancellationReasons.OFFERER

        cancel_notification_request = next(
            req for req in push_testing.requests if req.get("group_id") == "Cancel_booking"
        )
        assert cancel_notification_request == {
            "group_id": "Cancel_booking",
            "message": {
                "body": f"""Ta commande "{booking.stock.offer.name}" a été annulée par l\'offreur.""",
                "title": "Commande annulée",
            },
            "user_ids": [booking.userId],
        }

    def test_raise_if_already_cancelled(self):
        booking = factories.BookingFactory(
            isCancelled=True, status=BookingStatus.CANCELLED, cancellationReason=BookingCancellationReasons.BENEFICIARY
        )
        with pytest.raises(api_errors.ResourceGoneError):
            api.cancel_booking_by_offerer(booking)
        assert booking.isCancelled
        assert booking.status is BookingStatus.CANCELLED
        assert booking.cancellationReason == BookingCancellationReasons.BENEFICIARY

        assert push_testing.requests == []

    def test_raise_if_already_used(self):
        booking = factories.BookingFactory(isUsed=True, status=BookingStatus.USED)
        with pytest.raises(api_errors.ForbiddenError):
            api.cancel_booking_by_offerer(booking)
        assert booking.isUsed
        assert not booking.isCancelled
        assert booking.status is not BookingStatus.CANCELLED
        assert not booking.cancellationReason

        assert push_testing.requests == []

    def test_cancel_all_bookings_from_stock(self, app):
        stock = offers_factories.StockFactory(dnBookedQuantity=1)
        booking_1 = factories.BookingFactory(stock=stock)
        booking_2 = factories.BookingFactory(stock=stock)
        used_booking = factories.BookingFactory(stock=stock, isUsed=True, status=BookingStatus.USED)
        cancelled_booking = factories.BookingFactory(
            stock=stock,
            isCancelled=True,
            status=BookingStatus.CANCELLED,
            cancellationReason=BookingCancellationReasons.BENEFICIARY,
        )

        api.cancel_bookings_when_offerer_deletes_stock(stock)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

        assert models.Booking.query.filter().count() == 4
        assert models.Booking.query.filter(models.Booking.isCancelled == True).count() == 3
        assert models.Booking.query.filter(models.Booking.isUsed == True).count() == 1
        assert booking_1.isCancelled
        assert booking_1.status is BookingStatus.CANCELLED
        assert booking_1.cancellationReason == BookingCancellationReasons.OFFERER
        assert booking_2.isCancelled
        assert booking_2.status is BookingStatus.CANCELLED
        assert booking_2.cancellationReason == BookingCancellationReasons.OFFERER
        assert not used_booking.isCancelled
        assert used_booking.status is not BookingStatus.CANCELLED
        assert not used_booking.cancellationReason
        assert cancelled_booking.isCancelled
        assert cancelled_booking.status is BookingStatus.CANCELLED
        assert cancelled_booking.cancellationReason == BookingCancellationReasons.BENEFICIARY


@pytest.mark.usefixtures("db_session")
class CancelForFraudTest:
    def test_cancel(self):
        booking = factories.BookingFactory()

        api.cancel_booking_for_fraud(booking)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

        assert booking.isCancelled
        assert booking.status is BookingStatus.CANCELLED
        assert booking.cancellationReason == BookingCancellationReasons.FRAUD


@pytest.mark.usefixtures("db_session")
class MarkAsUsedTest:
    def test_mark_as_used(self):
        booking = factories.BookingFactory()
        api.mark_as_used(booking)
        assert booking.isUsed
        assert booking.status is BookingStatus.USED
        assert len(push_testing.requests) == 1

    def test_mark_as_used_with_uncancel(self):
        booking = factories.BookingFactory(
            isCancelled=True, status=BookingStatus.CANCELLED, cancellationReason="BENEFICIARY"
        )
        api.mark_as_used(booking, uncancel=True)
        assert booking.isUsed
        assert not booking.isCancelled
        assert booking.status is BookingStatus.USED
        assert not booking.cancellationReason

    def test_mark_as_used_when_stock_starts_soon(self):
        booking = factories.BookingFactory(stock__beginningDatetime=datetime.now() + timedelta(days=1))
        api.mark_as_used(booking)
        assert booking.isUsed
        assert booking.status is BookingStatus.USED

    def test_raise_if_already_used(self):
        booking = factories.BookingFactory(isUsed=True, status=BookingStatus.USED)
        with pytest.raises(api_errors.ResourceGoneError):
            api.mark_as_used(booking)

    def test_raise_if_cancelled(self):
        booking = factories.BookingFactory(isCancelled=True, status=BookingStatus.CANCELLED)
        with pytest.raises(api_errors.ForbiddenError):
            api.mark_as_used(booking)
        assert not booking.isUsed
        assert booking.status is not BookingStatus.USED

    def test_raise_if_already_reimbursed(self):
        booking = factories.BookingFactory(isUsed=True, status=BookingStatus.USED)
        payments_factories.PaymentFactory(booking=booking)
        with pytest.raises(api_errors.ForbiddenError):
            api.mark_as_used(booking)

    def test_raise_if_too_soon_to_mark_as_used(self):
        booking = factories.BookingFactory(stock__beginningDatetime=datetime.now() + timedelta(days=4))
        with pytest.raises(api_errors.ForbiddenError):
            api.mark_as_used(booking)
        assert not booking.isUsed
        assert booking.status is not BookingStatus.USED


@pytest.mark.usefixtures("db_session")
class MarkAsUnusedTest:
    def test_mark_as_unused(self):
        booking = factories.BookingFactory(isUsed=True, status=BookingStatus.USED)
        api.mark_as_unused(booking)
        assert not booking.isUsed
        assert booking.status is not BookingStatus.USED
        assert len(push_testing.requests) == 1

    @override_features(AUTO_ACTIVATE_DIGITAL_BOOKINGS=True)
    def test_mark_as_unused_digital_offer(self):
        offer = offers_factories.OfferFactory(product=offers_factories.DigitalProductFactory())
        booking = factories.BookingFactory(isUsed=True, status=BookingStatus.USED, stock__offer=offer)
        api.mark_as_unused(booking)
        assert not booking.isUsed
        assert booking.status is not BookingStatus.USED

    def test_raise_if_not_yet_used(self):
        booking = factories.BookingFactory(isUsed=False)
        with pytest.raises(api_errors.ResourceGoneError):
            api.mark_as_unused(booking)
        assert not booking.isUsed  # unchanged
        assert booking.status is not BookingStatus.USED

    def test_raise_if_has_payment(self):
        booking = factories.BookingFactory(isUsed=True, status=BookingStatus.USED)
        payments_factories.PaymentFactory(booking=booking)
        with pytest.raises(api_errors.ResourceGoneError):
            api.mark_as_unused(booking)
        assert booking.isUsed  # unchanged
        assert booking.status is BookingStatus.USED

    @override_features(AUTO_ACTIVATE_DIGITAL_BOOKINGS=True)
    def test_raise_if_booking_was_automatically_used_for_digital_offer_with_activation_code(self):
        offer = offers_factories.OfferFactory(product=offers_factories.DigitalProductFactory())
        digital_stock = offers_factories.StockWithActivationCodesFactory()
        first_activation_code = digital_stock.activationCodes[0]
        booking = factories.BookingFactory(
            isUsed=True, status=BookingStatus.USED, stock__offer=offer, activationCode=first_activation_code
        )
        with pytest.raises(api_errors.ForbiddenError):
            api.mark_as_unused(booking)
        assert booking.isUsed
        assert booking.status is BookingStatus.USED


class GenerateQrCodeTest:
    @mock.patch("qrcode.QRCode")
    def test_correct_technical_parameters(self, build_qr_code):
        api.generate_qr_code(random_token())
        build_qr_code.assert_called_once_with(
            version=2,
            error_correction=3,
            box_size=5,
            border=1,
        )

    @mock.patch("qrcode.QRCode.make_image")
    def test_should_build_qr_code_with_correct_image_parameters(self, build_qr_code_image_parameters):
        api.generate_qr_code(booking_token="ABCDE")
        build_qr_code_image_parameters.assert_called_once_with(
            back_color="white",
            fill_color="black",
        )

    @mock.patch("qrcode.QRCode.add_data")
    def test_include_product_isbn_if_provided(self, build_qr_code_booking_info):
        api.generate_qr_code("ABCDE")
        build_qr_code_booking_info.assert_called_once_with("PASSCULTURE:v3;TOKEN:ABCDE")

    def test_generated_qr_code(self):
        qr_code = api.generate_qr_code("ABCDE")
        assert isinstance(qr_code, str)
        assert qr_code == (
            "data:image/png;base64,"
            "iVBORw0KGgoAAAANSUhEUgAAAJsAAACbAQAAAABdGtQhAAABrUlEQVR4nL1XQW7bMB"
            "CcFQVQN6ovoD9isf1XE8mhgT6rUvoR6gf0jQRoTw/OpU3QS7zdC4E5zGAXw+FSiHe1"
            "d+8x4LNgFRGp3WXZq8iyi0j"
            "/ac6PwUAmHP1TcMwAyUVJiNLDxvwj1a84o8r4AM5/gJcF9jQ+lvOP6u/H8UsDAs96Q"
            "h2EDZB92QvH77DMOkIoAFAmF1OZXEwATFLpyJKkfQG83fbmSTadjriRCYHNY3LNk1m"
            "nIxTJhmSG58aYEBiVhOCYuLpIu7pIwFFHiDcXyZsjMbnFF6GeUAO3PCcyz6moua5+y"
            "4YDANTO9X4ISq7rsI0nAX0Pu+J6sC+P4PyoClzzXDGzwJEFmHVGhwlmw+TkgJABCLX"
            "eI+AUAJhkf45nDLgoJUORbJJdXYNlNrQ3p3NhOxx9DfUZhoV+QfmVtcwQGJNdAQBuA"
            "YJW1pEky+RIMhuWSWl0b++RcPGYXExFLetKIBNXmGSZDdWy7r4FQfL1cJHxKsNxPGt"
            "uQccRHoHNl1ele/QGvmJO9iQxDdPDOP8GhQ11zsAQ2O92dToRdHcdt2xSAWY918n/+"
            "k38Bmlp+NQ0I934AAAAAElFTkSuQmCC"
        )


@pytest.mark.parametrize(
    "booking_date",
    [datetime(2020, 7, 14, 15, 30), datetime(2020, 10, 25, 1, 45), datetime.now()],
    ids=["14 Jul", "Daylight Saving Switch", "Now"],
)
@pytest.mark.usefixtures("db_session")
class ComputeCancellationDateTest:
    def test_returns_none_if_no_event_beginning(self, booking_date):
        event_beginning = None
        booking_creation = booking_date
        assert api.compute_cancellation_limit_date(event_beginning, booking_creation) is None

    def test_returns_creation_date_if_event_begins_too_soon(self, booking_date):
        event_date_too_close_to_cancel_booking = booking_date + timedelta(days=1)
        booking_creation = booking_date
        assert (
            api.compute_cancellation_limit_date(event_date_too_close_to_cancel_booking, booking_creation)
            == booking_creation
        )

    def test_returns_two_days_after_booking_creation_if_event_begins_in_more_than_four_days(self, booking_date):
        event_date_more_ten_days_from_now = booking_date + timedelta(days=6)
        booking_creation = booking_date
        assert api.compute_cancellation_limit_date(
            event_date_more_ten_days_from_now, booking_creation
        ) == booking_creation + timedelta(days=2)

    def test_returns_two_days_before_event_if_event_begins_between_two_and_four_days_from_now(self, booking_date):
        event_date_four_days_from_now = booking_date + timedelta(days=4)
        booking_creation = booking_date
        assert api.compute_cancellation_limit_date(
            event_date_four_days_from_now, booking_creation
        ) == event_date_four_days_from_now - timedelta(days=2)


@freeze_time("2020-11-17 15:00:00")
@pytest.mark.usefixtures("db_session")
class UpdateCancellationLimitDatesTest:
    def should_update_bookings_cancellation_limit_dates_for_event_beginning_tomorrow(self):
        #  Given
        recent_booking = factories.BookingFactory(stock__beginningDatetime=datetime.now() + timedelta(days=90))
        old_booking = factories.BookingFactory(
            stock=recent_booking.stock, dateCreated=(datetime.now() - timedelta(days=7))
        )
        # When
        updated_bookings = api.update_cancellation_limit_dates(
            bookings_to_update=[recent_booking, old_booking], new_beginning_datetime=datetime.now() + timedelta(days=1)
        )
        # Then
        assert updated_bookings == [recent_booking, old_booking]
        assert recent_booking.cancellationLimitDate == old_booking.cancellationLimitDate == datetime(2020, 11, 17, 15)

    def should_update_bookings_cancellation_limit_dates_for_event_beginning_in_three_days(self):
        #  Given
        recent_booking = factories.BookingFactory(stock__beginningDatetime=datetime.now() + timedelta(days=90))
        old_booking = factories.BookingFactory(
            stock=recent_booking.stock, dateCreated=(datetime.now() - timedelta(days=7))
        )
        # When
        updated_bookings = api.update_cancellation_limit_dates(
            bookings_to_update=[recent_booking, old_booking], new_beginning_datetime=datetime.now() + timedelta(days=3)
        )
        # Then
        assert updated_bookings == [recent_booking, old_booking]
        assert recent_booking.cancellationLimitDate == old_booking.cancellationLimitDate == datetime(2020, 11, 18, 15)

    def should_update_bookings_cancellation_limit_dates_for_event_beginning_in_a_week(self):
        #  Given
        recent_booking = factories.BookingFactory(stock__beginningDatetime=datetime.now() + timedelta(days=90))
        old_booking = factories.BookingFactory(
            stock=recent_booking.stock, dateCreated=(datetime.now() - timedelta(days=7))
        )
        # When
        updated_bookings = api.update_cancellation_limit_dates(
            bookings_to_update=[recent_booking, old_booking], new_beginning_datetime=datetime.now() + timedelta(days=7)
        )
        # Then
        assert updated_bookings == [recent_booking, old_booking]
        assert recent_booking.cancellationLimitDate == old_booking.cancellationLimitDate == datetime(2020, 11, 19, 15)


@pytest.mark.usefixtures("db_session")
class AutoMarkAsUsedAfterEventTest:
    def test_do_not_update_if_thing_product(self):
        factories.BookingFactory(stock=offers_factories.ThingStockFactory())

        api.auto_mark_as_used_after_event()

        booking = Booking.query.first()
        assert not booking.isUsed
        assert booking.status is not BookingStatus.USED
        assert not booking.dateUsed

    @freeze_time("2021-01-01")
    def test_update_booking_used_when_event_date_is_3_days_before(self):
        event_date = datetime.now() - timedelta(days=3)
        factories.BookingFactory(stock__beginningDatetime=event_date)

        api.auto_mark_as_used_after_event()

        booking = Booking.query.first()
        assert booking.isUsed
        assert booking.status is BookingStatus.USED
        assert booking.dateUsed == datetime(2021, 1, 1)

    @freeze_time("2021-01-01")
    @pytest.mark.usefixtures("db_session")
    def test_does_not_update_when_event_date_is_only_1_day_before(self):
        event_date = datetime.now() - timedelta(days=1)
        factories.BookingFactory(stock__beginningDatetime=event_date)

        api.auto_mark_as_used_after_event()

        booking = Booking.query.first()
        assert not booking.isUsed
        assert booking.status is not BookingStatus.USED
        assert booking.dateUsed is None

    @freeze_time("2021-01-01")
    def test_does_not_update_booking_if_already_used(self):
        event_date = datetime.now() - timedelta(days=3)
        booking = factories.BookingFactory(stock__beginningDatetime=event_date, isUsed=True)
        initial_date_used = booking.dateUsed

        api.auto_mark_as_used_after_event()

        booking = Booking.query.first()
        assert booking.isUsed
        assert booking.dateUsed == initial_date_used

    @pytest.mark.usefixtures("db_session")
    @override_features(UPDATE_BOOKING_USED=False)
    def test_raise_if_feature_flag_is_deactivated(self):
        with pytest.raises(ValueError):
            api.auto_mark_as_used_after_event()
