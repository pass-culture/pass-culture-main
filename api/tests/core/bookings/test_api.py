import dataclasses
import datetime
from datetime import datetime
from datetime import timedelta
from unittest import mock
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import pytest
from sqlalchemy import create_engine
import sqlalchemy.exc
from sqlalchemy.sql import text

from pcapi.core.booking_providers.factories import ExternalBookingFactory
from pcapi.core.booking_providers.factories import VenueBookingProviderFactory
from pcapi.core.booking_providers.models import Ticket
from pcapi.core.bookings import api
from pcapi.core.bookings import exceptions
from pcapi.core.bookings import factories as booking_factories
from pcapi.core.bookings import models
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
import pcapi.core.educational.factories as educational_factories
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import EducationalBookingStatus
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.users.external.batch import BATCH_DATETIME_FORMAT
import pcapi.core.users.factories as users_factories
from pcapi.models import api_errors
from pcapi.models import db
import pcapi.notifications.push.testing as push_testing

from tests.conftest import clean_database


class BookOfferConcurrencyTest:
    @clean_database
    def test_create_booking(self, app):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
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
        booking = booking_factories.IndividualBookingFactory(stock__dnBookedQuantity=1)

        # open a second connection on purpose and lock the stock
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        with engine.connect() as connection:
            connection.execute(
                text("""SELECT * FROM stock WHERE stock.id = :stock_id FOR UPDATE"""), stock_id=booking.stockId
            )

            with pytest.raises(sqlalchemy.exc.OperationalError):
                api.cancel_booking_by_beneficiary(booking.individualBooking.user, booking)

        assert models.Booking.query.filter().count() == 1
        assert models.Booking.query.filter(models.Booking.status == BookingStatus.CANCELLED).count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_cancel_booking_with_concurrent_cancel(self, app):
        booking = booking_factories.IndividualBookingFactory(stock__dnBookedQuantity=1)
        booking_id = booking.id
        dnBookedQuantity = booking.stock.dnBookedQuantity

        # simulate concurent change
        db.session.query(Booking).filter(Booking.id == booking_id).update(
            {
                Booking.status: BookingStatus.CANCELLED,
                Booking.cancellationReason: BookingCancellationReasons.BENEFICIARY,
            },
            synchronize_session=False,
        )

        # Cancelling the booking (that appears as not cancelled as verified) should
        # not alter dnBookedQuantity due to the concurrent cancellation
        assert booking.status is not BookingStatus.CANCELLED
        api._cancel_booking(booking, BookingCancellationReasons.BENEFICIARY)
        assert booking.stock.dnBookedQuantity == dnBookedQuantity

    @clean_database
    def test_cancel_all_bookings_from_stock(self, app):
        stock = offers_factories.StockFactory(dnBookedQuantity=1)
        booking_factories.IndividualBookingFactory(stock=stock)
        booking_factories.IndividualBookingFactory(stock=stock)
        booking_factories.UsedIndividualBookingFactory(stock=stock)
        booking_factories.CancelledIndividualBookingFactory(stock=stock)

        # open a second connection on purpose and lock the stock
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        with engine.connect() as connection:
            connection.execute(text("""SELECT * FROM stock WHERE stock.id = :stock_id FOR UPDATE"""), stock_id=stock.id)

            with pytest.raises(sqlalchemy.exc.OperationalError):
                api.cancel_bookings_from_stock_by_offerer(stock)

        assert models.Booking.query.filter().count() == 4
        assert models.Booking.query.filter(models.Booking.status == BookingStatus.CANCELLED).count() == 1


@pytest.mark.usefixtures("db_session")
class BookOfferTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_create_booking(self, mocked_async_index_offer_ids, app):

        beneficiary = users_factories.BeneficiaryGrant18Factory()
        stock = offers_factories.StockFactory(price=10, dnBookedQuantity=5, offer__bookingEmail="offerer@example.com")

        # There is a different email for the first venue booking
        booking_factories.IndividualBookingFactory(stock=stock)

        booking = api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

        # One request should have been sent to Batch with the user's
        # updated attributes
        assert len(push_testing.requests) == 2

        data = push_testing.requests[0]
        assert data["attribute_values"]["u.credit"] == 29_000  # values in cents
        assert data["attribute_values"]["ut.booking_categories"] == ["FILM"]

        expected_date = booking.dateCreated.strftime(BATCH_DATETIME_FORMAT)
        assert data["attribute_values"]["date(u.last_booking_date)"] == expected_date

        expected_date = booking.dateCreated.strftime(BATCH_DATETIME_FORMAT)
        assert data["attribute_values"]["date(u.last_booking_date)"] == expected_date

        assert booking.quantity == 1
        assert booking.individualBookingId is not None
        assert booking.individualBooking.userId == beneficiary.id
        assert booking.individualBooking.depositId == beneficiary.deposit.id
        assert booking.amount == 10
        assert booking.stock == stock
        assert len(booking.token) == 6
        assert booking.status is BookingStatus.CONFIRMED
        assert booking.cancellationLimitDate is None
        assert stock.dnBookedQuantity == 7

        mocked_async_index_offer_ids.assert_called_once_with([stock.offer.id])

        assert len(mails_testing.outbox) == 2
        email_data1 = mails_testing.outbox[0].sent_data
        assert email_data1["template"] == dataclasses.asdict(TransactionalEmail.NEW_BOOKING_TO_PRO.value)  # to offerer
        email_data2 = mails_testing.outbox[1].sent_data
        assert email_data2["template"] == dataclasses.asdict(
            TransactionalEmail.BOOKING_CONFIRMATION_BY_BENEFICIARY.value
        )  # to beneficiary

    def test_if_it_is_first_venue_booking_to_send_specific_email(self):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        stock = offers_factories.StockFactory(price=10, dnBookedQuantity=5, offer__bookingEmail="offerer@example.com")

        api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)
        assert len(mails_testing.outbox) == 2
        email_data1 = mails_testing.outbox[0].sent_data
        assert email_data1["template"] == dataclasses.asdict(
            TransactionalEmail.FIRST_VENUE_BOOKING_TO_PRO.value
        )  # to offerer
        email_data2 = mails_testing.outbox[1].sent_data
        assert email_data2["template"] == dataclasses.asdict(
            TransactionalEmail.BOOKING_CONFIRMATION_BY_BENEFICIARY.value
        )  # to beneficiary

    def test_free_offer_booking_by_ex_beneficiary(self):
        with freeze_time(datetime.utcnow() - relativedelta(years=2, months=5)):
            ex_beneficiary = users_factories.BeneficiaryGrant18Factory()
        stock = offers_factories.StockFactory(price=0, dnBookedQuantity=5, offer__bookingEmail="offerer@example.com")

        booking = api.book_offer(beneficiary=ex_beneficiary, stock_id=stock.id, quantity=1)

        assert not booking.individualBooking.deposit

    def test_booked_categories_are_sent_to_batch_backend(self, app):
        offer1 = offers_factories.OfferFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id)
        offer2 = offers_factories.OfferFactory(subcategoryId=subcategories.CARTE_CINE_ILLIMITE.id)

        offers_factories.OfferFactory(subcategoryId=subcategories.ACHAT_INSTRUMENT.id)

        stock1 = offers_factories.StockFactory(price=10, dnBookedQuantity=5, offer=offer1)
        stock2 = offers_factories.StockFactory(price=10, dnBookedQuantity=5, offer=offer2)

        beneficiary = users_factories.BeneficiaryGrant18Factory()
        date_created = datetime.utcnow() - timedelta(days=5)
        booking_factories.IndividualBookingFactory.create_batch(
            3, individualBooking__user=beneficiary, dateCreated=date_created, stock=stock2
        )

        booking = api.book_offer(beneficiary=beneficiary, stock_id=stock1.id, quantity=1)

        # One request should have been sent to Batch with the user's
        # updated attributes
        assert len(push_testing.requests) == 2

        data = push_testing.requests[0]
        expected_date = booking.dateCreated.strftime(BATCH_DATETIME_FORMAT)
        assert data["attribute_values"]["date(u.last_booking_date)"] == expected_date

        expected_categories = ["CINEMA", "FILM"]
        assert sorted(data["attribute_values"]["ut.booking_categories"]) == expected_categories

    def test_booking_on_digital_offer_with_activation_stock(self):
        offer = offers_factories.OfferFactory(product=offers_factories.DigitalProductFactory())
        stock = offers_factories.StockWithActivationCodesFactory(price=10, dnBookedQuantity=3, offer=offer)
        beneficiary = users_factories.BeneficiaryGrant18Factory()

        booking = api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

        assert booking.status is BookingStatus.USED

    def test_booking_on_digital_offer_without_activation_stock(self):
        offer = offers_factories.OfferFactory(product=offers_factories.DigitalProductFactory())
        stock = offers_factories.StockFactory(price=10, dnBookedQuantity=5, offer=offer)
        beneficiary = users_factories.BeneficiaryGrant18Factory()

        booking = api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

        assert booking.status is not BookingStatus.USED

    def test_create_event_booking(self):
        ten_days_from_now = datetime.utcnow() + timedelta(days=10)
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        stock = offers_factories.StockFactory(price=10, beginningDatetime=ten_days_from_now, dnBookedQuantity=5)

        booking = api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

        # One request should have been sent to Batch with the user's
        # updated attributes
        assert len(push_testing.requests) == 2

        data = push_testing.requests[0]
        assert data["attribute_values"]["u.credit"] == 29_000  # values in cents

        expected_date = booking.dateCreated.strftime(BATCH_DATETIME_FORMAT)
        assert data["attribute_values"]["date(u.last_booking_date)"] == expected_date

        two_days_after_booking = booking.dateCreated + timedelta(days=2)
        assert booking.quantity == 1
        assert booking.amount == 10
        assert booking.stock == stock
        assert stock.dnBookedQuantity == 6
        assert len(booking.token) == 6
        assert booking.status is BookingStatus.CONFIRMED
        assert booking.cancellationLimitDate == two_days_after_booking

    def test_book_stock_with_unlimited_quantity(self):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        stock = offers_factories.StockFactory(price=10, quantity=None)

        booking = api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

        assert booking.quantity == 1
        assert stock.quantity is None

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
        booking = booking_factories.IndividualBookingFactory(stock__quantity=1)
        with pytest.raises(exceptions.StockIsNotBookable):
            api.book_offer(
                beneficiary=users_factories.BeneficiaryGrant18Factory(),
                stock_id=booking.stock.id,
                quantity=1,
            )

    def test_raise_if_user_has_already_booked(self):
        booking = booking_factories.IndividualBookingFactory()
        with pytest.raises(exceptions.OfferIsAlreadyBooked):
            api.book_offer(
                beneficiary=booking.individualBooking.user,
                stock_id=booking.stock.id,
                quantity=1,
            )

    def test_raise_if_user_has_no_more_money(self):
        stock = offers_factories.StockFactory(price=800)
        with pytest.raises(exceptions.UserHasInsufficientFunds):
            api.book_offer(
                beneficiary=users_factories.BeneficiaryGrant18Factory(),
                stock_id=stock.id,
                quantity=1,
            )

    def test_raise_if_invalid_quantity(self):
        with pytest.raises(exceptions.QuantityIsInvalid):
            api.book_offer(
                beneficiary=users_factories.BeneficiaryGrant18Factory(),
                stock_id=offers_factories.StockFactory().id,
                quantity=2,
            )

    def test_raise_if_offer_is_educational(self):
        with pytest.raises(exceptions.EducationalOfferCannotBeBooked):
            api.book_offer(
                beneficiary=users_factories.BeneficiaryGrant18Factory(),
                stock_id=offers_factories.EducationalEventStockFactory(offer__isEducational=True).id,
                quantity=2,
            )

    class WhenBookingWithActivationCodeTest:
        def test_book_offer_with_first_activation_code_available(self):
            # Given
            beneficiary = users_factories.BeneficiaryGrant18Factory()
            stock = offers_factories.StockWithActivationCodesFactory()
            first_activation_code = stock.activationCodes[0]

            # When
            booking = api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

            # Then
            assert booking.activationCode == first_activation_code

        def test_ignore_activation_that_is_already_used_for_booking(self):
            # Given
            beneficiary = users_factories.BeneficiaryGrant18Factory()
            booking = booking_factories.UsedIndividualBookingFactory(token="ABCDEF")
            stock = offers_factories.StockWithActivationCodesFactory(
                activationCodes=["code-vgya451afvyux", "code-bha45k15fuz"]
            )
            stock.activationCodes[0].booking = booking

            # When
            booking = api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

            # Then
            assert booking.activationCode.code == "code-bha45k15fuz"

        def test_raise_when_no_activation_code_available(self):
            # Given
            beneficiary = users_factories.BeneficiaryGrant18Factory()
            booking = booking_factories.UsedIndividualBookingFactory(token="ABCDEF")
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

        def test_raise_when_activation_codes_are_expired(self):
            # Given
            beneficiary = users_factories.BeneficiaryGrant18Factory()
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

    class WhenBookingIsExternalBookingTest:
        @patch("pcapi.core.bookings.api.booking_providers_api.book_ticket")
        @override_features(ENABLE_CDS_IMPLEMENTATION=True)
        def test_book_offer_with_solo_external_booking(
            self,
            mocked_book_ticket,
        ):
            mocked_book_ticket.return_value = [Ticket(barcode="testbarcode", seat_number="A_1")]

            # Given
            beneficiary = users_factories.BeneficiaryGrant18Factory()
            venue_provider = VenueBookingProviderFactory()
            offer_solo = offers_factories.EventOfferFactory(
                name="Séance ciné solo", venue=venue_provider.venue, subcategoryId=subcategories.SEANCE_CINE.id
            )
            stock_solo = offers_factories.EventStockFactory(offer=offer_solo, idAtProviders="1111%4444#111/datetime")

            # When
            booking = api.book_offer(beneficiary=beneficiary, stock_id=stock_solo.id, quantity=1)

            # Then
            assert len(booking.externalBookings) == 1
            assert booking.externalBookings[0].barcode == "testbarcode"
            assert booking.externalBookings[0].seat == "A_1"

        @patch("pcapi.core.bookings.api.booking_providers_api.book_ticket")
        @override_features(ENABLE_CDS_IMPLEMENTATION=True)
        def test_book_offer_with_duo_external_booking(self, mocked_book_ticket):
            mocked_book_ticket.return_value = [
                Ticket(barcode="barcode1", seat_number="B_1"),
                Ticket(barcode="barcode2", seat_number="B_2"),
            ]
            # Given
            beneficiary = users_factories.BeneficiaryGrant18Factory()
            venue_provider = VenueBookingProviderFactory()
            offer_duo = offers_factories.EventOfferFactory(
                name="Séance ciné duo",
                venue=venue_provider.venue,
                subcategoryId=subcategories.SEANCE_CINE.id,
            )
            stock_duo = offers_factories.EventStockFactory(offer=offer_duo, idAtProviders="1111%4444#111/datetime")

            # When
            booking = api.book_offer(beneficiary=beneficiary, stock_id=stock_duo.id, quantity=1)

            # Then
            assert len(booking.externalBookings) == 2
            assert booking.externalBookings[0].barcode == "barcode1"
            assert booking.externalBookings[0].seat == "B_1"
            assert booking.externalBookings[1].barcode == "barcode2"
            assert booking.externalBookings[1].seat == "B_2"

        @patch("pcapi.core.bookings.api.booking_providers_api.book_ticket")
        @override_features(ENABLE_CDS_IMPLEMENTATION=True)
        def should_not_create_external_booking_when_venue_booking_provider_is_not_active(
            self,
            mocked_book_ticket,
        ):
            mocked_book_ticket.return_value = [Ticket(barcode="testbarcode", seat_number="A_1")]

            # Given
            beneficiary = users_factories.BeneficiaryGrant18Factory()
            venue_provider = VenueBookingProviderFactory(isActive=False)
            offer_solo = offers_factories.EventOfferFactory(
                name="Séance ciné solo", venue=venue_provider.venue, subcategoryId=subcategories.SEANCE_CINE.id
            )
            stock_solo = offers_factories.EventStockFactory(offer=offer_solo, idAtProviders="1111%4444#111/datetime")

            # When
            booking = api.book_offer(beneficiary=beneficiary, stock_id=stock_solo.id, quantity=1)

            # Then
            assert len(booking.externalBookings) == 0
            mocked_book_ticket.assert_not_called()


@pytest.mark.usefixtures("db_session")
class CancelByBeneficiaryTest:
    def test_cancel_booking(self):
        stock = offers_factories.StockFactory(offer__bookingEmail="offerer@example.com")
        booking = booking_factories.IndividualBookingFactory.create_batch(20, stock=stock)[0]

        queries = 2  # select stock ; select booking
        queries += 1  # update booking
        queries += 1  # select feature_flag
        queries += 3  # update stock ; update booking ;  release savepoint
        queries += 7  # (update batch attributes): select booking ; individualBooking ; user_offerer exists ; user.bookings ;  favorites ; deposit ; wallet balance
        queries += 1  # select venue by id
        queries += 2  # select user by email ; select venue by same booking email
        queries += 1  # select offerer by id
        queries += 1  # select bank_information by venue.id
        queries += 1  # select exists offer
        queries += 1  # select exists booking
        queries += 1  # select stock
        queries += 1  # select booking ; offer
        queries += 1  # select external_booking

        individual_booking = booking.individualBooking
        user = individual_booking.user
        with assert_num_queries(queries):
            api.cancel_booking_by_beneficiary(user, booking)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

        assert booking.status is BookingStatus.CANCELLED
        assert booking.cancellationReason == BookingCancellationReasons.BENEFICIARY
        assert len(mails_testing.outbox) == 2
        email_data1 = mails_testing.outbox[0].sent_data
        assert email_data1["template"] == dataclasses.asdict(
            TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY.value
        )  # to beneficiary
        email_data2 = mails_testing.outbox[1].sent_data
        assert email_data2["template"] == dataclasses.asdict(
            TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO.value
        )  # to offerer

    def test_cancel_booking_twice(self):
        booking = booking_factories.IndividualBookingFactory()
        initial_quantity = booking.stock.dnBookedQuantity

        api.cancel_booking_by_beneficiary(booking.individualBooking.user, booking)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

        assert booking.status is BookingStatus.CANCELLED
        assert booking.stock.dnBookedQuantity == (initial_quantity - 1)

        api.cancel_booking_by_beneficiary(booking.individualBooking.user, booking)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

        assert booking.status is BookingStatus.CANCELLED
        assert booking.stock.dnBookedQuantity == (initial_quantity - 1)

    def test_raise_if_booking_is_already_used(self):
        booking = booking_factories.UsedIndividualBookingFactory()

        with pytest.raises(exceptions.BookingIsAlreadyUsed):
            api.cancel_booking_by_beneficiary(booking.individualBooking.user, booking)
        assert booking.status is not BookingStatus.CANCELLED

    def test_raise_if_event_too_close(self):
        event_date_too_close_to_cancel_booking = datetime.utcnow() + timedelta(days=1)
        booking = booking_factories.IndividualBookingFactory(
            stock__beginningDatetime=event_date_too_close_to_cancel_booking,
        )
        with pytest.raises(exceptions.CannotCancelConfirmedBooking) as exc:
            api.cancel_booking_by_beneficiary(booking.individualBooking.user, booking)
        assert booking.status is not BookingStatus.CANCELLED
        assert not booking.cancellationReason
        assert exc.value.errors["booking"] == [
            "Impossible d'annuler une réservation plus de 48h après l'avoir "
            "réservée et moins de 48h avant le début de l'événement"
        ]

    def test_raise_if_booking_created_too_long_ago_to_cancel_booking(self):
        event_date_far_enough_to_cancel_booking = datetime.utcnow() + timedelta(days=2, minutes=1)
        booking_date_too_long_ago_to_cancel_booking = datetime.utcnow() - timedelta(days=2, minutes=1)
        booking = booking_factories.IndividualBookingFactory(
            stock__beginningDatetime=event_date_far_enough_to_cancel_booking,
            dateCreated=booking_date_too_long_ago_to_cancel_booking,
        )
        with pytest.raises(exceptions.CannotCancelConfirmedBooking) as exc:
            api.cancel_booking_by_beneficiary(booking.individualBooking.user, booking)
        assert booking.status is not BookingStatus.CANCELLED
        assert not booking.cancellationReason
        assert exc.value.errors["booking"] == [
            "Impossible d'annuler une réservation plus de 48h après l'avoir réservée"
            " et moins de 48h avant le début de l'événement"
        ]

    def test_raise_if_event_too_close_and_booked_long_ago(self):
        booking_date_too_long_ago_to_cancel_booking = datetime.utcnow() - timedelta(days=2, minutes=1)
        event_date_too_close_to_cancel_booking = datetime.utcnow() + timedelta(days=1)
        booking = booking_factories.IndividualBookingFactory(
            stock__beginningDatetime=event_date_too_close_to_cancel_booking,
            dateCreated=booking_date_too_long_ago_to_cancel_booking,
        )
        with pytest.raises(exceptions.CannotCancelConfirmedBooking) as exc:
            api.cancel_booking_by_beneficiary(booking.individualBooking.user, booking)
        assert booking.status is not BookingStatus.CANCELLED
        assert not booking.cancellationReason
        assert exc.value.errors["booking"] == [
            "Impossible d'annuler une réservation plus de 48h après l'avoir "
            "réservée et moins de 48h avant le début de l'événement"
        ]

    def test_raise_if_trying_to_cancel_someone_else_s_booking(self):
        booking = booking_factories.IndividualBookingFactory()
        other_beneficiary = users_factories.BeneficiaryGrant18Factory()
        with pytest.raises(exceptions.BookingDoesntExist):
            api.cancel_booking_by_beneficiary(other_beneficiary, booking)
        assert booking.status is not BookingStatus.CANCELLED
        assert not booking.cancellationReason

    @patch("pcapi.core.bookings.api.booking_providers_api.cancel_booking")
    @override_features(ENABLE_CDS_IMPLEMENTATION=True)
    def test_cancel_external_booking(self, mocked_cancel_booking):
        mocked_cancel_booking.return_value = None

        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        venue_provider = VenueBookingProviderFactory()
        offer_solo = offers_factories.EventOfferFactory(
            name="Séance ciné solo", venue=venue_provider.venue, subcategoryId=subcategories.SEANCE_CINE.id
        )
        stock_solo = offers_factories.EventStockFactory(offer=offer_solo, idAtProviders="1111")
        booking = booking_factories.IndividualBookingFactory(stock=stock_solo, individualBooking__user=beneficiary)
        ExternalBookingFactory(booking=booking)
        api._cancel_booking(booking, BookingCancellationReasons.BENEFICIARY)

        mocked_cancel_booking.assert_called()


@pytest.mark.usefixtures("db_session")
class CancelByOffererTest:
    def test_cancel(self):
        booking = booking_factories.IndividualBookingFactory()

        api.cancel_booking_by_offerer(booking)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

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
            "user_ids": [booking.individualBooking.userId],
        }

    def test_raise_if_already_cancelled(self):
        booking = booking_factories.CancelledIndividualBookingFactory(
            cancellationReason=BookingCancellationReasons.BENEFICIARY
        )
        with pytest.raises(exceptions.BookingIsAlreadyCancelled):
            api.cancel_booking_by_offerer(booking)
        assert booking.status is BookingStatus.CANCELLED
        assert booking.cancellationReason == BookingCancellationReasons.BENEFICIARY  # unchanged

        assert not push_testing.requests

    def test_raise_if_already_used(self):
        booking = booking_factories.UsedIndividualBookingFactory()
        with pytest.raises(exceptions.BookingIsAlreadyRefunded):
            api.cancel_booking_by_offerer(booking)
        assert booking.status is BookingStatus.USED
        assert not booking.cancellationReason

        assert not push_testing.requests

    def test_cancel_all_bookings_from_stock(self, app):
        stock = offers_factories.StockFactory(dnBookedQuantity=1)
        booking_1 = booking_factories.IndividualBookingFactory(stock=stock)
        booking_2 = booking_factories.IndividualBookingFactory(stock=stock)
        used_booking = booking_factories.UsedIndividualBookingFactory(stock=stock)
        cancelled_booking = booking_factories.CancelledIndividualBookingFactory(stock=stock)

        api.cancel_bookings_from_stock_by_offerer(stock)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

        assert models.Booking.query.filter().count() == 4
        assert models.Booking.query.filter(models.Booking.status == BookingStatus.CANCELLED).count() == 3
        assert models.Booking.query.filter(models.Booking.is_used_or_reimbursed.is_(True)).count() == 1
        assert booking_1.status is BookingStatus.CANCELLED
        assert booking_1.cancellationReason == BookingCancellationReasons.OFFERER
        assert booking_2.status is BookingStatus.CANCELLED
        assert booking_2.cancellationReason == BookingCancellationReasons.OFFERER
        assert used_booking.status is not BookingStatus.CANCELLED
        assert not used_booking.cancellationReason
        assert cancelled_booking.status is BookingStatus.CANCELLED
        assert cancelled_booking.cancellationReason == BookingCancellationReasons.BENEFICIARY

    def test_send_email_when_cancelled_by_offerer(self):
        # when
        booking = booking_factories.IndividualBookingFactory(stock__offer__bookingEmail="test@sent")

        api.cancel_booking_by_offerer(booking)

        # then
        assert len(mails_testing.outbox) == 2
        assert mails_testing.outbox[0].sent_data["To"] == booking.email
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.BOOKING_CANCELLATION_BY_PRO_TO_BENEFICIARY.value
        )
        assert mails_testing.outbox[1].sent_data["To"] == "test@sent"
        assert "Confirmation de votre annulation de réservation " in mails_testing.outbox[1].sent_data["subject"]


@pytest.mark.usefixtures("db_session")
class CancelForFraudTest:
    def test_cancel(self):
        booking = booking_factories.IndividualBookingFactory()

        api.cancel_booking_for_fraud(booking)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

        assert booking.status is BookingStatus.CANCELLED
        assert booking.cancellationReason == BookingCancellationReasons.FRAUD


@pytest.mark.usefixtures("db_session")
class MarkAsUsedTest:
    def test_mark_as_used(self):
        booking = booking_factories.IndividualBookingFactory()
        api.mark_as_used(booking)
        assert booking.status is BookingStatus.USED
        assert len(push_testing.requests) == 2

    @freeze_time("2021-09-08")
    def test_mark_as_used_with_uncancel(self):
        booking = booking_factories.CancelledIndividualBookingFactory()
        api.mark_as_used_with_uncancelling(booking)
        assert booking.status is BookingStatus.USED
        assert booking.dateUsed == datetime.utcnow()
        assert not booking.cancellationReason

    def test_mark_as_used_when_stock_starts_soon(self):
        booking = booking_factories.IndividualBookingFactory(
            stock__beginningDatetime=datetime.utcnow() + timedelta(days=1)
        )
        api.mark_as_used(booking)
        assert booking.status is BookingStatus.USED

    def test_raise_if_already_used(self):
        booking = booking_factories.UsedIndividualBookingFactory()
        with pytest.raises(exceptions.BookingIsAlreadyUsed):
            api.mark_as_used(booking)

    def test_raise_if_cancelled(self):
        booking = booking_factories.CancelledIndividualBookingFactory()
        with pytest.raises(exceptions.BookingIsAlreadyCancelled):
            api.mark_as_used(booking)
        assert booking.status is not BookingStatus.USED

    def test_raise_if_already_reimbursed(self):
        booking = booking_factories.UsedIndividualBookingFactory()
        finance_factories.PaymentFactory(booking=booking)
        with pytest.raises(exceptions.BookingIsAlreadyRefunded):
            api.mark_as_used(booking)

    def test_raise_if_too_soon_to_mark_as_used(self):
        booking = booking_factories.IndividualBookingFactory(
            stock__beginningDatetime=datetime.utcnow() + timedelta(days=4)
        )
        with pytest.raises(exceptions.BookingIsNotConfirmed):
            api.mark_as_used(booking)
        assert booking.status is not BookingStatus.USED


@pytest.mark.usefixtures("db_session")
class MarkAsUnusedTest:
    def test_mark_as_unused(self):
        booking = booking_factories.UsedIndividualBookingFactory()
        api.mark_as_unused(booking)
        assert booking.status is not BookingStatus.USED
        assert len(push_testing.requests) == 2

    def test_mark_as_unused_digital_offer(self):
        offer = offers_factories.OfferFactory(product=offers_factories.DigitalProductFactory())
        booking = booking_factories.UsedIndividualBookingFactory(stock__offer=offer)
        api.mark_as_unused(booking)
        assert booking.status is not BookingStatus.USED

    def test_raise_if_not_yet_used(self):
        booking = booking_factories.IndividualBookingFactory()
        with pytest.raises(api_errors.ResourceGoneError):
            api.mark_as_unused(booking)
        assert booking.status is not BookingStatus.USED

    def test_raise_if_has_reimbursement(self):
        booking = booking_factories.UsedIndividualBookingFactory()
        finance_factories.PricingFactory(booking=booking, status=finance_models.PricingStatus.PROCESSED)
        with pytest.raises(api_errors.ResourceGoneError):
            api.mark_as_unused(booking)
        assert booking.status is BookingStatus.USED

    def test_raise_if_has_reimbursement_legacy_payment(self):
        booking = booking_factories.UsedIndividualBookingFactory()
        finance_factories.PaymentFactory(booking=booking)
        with pytest.raises(api_errors.ResourceGoneError):
            api.mark_as_unused(booking)
        assert booking.status is BookingStatus.USED

    def test_raise_if_booking_was_automatically_used_for_digital_offer_with_activation_code(self):
        offer = offers_factories.OfferFactory(product=offers_factories.DigitalProductFactory())
        digital_stock = offers_factories.StockWithActivationCodesFactory()
        first_activation_code = digital_stock.activationCodes[0]
        booking = booking_factories.UsedIndividualBookingFactory(
            stock__offer=offer, activationCode=first_activation_code
        )
        with pytest.raises(api_errors.ForbiddenError):
            api.mark_as_unused(booking)
        assert booking.status is BookingStatus.USED


@pytest.mark.parametrize(
    "booking_date",
    [datetime(2020, 7, 14, 15, 30), datetime(2020, 10, 25, 1, 45), datetime.utcnow()],
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
        recent_booking = booking_factories.IndividualBookingFactory(
            stock__beginningDatetime=datetime.utcnow() + timedelta(days=90)
        )
        old_booking = booking_factories.IndividualBookingFactory(
            stock=recent_booking.stock, dateCreated=(datetime.utcnow() - timedelta(days=7))
        )
        # When
        updated_bookings = api.update_cancellation_limit_dates(
            bookings_to_update=[recent_booking, old_booking],
            new_beginning_datetime=datetime.utcnow() + timedelta(days=1),
        )
        # Then
        assert updated_bookings == [recent_booking, old_booking]
        assert recent_booking.cancellationLimitDate == old_booking.cancellationLimitDate == datetime(2020, 11, 17, 15)

    def should_update_bookings_cancellation_limit_dates_for_event_beginning_in_three_days(self):
        #  Given
        recent_booking = booking_factories.IndividualBookingFactory(
            stock__beginningDatetime=datetime.utcnow() + timedelta(days=90)
        )
        old_booking = booking_factories.IndividualBookingFactory(
            stock=recent_booking.stock, dateCreated=(datetime.utcnow() - timedelta(days=7))
        )
        # When
        updated_bookings = api.update_cancellation_limit_dates(
            bookings_to_update=[recent_booking, old_booking],
            new_beginning_datetime=datetime.utcnow() + timedelta(days=3),
        )
        # Then
        assert updated_bookings == [recent_booking, old_booking]
        assert recent_booking.cancellationLimitDate == old_booking.cancellationLimitDate == datetime(2020, 11, 18, 15)

    def should_update_bookings_cancellation_limit_dates_for_event_beginning_in_a_week(self):
        #  Given
        recent_booking = booking_factories.IndividualBookingFactory(
            stock__beginningDatetime=datetime.utcnow() + timedelta(days=90)
        )
        old_booking = booking_factories.IndividualBookingFactory(
            stock=recent_booking.stock, dateCreated=(datetime.utcnow() - timedelta(days=7))
        )
        # When
        updated_bookings = api.update_cancellation_limit_dates(
            bookings_to_update=[recent_booking, old_booking],
            new_beginning_datetime=datetime.utcnow() + timedelta(days=7),
        )
        # Then
        assert updated_bookings == [recent_booking, old_booking]
        assert recent_booking.cancellationLimitDate == old_booking.cancellationLimitDate == datetime(2020, 11, 19, 15)


@pytest.mark.usefixtures("db_session")
class AutoMarkAsUsedAfterEventTest:
    def test_do_not_update_if_thing_product(self):
        booking_factories.IndividualBookingFactory(stock=offers_factories.ThingStockFactory())

        api.auto_mark_as_used_after_event()

        booking = Booking.query.first()
        assert booking.status is not BookingStatus.USED
        assert not booking.dateUsed

    @freeze_time("2021-01-01")
    def test_update_booking_used_when_event_date_is_3_days_before(self):
        event_date = datetime.utcnow() - timedelta(days=3)
        booking_factories.IndividualBookingFactory(stock__beginningDatetime=event_date)

        api.auto_mark_as_used_after_event()

        booking = Booking.query.first()
        assert booking.status is BookingStatus.USED
        assert booking.dateUsed == datetime(2021, 1, 1)

    @freeze_time("2021-01-01")
    def test_does_not_update_when_event_date_is_only_1_day_before(self):
        event_date = datetime.utcnow() - timedelta(days=1)
        booking_factories.IndividualBookingFactory(stock__beginningDatetime=event_date)

        api.auto_mark_as_used_after_event()

        booking = Booking.query.first()
        assert booking.status is not BookingStatus.USED
        assert booking.dateUsed is None

    @freeze_time("2021-01-01")
    def test_does_not_update_booking_if_already_used(self):
        event_date = datetime.utcnow() - timedelta(days=3)
        booking = booking_factories.UsedIndividualBookingFactory(stock__beginningDatetime=event_date)
        initial_date_used = booking.dateUsed

        api.auto_mark_as_used_after_event()

        booking = Booking.query.first()
        assert booking.status is BookingStatus.USED
        assert booking.dateUsed == initial_date_used

    @freeze_time("2021-01-01")
    def test_does_not_update_booking_if_cancelled(self):
        event_date = datetime.utcnow() - timedelta(days=3)
        booking = booking_factories.CancelledIndividualBookingFactory(stock__beginningDatetime=event_date)

        api.auto_mark_as_used_after_event()

        booking = Booking.query.first()
        assert booking.status is BookingStatus.CANCELLED

    def test_update_external_booking_if_not_used(self):
        event_date = datetime.utcnow() - timedelta(days=3)
        ExternalBookingFactory(
            booking__stock__beginningDatetime=event_date,
        )
        api.auto_mark_as_used_after_event()

        validated_external_booking = Booking.query.first()
        assert validated_external_booking.status is BookingStatus.USED

    def test_update_educational_booking_if_not_used(self):
        event_date = datetime.utcnow() - timedelta(days=3)
        booking_factories.EducationalBookingFactory(
            stock__beginningDatetime=event_date,
        )

        api.auto_mark_as_used_after_event()

        validated_educational_booking = Booking.query.first()
        assert validated_educational_booking.status is BookingStatus.USED

    def test_does_not_update_educational_booking_if_not_used_and_refused_by_principal(self):
        event_date = datetime.utcnow() - timedelta(days=3)
        booking_factories.EducationalBookingFactory(
            stock__beginningDatetime=event_date,
            educationalBooking__status=EducationalBookingStatus.REFUSED,
        )

        api.auto_mark_as_used_after_event()

        validated_educational_booking = Booking.query.first()
        assert validated_educational_booking.status is not BookingStatus.USED

    def test_update_educational_booking_if_not_used_and_not_validated_by_principal_yet(self):
        event_date = datetime.utcnow() - timedelta(days=3)
        booking_factories.EducationalBookingFactory(
            stock__beginningDatetime=event_date,
            educationalBooking__status=None,
        )

        api.auto_mark_as_used_after_event()

        non_validated_by_ce_educational_booking = Booking.query.first()
        assert non_validated_by_ce_educational_booking.status is BookingStatus.USED

    @freeze_time("2021-01-01")
    def test_update_collective_booking_when_not_used_and_event_date_is_3_days_before(self):
        event_date = datetime.utcnow() - timedelta(days=3)
        educational_factories.CollectiveBookingFactory(collectiveStock__beginningDatetime=event_date)

        api.auto_mark_as_used_after_event()

        collectiveBooking = CollectiveBooking.query.first()
        assert collectiveBooking.status is CollectiveBookingStatus.USED
        assert collectiveBooking.dateUsed == datetime(2021, 1, 1)

    @freeze_time("2021-01-01")
    def test_does_not_update_collective_booking_when_event_date_is_only_1_day_before(self):
        event_date = datetime.utcnow() - timedelta(days=1)
        educational_factories.CollectiveBookingFactory(collectiveStock__beginningDatetime=event_date)

        api.auto_mark_as_used_after_event()

        collectiveBooking = CollectiveBooking.query.first()
        assert collectiveBooking.status is not CollectiveBookingStatus.USED
        assert collectiveBooking.dateUsed is None

    @freeze_time("2021-01-01")
    def test_does_not_update_collective_booking_when_cancelled(self):
        event_date = datetime.utcnow() - timedelta(days=3)
        educational_factories.CollectiveBookingFactory(
            collectiveStock__beginningDatetime=event_date, status=CollectiveBookingStatus.CANCELLED
        )

        api.auto_mark_as_used_after_event()

        collectiveBooking = CollectiveBooking.query.first()
        assert collectiveBooking.status is CollectiveBookingStatus.CANCELLED
        assert collectiveBooking.dateUsed is None

    @pytest.mark.usefixtures("db_session")
    @override_features(UPDATE_BOOKING_USED=False)
    def test_raise_if_feature_flag_is_deactivated(self):
        with pytest.raises(ValueError):
            api.auto_mark_as_used_after_event()


@pytest.mark.usefixtures("db_session")
class GetInvidualBookingsFromStockTest:
    def test_has_bookings(self):
        stock = offers_factories.StockFactory()
        bookings = booking_factories.IndividualBookingFactory.create_batch(2, stock=stock)

        found_bookings = list(api.get_individual_bookings_from_stock(stock.id))

        found_booking_ids = {booking.id for booking in found_bookings}
        expected_booking_ids = {booking.id for booking in bookings}

        assert len(found_bookings) == len(bookings)
        assert found_booking_ids == expected_booking_ids

    def test_has_cancelled_bookings(self):
        stock = offers_factories.StockFactory()

        booking = booking_factories.IndividualBookingFactory(stock=stock)
        booking_factories.IndividualBookingFactory(stock=stock, status=BookingStatus.CANCELLED)

        found_bookings = list(api.get_individual_bookings_from_stock(stock.id))

        found_booking_ids = {b.id for b in found_bookings}
        expected_booking_ids = {booking.id}

        assert found_booking_ids == expected_booking_ids

    def test_has_no_bookings(self):
        stock = offers_factories.StockFactory()
        assert not list(api.get_individual_bookings_from_stock(stock.id))
