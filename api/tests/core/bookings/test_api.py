import dataclasses
from datetime import datetime
from datetime import timedelta
import json
import logging
import re
from unittest import mock
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
import sqlalchemy.exc
from sqlalchemy.sql import text

from pcapi.analytics.amplitude.backends.amplitude_connector import AmplitudeEventType
import pcapi.analytics.amplitude.testing as amplitude_testing
from pcapi.connectors.ems import EMSBookingConnector
from pcapi.core import search
from pcapi.core.bookings import api
from pcapi.core.bookings import exceptions
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models
from pcapi.core.bookings.api import cancel_unstored_external_bookings
from pcapi.core.bookings.constants import RedisExternalBookingType
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.educational.factories as educational_factories
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.external.batch import BATCH_DATETIME_FORMAT
from pcapi.core.external_bookings import factories as external_bookings_factories
from pcapi.core.external_bookings.ems import constants
import pcapi.core.external_bookings.exceptions as external_bookings_exceptions
from pcapi.core.external_bookings.factories import ExternalBookingFactory
from pcapi.core.external_bookings.models import Ticket
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerer_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
from pcapi.models import db
from pcapi.models import feature
import pcapi.notifications.push.testing as push_testing
from pcapi.tasks.serialization.external_api_booking_notification_tasks import BookingAction
from pcapi.utils import queue
from pcapi.utils.requests import exceptions as requests_exception

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
            connection.execute(
                text("""SELECT * FROM stock WHERE stock.id = :stock_id FOR UPDATE"""), {"stock_id": stock.id}
            )

            with pytest.raises(sqlalchemy.exc.OperationalError):
                api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

        with engine.connect() as connection:
            connection.execute(
                text("""SELECT * FROM "user" WHERE id = :user_id FOR UPDATE"""), {"user_id": beneficiary.id}
            )

            with pytest.raises(sqlalchemy.exc.OperationalError):
                api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

        assert models.Booking.query.count() == 0
        assert offers_models.Stock.query.filter_by(id=stock.id, dnBookedQuantity=5).count() == 1

    @clean_database
    def test_cancel_booking(self, app):
        booking = bookings_factories.BookingFactory(stock__dnBookedQuantity=1)

        # open a second connection on purpose and lock the stock
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        with engine.connect() as connection:
            connection.execute(
                text("""SELECT * FROM stock WHERE stock.id = :stock_id FOR UPDATE"""), {"stock_id": booking.stockId}
            )

            with pytest.raises(sqlalchemy.exc.OperationalError):
                api.cancel_booking_by_beneficiary(booking.user, booking)

        assert models.Booking.query.filter().count() == 1
        assert models.Booking.query.filter(models.Booking.status == BookingStatus.CANCELLED).count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_cancel_booking_with_concurrent_cancel(self, app):
        booking = bookings_factories.BookingFactory(stock__dnBookedQuantity=1)
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
        bookings_factories.BookingFactory(stock=stock)
        bookings_factories.BookingFactory(stock=stock)
        bookings_factories.UsedBookingFactory(stock=stock)
        bookings_factories.CancelledBookingFactory(stock=stock)

        # open a second connection on purpose and lock the stock
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        with engine.connect() as connection:
            connection.execute(
                text("""SELECT * FROM stock WHERE stock.id = :stock_id FOR UPDATE"""), {"stock_id": stock.id}
            )

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
        bookings_factories.BookingFactory(stock=stock)

        booking = api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

        # One request should have been sent to Batch to trigger the event
        # HAS_BOOKED_OFFER, and another one with the user's
        # updated attributes (iOS + Android)
        assert len(push_testing.requests) == 3

        data = push_testing.requests[1]
        assert data["attribute_values"]["u.credit"] == 29_000  # values in cents
        assert data["attribute_values"]["ut.booking_categories"] == ["FILM"]

        expected_date = booking.dateCreated.strftime(BATCH_DATETIME_FORMAT)
        assert data["attribute_values"]["date(u.last_booking_date)"] == expected_date

        expected_date = booking.dateCreated.strftime(BATCH_DATETIME_FORMAT)
        assert data["attribute_values"]["date(u.last_booking_date)"] == expected_date

        assert booking.quantity == 1
        assert booking.userId == beneficiary.id
        assert booking.depositId == beneficiary.deposit.id
        assert booking.amount == 10
        assert booking.stock == stock
        assert len(booking.token) == 6
        assert booking.status is BookingStatus.CONFIRMED
        assert booking.cancellationLimitDate is None
        assert booking.priceCategoryLabel is None
        assert stock.dnBookedQuantity == 7

        mocked_async_index_offer_ids.assert_called_once_with(
            [stock.offer.id],
            reason=search.IndexationReason.BOOKING_CREATION,
        )

        assert len(mails_testing.outbox) == 2
        email_data1 = mails_testing.outbox[0]
        assert email_data1["template"] == dataclasses.asdict(TransactionalEmail.NEW_BOOKING_TO_PRO.value)  # to offerer
        email_data2 = mails_testing.outbox[1]
        assert email_data2["template"] == dataclasses.asdict(
            TransactionalEmail.BOOKING_CONFIRMATION_BY_BENEFICIARY.value
        )  # to beneficiary

    def test_if_it_is_first_venue_booking_to_send_specific_email(self):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        stock = offers_factories.StockFactory(price=10, dnBookedQuantity=5, offer__bookingEmail="offerer@example.com")

        api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)
        assert len(mails_testing.outbox) == 2
        email_data1 = mails_testing.outbox[0]
        assert email_data1["template"] == dataclasses.asdict(
            TransactionalEmail.FIRST_VENUE_BOOKING_TO_PRO.value
        )  # to offerer
        email_data2 = mails_testing.outbox[1]
        assert email_data2["template"] == dataclasses.asdict(
            TransactionalEmail.BOOKING_CONFIRMATION_BY_BENEFICIARY.value
        )  # to beneficiary

    def test_free_offer_booking_by_ex_beneficiary(self):
        ex_beneficiary = users_factories.BeneficiaryGrant18Factory(
            deposit__expirationDate=datetime.utcnow() - timedelta(days=1000)  # ~ 2 years and a half
        )
        stock = offers_factories.StockFactory(price=0, dnBookedQuantity=5, offer__bookingEmail="offerer@example.com")

        booking = api.book_offer(beneficiary=ex_beneficiary, stock_id=stock.id, quantity=1)

        assert not booking.deposit

    def test_booked_categories_are_sent_to_batch_backend(self, app):
        offer1 = offers_factories.OfferFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id)
        offer2 = offers_factories.OfferFactory(subcategoryId=subcategories.CARTE_CINE_ILLIMITE.id)

        offers_factories.OfferFactory(subcategoryId=subcategories.ACHAT_INSTRUMENT.id)

        stock1 = offers_factories.StockFactory(price=10, dnBookedQuantity=5, offer=offer1)
        stock2 = offers_factories.StockFactory(price=10, dnBookedQuantity=5, offer=offer2)

        beneficiary = users_factories.BeneficiaryGrant18Factory()
        date_created = datetime.utcnow() - timedelta(days=5)
        bookings_factories.BookingFactory.create_batch(3, user=beneficiary, dateCreated=date_created, stock=stock2)

        booking = api.book_offer(beneficiary=beneficiary, stock_id=stock1.id, quantity=1)

        # One request should have been sent to Batch to trigger the event
        # HAS_BOOKED_OFFER, and another one with the user's
        # updated attributes (iOS + Android)
        assert len(push_testing.requests) == 3

        data = push_testing.requests[1]
        expected_date = booking.dateCreated.strftime(BATCH_DATETIME_FORMAT)
        assert data["attribute_values"]["date(u.last_booking_date)"] == expected_date

        expected_categories = ["CINEMA", "FILM"]
        assert sorted(data["attribute_values"]["ut.booking_categories"]) == expected_categories

    def test_booking_on_digital_offer_with_activation_stock(self):
        stock = offers_factories.StockWithActivationCodesFactory(price=10, dnBookedQuantity=3)
        beneficiary = users_factories.BeneficiaryGrant18Factory()

        booking = api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

        assert booking.status is BookingStatus.USED
        assert booking.validationAuthorType == models.BookingValidationAuthorType.AUTO
        event = finance_models.FinanceEvent.query.filter_by(booking=booking).one()
        assert event.motive == finance_models.FinanceEventMotive.BOOKING_USED

    def test_booking_on_digital_offer_without_activation_stock(self):
        offer = offers_factories.DigitalOfferFactory()
        stock = offers_factories.StockFactory(price=10, dnBookedQuantity=5, offer=offer)
        beneficiary = users_factories.BeneficiaryGrant18Factory()

        booking = api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

        assert booking.status is not BookingStatus.USED
        event = finance_models.FinanceEvent.query.filter_by(booking=booking).first()
        assert event is None

    def test_create_event_booking(self):
        ten_days_from_now = datetime.utcnow() + timedelta(days=10)
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        stock = offers_factories.EventStockFactory(price=10, beginningDatetime=ten_days_from_now, dnBookedQuantity=5)

        booking = api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

        # One request should have been sent to Batch to trigger the event
        # HAS_BOOKED_OFFER, and another one with the user's
        # updated attributes (iOS + Android)
        assert len(push_testing.requests) == 3

        data = push_testing.requests[1]
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
        assert booking.priceCategoryLabel == "Tarif unique"

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
        booking = bookings_factories.BookingFactory(stock__quantity=1)
        with pytest.raises(exceptions.StockIsNotBookable):
            api.book_offer(
                beneficiary=users_factories.BeneficiaryGrant18Factory(),
                stock_id=booking.stock.id,
                quantity=1,
            )

    def test_raise_if_user_has_already_booked(self):
        booking = bookings_factories.BookingFactory()
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

    def test_logs_event_to_amplitude_and_batch(self):
        # Given
        stock = offers_factories.StockFactory(price=10)
        beneficiary = users_factories.BeneficiaryGrant18Factory()

        # When
        api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

        # Then
        assert len(amplitude_testing.requests) == 1
        assert amplitude_testing.requests[0] == {
            "event_name": AmplitudeEventType.OFFER_BOOKED.value,
            "event_properties": {
                "booking_id": stock.bookings[0].id,
                "category": "FILM",
                "offer_id": stock.offer.id,
                "price": 10.00,
                "subcategory": "SUPPORT_PHYSIQUE_FILM",
            },
            "user_id": beneficiary.id,
        }
        assert push_testing.requests[0] == {
            "can_be_asynchronously_retried": True,
            "event_name": "has_booked_offer",
            "event_payload": {
                "offer_category": "FILM",
                "offer_id": stock.offer.id,
                "offer_name": stock.offer.name,
                "offer_subcategory": "SUPPORT_PHYSIQUE_FILM",
                "offer_type": "solo",
                "stock": 999,
            },
            "user_id": beneficiary.id,
        }

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
            booking = bookings_factories.UsedBookingFactory(token="ABCDEF")
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
            booking = bookings_factories.UsedBookingFactory(token="ABCDEF")
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

    class WithExternalBookingApiTest:
        @patch("pcapi.core.bookings.api.external_bookings_api.book_cinema_ticket")
        @override_features(ENABLE_EMS_INTEGRATION=True)
        def test_ems_solo_external_booking(self, mocked_book_ticket):
            mocked_book_ticket.return_value = [
                Ticket(
                    barcode="111",
                    seat_number="",
                    additional_information={
                        "num_cine": "9997",
                        "num_caisse": "255",
                        "num_trans": 1257,
                        "num_ope": 147149,
                    },
                )
            ]

            beneficiary = users_factories.BeneficiaryGrant18Factory()
            ems_provider = get_provider_by_local_class("EMSStocks")
            venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider)
            cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)
            offer = offers_factories.EventOfferFactory(
                name="Film",
                venue=venue_provider.venue,
                subcategoryId=subcategories.SEANCE_CINE.id,
                lastProviderId=cinema_provider_pivot.provider.id,
            )
            stock = offers_factories.EventStockFactory(offer=offer, idAtProviders="1111%2222%EMS#3333")

            booking = api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

            assert len(booking.externalBookings) == 1
            assert booking.externalBookings[0].barcode == "111"
            assert booking.externalBookings[0].seat == ""
            assert booking.externalBookings[0].additional_information == {
                "num_cine": "9997",
                "num_caisse": "255",
                "num_trans": 1257,
                "num_ope": 147149,
            }

        @patch("pcapi.core.bookings.api.external_bookings_api.book_cinema_ticket")
        @override_features(ENABLE_EMS_INTEGRATION=True)
        def test_ems_duo_external_booking(self, mocked_book_ticket):
            mocked_book_ticket.return_value = [
                Ticket(
                    barcode="111",
                    seat_number="",
                    additional_information={
                        "num_cine": "9997",
                        "num_caisse": "255",
                        "num_trans": 1257,
                        "num_ope": 147149,
                    },
                ),
                Ticket(
                    barcode="222",
                    seat_number="",
                    additional_information={
                        "num_cine": "9997",
                        "num_caisse": "255",
                        "num_trans": 1258,
                        "num_ope": 147150,
                    },
                ),
            ]

            beneficiary = users_factories.BeneficiaryGrant18Factory()
            ems_provider = get_provider_by_local_class("EMSStocks")
            venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider)
            cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)
            offer = offers_factories.EventOfferFactory(
                name="Film",
                venue=venue_provider.venue,
                subcategoryId=subcategories.SEANCE_CINE.id,
                lastProviderId=cinema_provider_pivot.provider.id,
                isDuo=True,
            )
            stock = offers_factories.EventStockFactory(offer=offer, idAtProviders="1111%2222%EMS#3333")

            booking = api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=2)

            assert len(booking.externalBookings) == 2
            assert booking.externalBookings[0].barcode == "111"
            assert booking.externalBookings[0].seat == ""
            assert booking.externalBookings[0].additional_information == {
                "num_cine": "9997",
                "num_caisse": "255",
                "num_trans": 1257,
                "num_ope": 147149,
            }
            assert booking.externalBookings[1].barcode == "222"
            assert booking.externalBookings[1].seat == ""
            assert booking.externalBookings[1].additional_information == {
                "num_cine": "9997",
                "num_caisse": "255",
                "num_trans": 1258,
                "num_ope": 147150,
            }

        @patch("flask.current_app.redis_client.llen")
        @patch("pcapi.core.external_bookings.ems.client.current_app.redis_client.lpush")
        @patch("pcapi.core.external_bookings.ems.client.current_app.redis_client.rpop")
        @patch("pcapi.core.bookings.api.generate_booking_token")
        @patch("pcapi.core.external_bookings.ems.client.EMSClientAPI.cancel_booking_with_tickets")
        @override_features(ENABLE_EMS_INTEGRATION=True, EMS_CANCEL_PENDING_EXTERNAL_BOOKING=True)
        @pytest.mark.parametrize("exception", [requests_exception.Timeout, requests_exception.ReadTimeout])
        def test_timeout_during_ems_external_booking_trigger_a_cancel_call(
            self,
            mock_cancel_booking,
            mock_generate_booking_token,
            mock_rpop,
            mock_lpush,
            mock_llen,
            exception,
            requests_mock,
        ):
            token = "AAAAAA"
            mock_generate_booking_token.return_value = token

            beneficiary = users_factories.BeneficiaryGrant18Factory()
            ems_provider = get_provider_by_local_class("EMSStocks")
            venue_provider = providers_factories.VenueProviderFactory(
                provider=ems_provider, venueIdAtOfferProvider="9997"
            )
            cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)
            offer = offers_factories.EventOfferFactory(
                name="Film",
                venue=venue_provider.venue,
                subcategoryId=subcategories.SEANCE_CINE.id,
                lastProviderId=cinema_provider_pivot.provider.id,
            )
            stock = offers_factories.EventStockFactory(offer=offer, idAtProviders="1111%2222%EMS#3333")

            payload = {
                "num_cine": venue_provider.venueIdAtOfferProvider,
                "id_seance": stock.idAtProviders.split("#")[-1],
                "qte_place": 1,
                "pass_culture_price": float(stock.price),
                "total_price": float(stock.price),
                "email": beneficiary.email,
                "num_pass_culture": str(beneficiary.id),
                "num_cmde": token,
            }
            url = EMSBookingConnector()._build_url("VENTE", payload)
            booking_adapter = requests_mock.post(url=re.compile(rf"{url}"), exc=exception)

            with pytest.raises(external_bookings_exceptions.ExternalBookingException):
                api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

            assert not Booking.query.all()
            assert booking_adapter.call_count == 1
            assert mock_lpush.call_count == 1
            assert mock_lpush.mock_calls[0].args[0] == constants.EMS_EXTERNAL_BOOKINGS_TO_CANCEL
            booking_queued = json.loads(mock_lpush.mock_calls[0].args[1])
            assert booking_queued["cinema_id"] == venue_provider.venueIdAtOfferProvider
            assert booking_queued["token"] == token
            timestamp = booking_queued["timestamp"]
            assert timestamp == pytest.approx(datetime.utcnow().timestamp())

            mock_llen.side_effect = [1, 0]
            mock_rpop.return_value = json.dumps(
                {
                    "cinema_id": venue_provider.venueIdAtOfferProvider,
                    "token": token,
                    # Mocking an older booking, otherwise tests runs too fast
                    "timestamp": (datetime.utcnow() - timedelta(seconds=180)).timestamp(),
                }
            )

            # Few minutes later, a cron trigger our task
            # First we should check that the external booking has been successfully created
            # Otherwise, there's nothing to cancel
            payload = {"num_cine": venue_provider.venueIdAtOfferProvider, "num_cmde": token}
            url = EMSBookingConnector()._build_url("STATUT", payload)
            get_tickets_adapter = requests_mock.post(
                url=re.compile(rf"{url}"),
                json={
                    "statut": 1,
                    "num_cine": "9997",
                    "id_seance": "999700078774",
                    "qte_place": 1,
                    "pass_culture_price": 5.15,
                    "total_price": 5.15,
                    "email": "email@email.fr",
                    "num_pass_culture": "",
                    "num_cmde": "",
                    "billets": [
                        {
                            "num_caisse": "255",
                            "code_barre": "000000139863",
                            "num_trans": 475,
                            "num_ope": 139863,
                            "code_tarif": "0RG",
                            "num_serie": 5,
                            "montant": 5.15,
                            "num_place": "",
                        }
                    ],
                },
            )

            api.cancel_ems_external_bookings()

            assert get_tickets_adapter.call_count == 1
            assert mock_rpop.call_count == 1
            assert mock_cancel_booking.call_count == 1
            assert not Booking.query.all()

        @patch("flask.current_app.redis_client.llen")
        @patch("flask.current_app.redis_client.rpush")
        @patch("flask.current_app.redis_client.lpush")
        @patch("pcapi.core.external_bookings.ems.client.current_app.redis_client.rpop")
        @patch("pcapi.core.bookings.api.generate_booking_token")
        @patch("pcapi.core.external_bookings.ems.client.EMSClientAPI.cancel_booking_with_tickets")
        @override_features(ENABLE_EMS_INTEGRATION=True, EMS_CANCEL_PENDING_EXTERNAL_BOOKING=True)
        @pytest.mark.parametrize("exception", [requests_exception.Timeout, requests_exception.ReadTimeout])
        def test_we_dont_cancel_too_early_failing_booking(
            self,
            mock_cancel_booking,
            mock_generate_booking_token,
            mock_rpop,
            mock_lpush,
            mock_rpush,
            mock_llen,
            exception,
            requests_mock,
        ):
            token = "AAAAAA"
            mock_generate_booking_token.return_value = token

            beneficiary = users_factories.BeneficiaryGrant18Factory()
            ems_provider = get_provider_by_local_class("EMSStocks")
            venue_provider = providers_factories.VenueProviderFactory(
                provider=ems_provider, venueIdAtOfferProvider="9997"
            )
            cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)
            offer = offers_factories.EventOfferFactory(
                name="Film",
                venue=venue_provider.venue,
                subcategoryId=subcategories.SEANCE_CINE.id,
                lastProviderId=cinema_provider_pivot.provider.id,
            )
            stock = offers_factories.EventStockFactory(offer=offer, idAtProviders="1111%2222%EMS#3333")

            payload = {
                "num_cine": venue_provider.venueIdAtOfferProvider,
                "id_seance": stock.idAtProviders.split("#")[-1],
                "qte_place": 1,
                "pass_culture_price": float(stock.price),
                "total_price": float(stock.price),
                "email": beneficiary.email,
                "num_pass_culture": str(beneficiary.id),
                "num_cmde": token,
            }
            url = EMSBookingConnector()._build_url("VENTE", payload)
            booking_adapter = requests_mock.post(url=re.compile(rf"{url}"), exc=exception)

            with pytest.raises(external_bookings_exceptions.ExternalBookingException):
                api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

            assert not Booking.query.all()
            assert booking_adapter.call_count == 1
            assert mock_lpush.call_count == 1
            assert mock_lpush.mock_calls[0].args[0] == constants.EMS_EXTERNAL_BOOKINGS_TO_CANCEL
            booking_queued = json.loads(mock_lpush.mock_calls[0].args[1])
            assert booking_queued["cinema_id"] == venue_provider.venueIdAtOfferProvider
            assert booking_queued["token"] == token
            timestamp = booking_queued["timestamp"]
            assert timestamp == pytest.approx(datetime.utcnow().timestamp())

            mock_llen.side_effect = [1, 0]
            mock_rpop.return_value = json.dumps(
                {
                    "cinema_id": venue_provider.venueIdAtOfferProvider,
                    "token": token,
                    "timestamp": timestamp,
                }
            )

            get_tickets_adapter = requests_mock.post(
                url=re.compile(r"https://fake_url.com/STATUT/*"),
            )

            api.cancel_ems_external_bookings()

            assert mock_rpop.call_count == 1
            assert mock_rpush.call_count == 1
            assert get_tickets_adapter.call_count == 0
            assert mock_cancel_booking.call_count == 0
            assert not Booking.query.all()

        @patch("flask.current_app.redis_client.llen")
        @patch("pcapi.core.external_bookings.ems.client.current_app.redis_client.lpush")
        @patch("pcapi.core.external_bookings.ems.client.current_app.redis_client.rpop")
        @patch("pcapi.core.bookings.api.generate_booking_token")
        @patch("pcapi.core.external_bookings.ems.client.EMSClientAPI.cancel_booking_with_tickets")
        @override_features(ENABLE_EMS_INTEGRATION=True, EMS_CANCEL_PENDING_EXTERNAL_BOOKING=False)
        @pytest.mark.parametrize("exception", [requests_exception.Timeout, requests_exception.ReadTimeout])
        def test_timeout_during_ems_external_booking_dont_do_anything_if_ff_deactivated(
            self,
            mock_cancel_booking,
            mock_generate_booking_token,
            mock_rpop,
            mock_lpush,
            mock_llen,
            exception,
            requests_mock,
        ):
            token = "AAAAAA"
            mock_generate_booking_token.return_value = token

            beneficiary = users_factories.BeneficiaryGrant18Factory()
            ems_provider = get_provider_by_local_class("EMSStocks")
            venue_provider = providers_factories.VenueProviderFactory(
                provider=ems_provider, venueIdAtOfferProvider="9997"
            )
            cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)
            offer = offers_factories.EventOfferFactory(
                name="Film",
                venue=venue_provider.venue,
                subcategoryId=subcategories.SEANCE_CINE.id,
                lastProviderId=cinema_provider_pivot.provider.id,
            )
            stock = offers_factories.EventStockFactory(offer=offer, idAtProviders="1111%2222%EMS#3333")

            payload = {
                "num_cine": venue_provider.venueIdAtOfferProvider,
                "id_seance": stock.idAtProviders.split("#")[-1],
                "qte_place": 1,
                "pass_culture_price": float(stock.price),
                "total_price": float(stock.price),
                "email": beneficiary.email,
                "num_pass_culture": str(beneficiary.id),
                "num_cmde": token,
            }
            url = EMSBookingConnector()._build_url("VENTE", payload)
            booking_adapter = requests_mock.post(url=re.compile(rf"{url}"), exc=exception)

            with pytest.raises(external_bookings_exceptions.ExternalBookingException):
                api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

            assert not Booking.query.all()
            assert booking_adapter.call_count == 1
            assert mock_lpush.call_count == 0

            mock_llen.return_value = 0

            # Few minutes later, a cron trigger our task
            # First we should check that the external booking has been successfully created
            # Otherwise, there's nothing to cancel
            api.cancel_ems_external_bookings()

            assert mock_rpop.call_count == 0
            assert mock_cancel_booking.call_count == 0
            assert not Booking.query.all()

        @patch("pcapi.core.bookings.api.external_bookings_api.book_cinema_ticket")
        @override_features(ENABLE_CDS_IMPLEMENTATION=True)
        def test_solo_external_booking(self, mocked_book_cinema_ticket):
            mocked_book_cinema_ticket.return_value = [Ticket(barcode="testbarcode", seat_number="A_1")]

            # Given

            beneficiary = users_factories.BeneficiaryGrant18Factory()
            cds_provider = get_provider_by_local_class("CDSStocks")
            venue_provider = providers_factories.VenueProviderFactory(provider=cds_provider)
            cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)
            offer_solo = offers_factories.EventOfferFactory(
                name="Séance ciné solo",
                venue=venue_provider.venue,
                subcategoryId=subcategories.SEANCE_CINE.id,
                lastProviderId=cinema_provider_pivot.provider.id,
            )
            stock_solo = offers_factories.EventStockFactory(offer=offer_solo, idAtProviders="1111%4444#111/datetime")

            # When
            booking = api.book_offer(beneficiary=beneficiary, stock_id=stock_solo.id, quantity=1)

            # Then
            assert len(booking.externalBookings) == 1
            assert booking.externalBookings[0].barcode == "testbarcode"
            assert booking.externalBookings[0].seat == "A_1"

        @patch("pcapi.core.bookings.api.external_bookings_api.book_cinema_ticket")
        @override_features(ENABLE_CDS_IMPLEMENTATION=True)
        def test_duo_external_booking(self, mocked_book_cinema_ticket):
            mocked_book_cinema_ticket.return_value = [
                Ticket(barcode="barcode1", seat_number="B_1"),
                Ticket(barcode="barcode2", seat_number="B_2"),
            ]
            # Given
            beneficiary = users_factories.BeneficiaryGrant18Factory()
            cds_provider = get_provider_by_local_class("CDSStocks")
            venue_provider = providers_factories.VenueProviderFactory(provider=cds_provider)
            cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)
            offer_duo = offers_factories.EventOfferFactory(
                name="Séance ciné duo",
                venue=venue_provider.venue,
                subcategoryId=subcategories.SEANCE_CINE.id,
                lastProviderId=cinema_provider_pivot.provider.id,
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

        @override_features(ENABLE_CDS_IMPLEMENTATION=True)
        def test_error_if_offer_from_inactive_cinema_venue_provider(self):
            cds_provider = get_provider_by_local_class("CDSStocks")
            venue_provider = providers_factories.VenueProviderFactory(provider=cds_provider, isActive=False)
            providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue, provider=cds_provider)
            beneficiary = users_factories.BeneficiaryGrant18Factory()

            offer_solo = offers_factories.EventOfferFactory(
                name="Séance ciné solo",
                venue=venue_provider.venue,
                subcategoryId=subcategories.SEANCE_CINE.id,
                lastProviderId=cds_provider.id,
            )
            stock_solo = offers_factories.EventStockFactory(offer=offer_solo, idAtProviders="1111%4444#111/datetime")
            with pytest.raises(Exception) as exc:
                api.book_offer(beneficiary=beneficiary, stock_id=stock_solo.id, quantity=1)

            assert Booking.query.count() == 0
            assert str(exc.value) == f"No active cinema venue provider found for venue #{venue_provider.venue.id}"

        @patch("pcapi.core.bookings.api.external_bookings_api.book_cinema_ticket")
        @override_features(ENABLE_CDS_IMPLEMENTATION=True)
        def test_no_booking_if_external_booking_fails(
            self,
            mocked_book_cinema_ticket,
        ):
            # Given
            mocked_book_cinema_ticket.side_effect = Exception("Something wrong happened")
            cds_provider = get_provider_by_local_class("CDSStocks")
            venue_provider = providers_factories.VenueProviderFactory(provider=cds_provider)
            providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue, provider=cds_provider)
            beneficiary = users_factories.BeneficiaryGrant18Factory()

            offer_solo = offers_factories.EventOfferFactory(
                name="Séance ciné solo",
                venue=venue_provider.venue,
                subcategoryId=subcategories.SEANCE_CINE.id,
                lastProviderId=cds_provider.id,
            )
            stock_solo = offers_factories.EventStockFactory(offer=offer_solo, idAtProviders="1111%4444#111/datetime")

            # When
            with pytest.raises(Exception):
                api.book_offer(beneficiary=beneficiary, stock_id=stock_solo.id, quantity=1)

            assert Booking.query.count() == 0

        @override_features(ENABLE_CDS_IMPLEMENTATION=True)
        def test_book_manual_offer(self):
            beneficiary = users_factories.BeneficiaryGrant18Factory()
            cds_provider = get_provider_by_local_class("CDSStocks")
            venue_provider = providers_factories.VenueProviderFactory(provider=cds_provider)
            providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)
            non_synced_offer = offers_factories.EventOfferFactory(
                name="Séance ciné",
                venue=venue_provider.venue,
                subcategoryId=subcategories.SEANCE_CINE.id,
            )
            stock = offers_factories.EventStockFactory(offer=non_synced_offer)

            booking = api.book_offer(beneficiary=beneficiary, stock_id=stock.id, quantity=1)

            assert booking.token
            assert len(booking.externalBookings) == 0

        def test_sold_out_failure(self, requests_mock):
            external_booking_url = "https://api.example.com/"
            beneficiary = users_factories.BeneficiaryGrant18Factory()
            provider = providers_factories.ProviderFactory(
                bookingExternalUrl=external_booking_url,
                cancelExternalUrl=external_booking_url,
            )
            stock = offers_factories.EventStockFactory(
                offer__lastProvider=provider,
                offer__withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
                idAtProviders="",
                quantity=25,
                dnBookedQuantity=10,
            )
            requests_mock.post(
                external_booking_url,
                json={"error": "sold_out", "remainingQuantity": 0},
                status_code=409,
            )

            with pytest.raises(external_bookings_exceptions.ExternalBookingSoldOutError):
                api.book_offer(beneficiary, stock.id, quantity=1)

            assert not models.Booking.query.count()
            assert stock.quantity == 10  # dnBookedQuantity + 0

        def test_not_enough_seats_failure(self, requests_mock):
            external_booking_url = "https://api.example.com/"
            beneficiary = users_factories.BeneficiaryGrant18Factory()
            provider = providers_factories.ProviderFactory(
                bookingExternalUrl=external_booking_url,
                cancelExternalUrl=external_booking_url,
            )
            stock = offers_factories.EventStockFactory(
                offer__isDuo=True,
                offer__lastProvider=provider,
                offer__withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
                idAtProviders="",
                quantity=25,
                dnBookedQuantity=10,
            )
            requests_mock.post(
                external_booking_url,
                json={"error": "not_enough_seats", "remainingQuantity": 1},
                status_code=409,
            )

            with pytest.raises(external_bookings_exceptions.ExternalBookingNotEnoughSeatsError):
                api.book_offer(beneficiary, stock.id, quantity=2)

            assert not models.Booking.query.count()
            assert stock.quantity == 11  # dnBookedQuantity + 1

        @override_features(DISABLE_CDS_EXTERNAL_BOOKINGS=True)
        def test_should_raise_error_when_cds_external_bookings_are_disabled(self):
            beneficiary = users_factories.BeneficiaryGrant18Factory()
            cds_provider = get_provider_by_local_class("CDSStocks")
            venue_provider = providers_factories.VenueProviderFactory(provider=cds_provider)
            cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)
            offer_solo = offers_factories.EventOfferFactory(
                name="Séance ciné solo",
                venue=venue_provider.venue,
                subcategoryId=subcategories.SEANCE_CINE.id,
                lastProviderId=cinema_provider_pivot.provider.id,
            )
            stock_solo = offers_factories.EventStockFactory(offer=offer_solo, idAtProviders="1111%4444#111/datetime")

            # When
            with pytest.raises(feature.DisabledFeatureError) as exc:
                api.book_offer(beneficiary=beneficiary, stock_id=stock_solo.id, quantity=1)

            assert Booking.query.count() == 0
            assert str(exc.value) == "DISABLE_CDS_EXTERNAL_BOOKINGS is active"

        @override_features(DISABLE_BOOST_EXTERNAL_BOOKINGS=True)
        def test_should_raise_error_when_boost_external_bookings_are_disabled(self):
            beneficiary = users_factories.BeneficiaryGrant18Factory()
            boost_provider = get_provider_by_local_class("BoostStocks")
            venue_provider = providers_factories.VenueProviderFactory(provider=boost_provider)
            cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)
            offer_solo = offers_factories.EventOfferFactory(
                name="Séance ciné solo",
                venue=venue_provider.venue,
                subcategoryId=subcategories.SEANCE_CINE.id,
                lastProviderId=cinema_provider_pivot.provider.id,
            )
            stock_solo = offers_factories.EventStockFactory(offer=offer_solo, idAtProviders="123%12345678912345#111")

            # When
            with pytest.raises(feature.DisabledFeatureError) as exc:
                api.book_offer(beneficiary=beneficiary, stock_id=stock_solo.id, quantity=1)

            assert Booking.query.count() == 0
            assert str(exc.value) == "DISABLE_BOOST_EXTERNAL_BOOKINGS is active"

        @override_features(ENABLE_CGR_INTEGRATION=True, DISABLE_CGR_EXTERNAL_BOOKINGS=True)
        def test_should_raise_error_when_cgr_external_bookings_are_disabled(self):
            beneficiary = users_factories.BeneficiaryGrant18Factory()
            boost_provider = get_provider_by_local_class("CGRStocks")
            venue_provider = providers_factories.VenueProviderFactory(provider=boost_provider)
            cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)
            offer_solo = offers_factories.EventOfferFactory(
                name="Séance ciné solo",
                venue=venue_provider.venue,
                subcategoryId=subcategories.SEANCE_CINE.id,
                lastProviderId=cinema_provider_pivot.provider.id,
            )
            stock_solo = offers_factories.EventStockFactory(offer=offer_solo, idAtProviders="123%12354114%CGR#111")

            # When
            with pytest.raises(feature.DisabledFeatureError) as exc:
                api.book_offer(beneficiary=beneficiary, stock_id=stock_solo.id, quantity=1)

            assert Booking.query.count() == 0
            assert str(exc.value) == "DISABLE_CGR_EXTERNAL_BOOKINGS is active"


@pytest.mark.usefixtures("db_session")
class CancelByBeneficiaryTest:
    @patch("pcapi.core.bookings.api._cancel_external_booking")
    def test_cancel_booking(self, mocked_cancel_external_booking):
        stock = offers_factories.StockFactory(offer__bookingEmail="offerer@example.com")
        booking = bookings_factories.BookingFactory.create_batch(20, stock=stock)[0]
        user = booking.user
        with assert_no_duplicated_queries():
            api.cancel_booking_by_beneficiary(user, booking)

        mocked_cancel_external_booking.assert_called_once_with(booking, stock)
        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

        assert booking.status is BookingStatus.CANCELLED
        assert booking.cancellationReason == BookingCancellationReasons.BENEFICIARY
        assert len(mails_testing.outbox) == 2
        email_data1 = mails_testing.outbox[0]
        assert email_data1["template"] == dataclasses.asdict(
            TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY.value
        )  # to beneficiary
        email_data2 = mails_testing.outbox[1]
        assert email_data2["template"] == dataclasses.asdict(
            TransactionalEmail.BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO.value
        )  # to offerer

    @patch("pcapi.tasks.external_api_booking_notification_tasks.external_api_booking_notification_task.delay")
    def test_send_notification_to_external_api_when_cancel_booking(self, mocked_task):
        provider = providers_factories.ProviderFactory(
            name="Technical provider", localClass=None, notificationExternalUrl="http://external.api.com/notify"
        )
        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.StockFactory(
            offer__lastProvider=provider,
            offer__venue__street="1 boulevard Poissonniere",
            offer__extraData={"ean": "1234567890123"},
            dnBookedQuantity=1,
            idAtProviders="",
            lastProvider=provider,
        )
        booking = bookings_factories.BookingFactory(stock=stock)

        api.cancel_booking_by_beneficiary(booking.user, booking)

        updated_booking = models.Booking.query.filter().one()

        assert models.Booking.query.filter().count() == 1
        assert updated_booking.status == BookingStatus.CANCELLED

        assert updated_booking.stock.dnBookedQuantity == 1

        assert mocked_task.call_count == 1
        notification = mocked_task.call_args.args[0].data
        assert notification.offer_ean == "1234567890123"
        assert notification.offer_id == stock.offer.id
        assert notification.offer_name == stock.offer.name
        assert notification.offer_price == finance_api.utils.to_eurocents(stock.price)
        assert notification.stock_id == stock.id
        assert notification.booking_quantity == booking.quantity
        assert notification.booking_creation_date == booking.dateCreated
        assert notification.venue_address == "1 boulevard Poissonniere"
        assert notification.user_email == booking.user.email
        assert notification.user_first_name == booking.user.firstName
        assert notification.user_last_name == booking.user.lastName
        assert notification.user_phone == booking.user.phoneNumber
        assert notification.action == BookingAction.CANCEL

        assert mocked_task.call_args.args[0].notificationUrl == provider.notificationExternalUrl

    @patch("pcapi.tasks.external_api_booking_notification_tasks.external_api_booking_notification_task.delay")
    def test_cancel_booking_when_send_notification_to_external_api_fails(self, mocked_task):
        provider = providers_factories.ProviderFactory(
            name="Technical provider", localClass=None, notificationExternalUrl="http://external.api.com/notify"
        )
        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            offer__lastProvider=provider,
            offer__venue__street="1 boulevard Poissonniere",
            offer__extraData={"ean": "1234567890123"},
            offer__withdrawalType=offers_models.WithdrawalTypeEnum.NO_TICKET,
            dnBookedQuantity=1,
            idAtProviders="",
            lastProvider=provider,
        )
        booking = bookings_factories.BookingFactory(stock=stock)

        mocked_task.side_effect = Exception("Something wrong happened")

        api.cancel_booking_by_beneficiary(booking.user, booking)

        updated_booking = models.Booking.query.filter().one()

        assert models.Booking.query.filter().count() == 1
        assert updated_booking.status == BookingStatus.CANCELLED

        assert updated_booking.stock.dnBookedQuantity == 1

    def test_cancel_booking_twice(self):
        booking = bookings_factories.BookingFactory()
        initial_quantity = booking.stock.dnBookedQuantity

        api.cancel_booking_by_beneficiary(booking.user, booking)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

        assert booking.status is BookingStatus.CANCELLED
        assert booking.stock.dnBookedQuantity == (initial_quantity - 1)

        with pytest.raises(exceptions.BookingIsCancelled):
            api.cancel_booking_by_beneficiary(booking.user, booking)

        assert booking.status is BookingStatus.CANCELLED
        assert booking.stock.dnBookedQuantity == (initial_quantity - 1)

    def test_raise_if_booking_is_already_used(self):
        booking = bookings_factories.UsedBookingFactory()

        with pytest.raises(exceptions.BookingIsAlreadyUsed):
            api.cancel_booking_by_beneficiary(booking.user, booking)
        assert booking.status is not BookingStatus.CANCELLED

    def test_raise_if_event_too_close(self):
        event_date_too_close_to_cancel_booking = datetime.utcnow() + timedelta(days=1)
        booking = bookings_factories.BookingFactory(
            stock__beginningDatetime=event_date_too_close_to_cancel_booking,
        )
        with pytest.raises(exceptions.CannotCancelConfirmedBooking) as exc:
            api.cancel_booking_by_beneficiary(booking.user, booking)
        assert booking.status is not BookingStatus.CANCELLED
        assert not booking.cancellationReason
        assert exc.value.errors["booking"] == [
            "Impossible d'annuler une réservation plus de 48h après l'avoir "
            "réservée et moins de 48h avant le début de l'évènement"
        ]

    def test_raise_if_booking_created_too_long_ago_to_cancel_booking(self):
        event_date_far_enough_to_cancel_booking = datetime.utcnow() + timedelta(days=2, minutes=1)
        booking_date_too_long_ago_to_cancel_booking = datetime.utcnow() - timedelta(days=2, minutes=1)
        booking = bookings_factories.BookingFactory(
            stock__beginningDatetime=event_date_far_enough_to_cancel_booking,
            dateCreated=booking_date_too_long_ago_to_cancel_booking,
        )
        with pytest.raises(exceptions.CannotCancelConfirmedBooking) as exc:
            api.cancel_booking_by_beneficiary(booking.user, booking)
        assert booking.status is not BookingStatus.CANCELLED
        assert not booking.cancellationReason
        assert exc.value.errors["booking"] == [
            "Impossible d'annuler une réservation plus de 48h après l'avoir réservée"
            " et moins de 48h avant le début de l'évènement"
        ]

    def test_raise_if_event_too_close_and_booked_long_ago(self):
        booking_date_too_long_ago_to_cancel_booking = datetime.utcnow() - timedelta(days=2, minutes=1)
        event_date_too_close_to_cancel_booking = datetime.utcnow() + timedelta(days=1)
        booking = bookings_factories.BookingFactory(
            stock__beginningDatetime=event_date_too_close_to_cancel_booking,
            dateCreated=booking_date_too_long_ago_to_cancel_booking,
        )
        with pytest.raises(exceptions.CannotCancelConfirmedBooking) as exc:
            api.cancel_booking_by_beneficiary(booking.user, booking)
        assert booking.status is not BookingStatus.CANCELLED
        assert not booking.cancellationReason
        assert exc.value.errors["booking"] == [
            "Impossible d'annuler une réservation plus de 48h après l'avoir "
            "réservée et moins de 48h avant le début de l'évènement"
        ]

    def test_raise_if_trying_to_cancel_someone_else_s_booking(self):
        booking = bookings_factories.BookingFactory()
        other_beneficiary = users_factories.BeneficiaryGrant18Factory()
        with pytest.raises(exceptions.BookingDoesntExist):
            api.cancel_booking_by_beneficiary(other_beneficiary, booking)
        assert booking.status is not BookingStatus.CANCELLED
        assert not booking.cancellationReason

    def test_raise_external_booking_error_if_trying_to_cancel_with_external_server_error(self, requests_mock):
        external_url = "https://book_my_offer.com"
        provider = providers_factories.ProviderFactory(
            name="Technical provider",
            bookingExternalUrl=external_url + "/book",
            cancelExternalUrl=external_url + "/cancel",
        )
        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            offer__subcategoryId=subcategories.SEANCE_ESSAI_PRATIQUE_ART.id,
            offer__lastProvider=provider,
            idAtProviders="",
        )
        booking = bookings_factories.BookingFactory(stock=stock)
        offerer_factories.ApiKeyFactory(offerer=booking.offerer)
        external_bookings_factories.ExternalBookingFactory(booking=booking, barcode="1234567890123")
        requests_mock.post(
            external_url + "/cancel",
            text="internal error",
            status_code=500,
        )

        with pytest.raises(external_bookings_exceptions.ExternalBookingException):
            api.cancel_booking_by_beneficiary(booking.user, booking)

        assert booking.status is not BookingStatus.CANCELLED
        assert not booking.cancellationReason

    def test_no_external_booking_error_when_trying_to_cancel_with_already_canceled_ticket(self, requests_mock):
        external_url = "https://book_my_offer.com"
        provider = providers_factories.ProviderFactory(
            name="Technical provider",
            bookingExternalUrl=external_url + "/book",
            cancelExternalUrl=external_url + "/cancel",
        )
        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            offer__subcategoryId=subcategories.SEANCE_ESSAI_PRATIQUE_ART.id,
            offer__lastProvider=provider,
            idAtProviders="",
        )
        booking = bookings_factories.BookingFactory(stock=stock)
        offerer_factories.ApiKeyFactory(offerer=booking.offerer)
        external_bookings_factories.ExternalBookingFactory(booking=booking, barcode="1234567890123")
        requests_mock.post(
            external_url + "/cancel",
            json={"error": "already_cancelled", "remainingQuantity": None},
            status_code=409,
        )

        assert api.cancel_booking_by_beneficiary(booking.user, booking) is None

        assert booking.status is BookingStatus.CANCELLED
        assert booking.cancellationReason == BookingCancellationReasons.BENEFICIARY
        assert booking.stock.remainingQuantity == "unlimited"

    @patch("pcapi.core.bookings.api.external_bookings_api.cancel_booking")
    @override_features(ENABLE_CDS_IMPLEMENTATION=True)
    def test_cds_cancel_external_booking(self, mocked_cancel_booking):
        cds_provider = get_provider_by_local_class("CDSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cds_provider)
        mocked_cancel_booking.return_value = None

        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        offer_solo = offers_factories.EventOfferFactory(
            name="Séance ciné solo", subcategoryId=subcategories.SEANCE_CINE.id, venue=venue_provider.venue
        )
        stock_solo = offers_factories.EventStockFactory(offer=offer_solo, idAtProviders="1111")
        booking = bookings_factories.BookingFactory(stock=stock_solo, user=beneficiary)
        ExternalBookingFactory(booking=booking)
        api._cancel_booking(booking, BookingCancellationReasons.BENEFICIARY)

        mocked_cancel_booking.assert_called()

    @override_features(ENABLE_EMS_INTEGRATION=True)
    def test_ems_cancel_external_booking(self, requests_mock):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider)
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)
        offer = offers_factories.EventOfferFactory(
            name="Film",
            venue=venue_provider.venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            lastProviderId=cinema_provider_pivot.provider.id,
        )
        stock = offers_factories.EventStockFactory(offer=offer, idAtProviders="1111%2222%EMS#3333")
        booking = bookings_factories.BookingFactory(stock=stock, user=beneficiary)
        ExternalBookingFactory(
            booking=booking,
            additional_information={
                "num_cine": "9997",
                "num_caisse": "255",
                "num_trans": 1257,
                "num_ope": 147149,
            },
        )

        assert booking.status is BookingStatus.CONFIRMED
        assert len(booking.externalBookings) == 1
        assert booking.externalBookings[0].barcode
        assert booking.externalBookings[0].seat
        assert booking.externalBookings[0].additional_information == {
            "num_cine": "9997",
            "num_caisse": "255",
            "num_trans": 1257,
            "num_ope": 147149,
        }

        requests_mock.post(url=re.compile(r"https://fake_url.com/ANNULATION/*"), json={})
        old_quantity = stock.dnBookedQuantity

        api._cancel_booking(booking, BookingCancellationReasons.BENEFICIARY)

        assert booking.status is BookingStatus.CANCELLED
        assert stock.dnBookedQuantity == old_quantity - 1

    @patch("pcapi.core.bookings.api.external_bookings_api.cancel_event_ticket")
    def test_cancel_external_booking_from_charlie_api(self, mocked_cancel_booking):
        external_url = "https://book_my_offer.com"
        provider = providers_factories.ProviderFactory(
            name="Technical provider",
            bookingExternalUrl=external_url + "/book",
            cancelExternalUrl=external_url + "/cancel",
        )
        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            offer__subcategoryId=subcategories.SEANCE_ESSAI_PRATIQUE_ART.id,
            offer__lastProvider=provider,
            idAtProviders="",
            quantity=20,
            dnBookedQuantity=4,
        )
        booking = bookings_factories.BookingFactory(stock=stock)
        offerer_factories.ApiKeyFactory(offerer=booking.offerer)
        external_bookings_factories.ExternalBookingFactory(booking=booking, barcode="1234567890123")
        mocked_cancel_booking.return_value = None

        api._cancel_booking(booking, BookingCancellationReasons.BENEFICIARY)

        mocked_cancel_booking.assert_called()

    def test_cancel_booking_tracked_in_amplitude(self):
        booking = bookings_factories.BookingFactory()

        api.cancel_booking_by_beneficiary(booking.user, booking)

        assert amplitude_testing.requests[0] == {
            "event_name": "BOOKING_CANCELLED",
            "event_properties": {
                "booking_id": booking.id,
                "category": "FILM",
                "offer_id": booking.stock.offerId,
                "price": 10.10,
                "reason": BookingCancellationReasons.BENEFICIARY.value,
                "subcategory": "SUPPORT_PHYSIQUE_FILM",
            },
            "user_id": booking.userId,
        }


@pytest.mark.usefixtures("db_session")
class CancelByOffererTest:
    def test_cancel(self):
        booking = bookings_factories.BookingFactory()

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
            "user_ids": [booking.userId],
            "can_be_asynchronously_retried": False,
        }

    def test_raise_if_already_cancelled(self):
        booking = bookings_factories.CancelledBookingFactory(cancellationReason=BookingCancellationReasons.BENEFICIARY)
        with pytest.raises(exceptions.BookingIsAlreadyCancelled):
            api.cancel_booking_by_offerer(booking)
        assert booking.status is BookingStatus.CANCELLED
        assert booking.cancellationReason == BookingCancellationReasons.BENEFICIARY  # unchanged

        assert not push_testing.requests

    def test_raise_if_already_used(self):
        booking = bookings_factories.UsedBookingFactory()
        with pytest.raises(exceptions.BookingIsAlreadyUsed):
            api.cancel_booking_by_offerer(booking)
        assert booking.status is BookingStatus.USED
        assert not booking.cancellationReason

        assert not push_testing.requests

    def test_cancel_all_bookings_from_stock(self):
        stock = offers_factories.StockFactory(dnBookedQuantity=1)
        booking_1 = bookings_factories.BookingFactory(stock=stock)
        booking_2 = bookings_factories.BookingFactory(stock=stock)
        used_booking = bookings_factories.UsedBookingFactory(stock=stock)
        cancelled_booking = bookings_factories.CancelledBookingFactory(stock=stock)

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

    @patch("pcapi.core.bookings.api.external_bookings_api.cancel_event_ticket")
    def test_cancel_all_bookings_from_stock_dont_call_external_api(self, mock_cancel_event_ticket):
        provider_with_charlie = providers_factories.PublicApiProviderFactory()
        event_offer = offers_factories.EventOfferFactory(lastProvider=provider_with_charlie)
        stock = offers_factories.StockFactory(dnBookedQuantity=1, offer=event_offer)
        booking = bookings_factories.BookingFactory(stock=stock, status=models.BookingStatus.USED)
        bookings_factories.ExternalBookingFactory(bookingId=booking.id)

        api.cancel_bookings_from_stock_by_offerer(stock)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

        mock_cancel_event_ticket.assert_not_called()

    def test_send_email_when_cancelled_by_offerer(self):
        # when
        booking = bookings_factories.BookingFactory(stock__offer__bookingEmail="test@sent")

        api.cancel_booking_by_offerer(booking)

        # then
        assert len(mails_testing.outbox) == 2
        assert mails_testing.outbox[0]["To"] == booking.email
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.BOOKING_CANCELLATION_BY_PRO_TO_BENEFICIARY.value
        )
        assert mails_testing.outbox[1]["To"] == "test@sent"
        assert "Confirmation de votre annulation de réservation " in mails_testing.outbox[1]["subject"]


@pytest.mark.usefixtures("db_session")
class CancelForFraudTest:
    def test_cancel(self):
        booking = bookings_factories.BookingFactory()

        api.cancel_booking_for_fraud(booking)

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

        assert booking.status is BookingStatus.CANCELLED
        assert booking.cancellationReason == BookingCancellationReasons.FRAUD


@pytest.mark.usefixtures("db_session")
class CancelBookingTest:
    # Test `_cancel_booking()` internal function.

    # FIXME (dbaty, 2023-09-11): the following test fails because
    # `pytest_flask_sqlalchemy` introduces extra `SAVEPOINT` queries
    # that change the behaviour of `ROLLBACK` queries. When run in
    # tests, the `ROLLBACK` in `_cancel_booking()` does not roll back
    # anything. When run outside tests, though, the `ROLLBACK` works
    # well.
    @pytest.mark.xfail
    def test_cancel_already_used_no_override(self):
        finance_event = finance_factories.UsedBookingFinanceEventFactory(
            status=finance_models.FinanceEventStatus.PRICED,
            booking__stock__offer__venue__pricing_point="self",
        )
        booking = finance_event.booking
        pricing = finance_factories.PricingFactory(event=finance_event, booking=booking)

        api._cancel_booking(
            booking,
            models.BookingCancellationReasons.BENEFICIARY,
        )

        assert booking.status == models.BookingStatus.USED
        assert pricing.status == finance_models.PricingStatus.VALIDATED
        assert finance_event.status == finance_models.FinanceEventStatus.PRICED


@pytest.mark.usefixtures("db_session")
def test_mark_as_cancelled():
    booking = bookings_factories.BookingFactory(
        stock__offer__venue__pricing_point="self",
    )
    api.mark_as_used(booking, models.BookingValidationAuthorType.OFFERER)

    event = finance_models.FinanceEvent.query.one()
    finance_api.price_event(event)
    pricing = finance_models.Pricing.query.one()
    assert booking.status == BookingStatus.USED
    assert booking.validationAuthorType == models.BookingValidationAuthorType.OFFERER
    assert pricing.status == finance_models.PricingStatus.VALIDATED

    api.mark_as_cancelled(booking, BookingCancellationReasons.FRAUD)
    assert booking.status == BookingStatus.CANCELLED
    assert booking.cancellationReason == BookingCancellationReasons.FRAUD
    assert event.status == finance_models.FinanceEventStatus.CANCELLED
    assert pricing.status == finance_models.PricingStatus.CANCELLED
    unuse_event = finance_models.FinanceEvent.query.filter(finance_models.FinanceEvent.id != event.id).one()
    assert unuse_event.motive == finance_models.FinanceEventMotive.BOOKING_CANCELLED_AFTER_USE
    assert unuse_event.status == finance_models.FinanceEventStatus.NOT_TO_BE_PRICED


@pytest.mark.usefixtures("db_session")
class MarkAsUsedTest:
    def test_mark_as_used(self):
        booking = bookings_factories.BookingFactory()

        api.mark_as_used(booking, models.BookingValidationAuthorType.OFFERER)

        assert booking.status is BookingStatus.USED
        assert booking.validationAuthorType == models.BookingValidationAuthorType.OFFERER
        assert len(push_testing.requests) == 2
        event = finance_models.FinanceEvent.query.filter_by(booking=booking).one()
        assert event.motive == finance_models.FinanceEventMotive.BOOKING_USED

    def test_mark_as_used_with_uncancel(self):
        booking = bookings_factories.CancelledBookingFactory()

        api.mark_as_used_with_uncancelling(booking, models.BookingValidationAuthorType.BACKOFFICE)

        assert booking.status is BookingStatus.USED
        assert booking.validationAuthorType == models.BookingValidationAuthorType.BACKOFFICE
        assert booking.dateUsed is not None
        assert not booking.cancellationReason
        event = finance_models.FinanceEvent.query.filter_by(booking=booking).one()
        assert event.motive == finance_models.FinanceEventMotive.BOOKING_USED_AFTER_CANCELLATION

    def test_mark_as_used_when_stock_starts_soon(self):
        booking = bookings_factories.BookingFactory(stock__beginningDatetime=datetime.utcnow() + timedelta(days=1))
        api.mark_as_used(booking, models.BookingValidationAuthorType.OFFERER)
        assert booking.status is BookingStatus.USED
        assert booking.validationAuthorType == models.BookingValidationAuthorType.OFFERER

    def test_raise_if_already_used(self):
        booking = bookings_factories.UsedBookingFactory()
        with pytest.raises(exceptions.BookingIsAlreadyUsed):
            api.mark_as_used(booking, models.BookingValidationAuthorType.OFFERER)

    def test_raise_if_cancelled(self):
        booking = bookings_factories.CancelledBookingFactory()
        with pytest.raises(exceptions.BookingIsAlreadyCancelled):
            api.mark_as_used(booking, models.BookingValidationAuthorType.OFFERER)
        assert booking.status is not BookingStatus.USED

    def test_raise_if_already_reimbursed(self):
        booking = bookings_factories.ReimbursedBookingFactory()
        with pytest.raises(exceptions.BookingIsAlreadyRefunded):
            api.mark_as_used(booking, models.BookingValidationAuthorType.OFFERER)

    def test_raise_if_too_soon_to_mark_as_used(self):
        booking = bookings_factories.BookingFactory(stock__beginningDatetime=datetime.utcnow() + timedelta(days=4))
        with pytest.raises(exceptions.BookingIsNotConfirmed):
            api.mark_as_used(booking, models.BookingValidationAuthorType.OFFERER)
        assert booking.status is not BookingStatus.USED

    def test_mark_as_used_tracked_to_amplitude(self):
        booking = bookings_factories.BookingFactory()
        api.mark_as_used(booking, models.BookingValidationAuthorType.OFFERER)
        assert len(amplitude_testing.requests) == 1
        assert amplitude_testing.requests[0] == {
            "event_name": "BOOKING_USED",
            "event_properties": {
                "booking_id": booking.id,
                "category": "FILM",
                "offer_id": booking.stock.offerId,
                "price": 10.10,
                "subcategory": "SUPPORT_PHYSIQUE_FILM",
            },
            "user_id": booking.userId,
        }


@pytest.mark.usefixtures("db_session")
class MarkAsUnusedTest:
    def test_mark_as_unused(self):
        booking = bookings_factories.UsedBookingFactory()
        api.mark_as_unused(booking)
        assert booking.status is not BookingStatus.USED
        assert len(push_testing.requests) == 2

    def test_mark_as_unused_digital_offer(self):
        offer = offers_factories.DigitalOfferFactory()
        booking = bookings_factories.UsedBookingFactory(stock__offer=offer)
        api.mark_as_unused(booking)
        assert booking.status is not BookingStatus.USED

    def test_raise_if_not_yet_used(self):
        booking = bookings_factories.BookingFactory()
        with pytest.raises(exceptions.BookingIsNotUsed):
            api.mark_as_unused(booking)
        assert booking.status is not BookingStatus.USED

    def test_raise_if_has_reimbursement(self):
        booking = bookings_factories.UsedBookingFactory()
        finance_factories.PricingFactory(booking=booking, status=finance_models.PricingStatus.PROCESSED)
        with pytest.raises(exceptions.BookingIsAlreadyRefunded):
            api.mark_as_unused(booking)
        assert booking.status is BookingStatus.USED

    def test_raise_if_booking_was_automatically_used_for_digital_offer_with_activation_code(self):
        offer = offers_factories.DigitalOfferFactory()
        digital_stock = offers_factories.StockWithActivationCodesFactory()
        first_activation_code = digital_stock.activationCodes[0]
        booking = bookings_factories.UsedBookingFactory(stock__offer=offer, activationCode=first_activation_code)
        with pytest.raises(exceptions.BookingHasActivationCode):
            api.mark_as_unused(booking)
        assert booking.status is BookingStatus.USED

    def test_check_finance_events_and_pricings(self):
        booking = bookings_factories.BookingFactory(
            stock__offer__venue__pricing_point="self",
        )

        api.mark_as_used(booking, models.BookingValidationAuthorType.OFFERER)
        event = finance_models.FinanceEvent.query.one()
        finance_api.price_event(event)
        pricing = finance_models.Pricing.query.one()
        assert booking.status == BookingStatus.USED
        assert booking.validationAuthorType == models.BookingValidationAuthorType.OFFERER
        assert pricing.status == finance_models.PricingStatus.VALIDATED

        api.mark_as_unused(booking)
        assert booking.status == BookingStatus.CONFIRMED
        assert event.status == finance_models.FinanceEventStatus.CANCELLED
        assert pricing.status == finance_models.PricingStatus.CANCELLED
        unuse_event = finance_models.FinanceEvent.query.filter(finance_models.FinanceEvent.id != event.id).one()
        assert unuse_event.motive == finance_models.FinanceEventMotive.BOOKING_UNUSED
        assert unuse_event.status == finance_models.FinanceEventStatus.NOT_TO_BE_PRICED


@pytest.mark.parametrize(
    "booking_creation_date",
    [datetime(2020, 7, 14, 15, 30), datetime(2020, 10, 25, 1, 45), datetime.utcnow()],
    ids=["14 Jul", "Daylight Saving Switch", "Now"],
)
@pytest.mark.usefixtures("db_session")
class ComputeCancellationDateTest:
    def test_returns_none_if_no_event_beginning(self, booking_creation_date):
        event_beginning = None
        assert api.compute_booking_cancellation_limit_date(event_beginning, booking_creation_date) is None

    def test_returns_creation_date_if_event_begins_too_soon(self, booking_creation_date):
        event_date_too_close_to_cancel_booking = booking_creation_date + timedelta(days=1)
        assert (
            api.compute_booking_cancellation_limit_date(event_date_too_close_to_cancel_booking, booking_creation_date)
            == booking_creation_date
        )

    def test_returns_two_days_after_booking_creation_if_event_begins_in_more_than_four_days(
        self, booking_creation_date
    ):
        event_date_more_ten_days_from_now = booking_creation_date + timedelta(days=6)
        assert api.compute_booking_cancellation_limit_date(
            event_date_more_ten_days_from_now, booking_creation_date
        ) == booking_creation_date + timedelta(days=2)

    def test_returns_two_days_before_event_if_event_begins_between_two_and_four_days_from_now(
        self, booking_creation_date
    ):
        event_date_four_days_from_now = booking_creation_date + timedelta(days=4)
        assert api.compute_booking_cancellation_limit_date(
            event_date_four_days_from_now, booking_creation_date
        ) == event_date_four_days_from_now - timedelta(days=2)


@pytest.mark.usefixtures("db_session")
class UpdateCancellationLimitDatesTest:
    def should_update_bookings_cancellation_limit_dates_for_event_beginning_tomorrow(self):
        # Given
        now = datetime.utcnow()
        recent_booking = bookings_factories.BookingFactory(stock__beginningDatetime=now + timedelta(days=90))
        old_booking = bookings_factories.BookingFactory(stock=recent_booking.stock, dateCreated=now - timedelta(days=7))
        # When
        tomorrow = now + timedelta(days=1)
        updated_bookings = api.update_cancellation_limit_dates(
            bookings_to_update=[recent_booking, old_booking],
            new_beginning_datetime=tomorrow,
        )
        # Then
        assert updated_bookings == [recent_booking, old_booking]
        assert (
            recent_booking.cancellationLimitDate.isoformat(timespec="hours")
            == old_booking.cancellationLimitDate.isoformat(timespec="hours")
            == tomorrow.isoformat(timespec="hours")
        )

    def should_update_bookings_cancellation_limit_dates_for_event_beginning_in_three_days(self):
        # Given
        now = datetime.utcnow()
        recent_booking = bookings_factories.BookingFactory(stock__beginningDatetime=now + timedelta(days=90))
        old_booking = bookings_factories.BookingFactory(stock=recent_booking.stock, dateCreated=now - timedelta(days=7))
        # When
        updated_bookings = api.update_cancellation_limit_dates(
            bookings_to_update=[recent_booking, old_booking],
            new_beginning_datetime=now + timedelta(days=3),
        )
        # Then
        assert updated_bookings == [recent_booking, old_booking]
        two_days_past_today = now + timedelta(days=2)
        assert (
            recent_booking.cancellationLimitDate.isoformat(timespec="hours")
            == old_booking.cancellationLimitDate.isoformat(timespec="hours")
            == two_days_past_today.isoformat(timespec="hours")
        )

    def should_update_bookings_cancellation_limit_dates_for_event_beginning_in_a_week(self):
        # Given
        now = datetime.utcnow()
        recent_booking = bookings_factories.BookingFactory(stock__beginningDatetime=now + timedelta(days=90))
        old_booking = bookings_factories.BookingFactory(stock=recent_booking.stock, dateCreated=now - timedelta(days=7))
        # When
        updated_bookings = api.update_cancellation_limit_dates(
            bookings_to_update=[recent_booking, old_booking],
            new_beginning_datetime=now + timedelta(days=7),
        )
        # Then
        assert updated_bookings == [recent_booking, old_booking]
        two_days_past_today = now + timedelta(days=2)
        assert (
            recent_booking.cancellationLimitDate.isoformat(timespec="hours")
            == old_booking.cancellationLimitDate.isoformat(timespec="hours")
            == two_days_past_today.isoformat(timespec="hours")
        )


@pytest.mark.usefixtures("db_session")
class AutoMarkAsUsedAfterEventTest:
    def test_do_not_update_if_thing_product(self):
        bookings_factories.BookingFactory(stock=offers_factories.ThingStockFactory())

        api.auto_mark_as_used_after_event()

        booking = Booking.query.first()
        assert booking.status is not BookingStatus.USED
        assert not booking.dateUsed

    def test_update_booking_used_when_event_date_is_3_days_before(self):
        event_date = datetime.utcnow() - timedelta(days=3)
        bookings_factories.BookingFactory(stock__beginningDatetime=event_date)

        api.auto_mark_as_used_after_event()

        booking = Booking.query.first()
        assert booking.status is BookingStatus.USED
        assert booking.validationAuthorType == models.BookingValidationAuthorType.AUTO
        assert booking.dateUsed is not None

    def test_create_finance_event_for_individual_booking(self):
        event_date = datetime.utcnow() - timedelta(days=3)
        booking = bookings_factories.BookingFactory(stock__beginningDatetime=event_date)

        api.auto_mark_as_used_after_event()

        event = finance_models.FinanceEvent.query.one()
        assert event.booking == booking
        assert event.valueDate == booking.dateUsed != None

    def test_num_queries(self):
        event_date = datetime.utcnow() - timedelta(days=3)
        bookings_factories.BookingFactory(stock__beginningDatetime=event_date)
        bookings_factories.BookingFactory(stock__beginningDatetime=event_date)
        educational_factories.CollectiveBookingFactory(collectiveStock__beginningDatetime=event_date)
        educational_factories.CollectiveBookingFactory(collectiveStock__beginningDatetime=event_date)

        queries = 1  # select feature flag
        queries += 1  # select individual bookings
        # fmt: off
        queries += 2 * (
            1  # fetch pricing point
            + 1  # insert finance event
        )
        # fmt: on
        queries += 1  # update all individual bookings
        queries += 1  # select collective bookings
        # fmt: off
        queries += 2 * (
            1  # fetch pricing point
            + 1  # insert finance event
        )
        # fmt: on
        queries += 1  # update all collective bookings

        with assert_num_queries(queries):
            api.auto_mark_as_used_after_event()

    def test_does_not_update_when_event_date_is_only_1_day_before(self):
        event_date = datetime.utcnow() - timedelta(days=1)
        bookings_factories.BookingFactory(stock__beginningDatetime=event_date)

        api.auto_mark_as_used_after_event()

        booking = Booking.query.first()
        assert booking.status is not BookingStatus.USED
        assert booking.dateUsed is None

    def test_does_not_update_booking_if_already_used(self):
        event_date = datetime.utcnow() - timedelta(days=3)
        booking = bookings_factories.UsedBookingFactory(stock__beginningDatetime=event_date)
        initial_date_used = booking.dateUsed

        api.auto_mark_as_used_after_event()

        booking = Booking.query.first()
        assert booking.status is BookingStatus.USED
        assert booking.dateUsed == initial_date_used

    def test_does_not_update_booking_if_cancelled(self):
        event_date = datetime.utcnow() - timedelta(days=3)
        booking = bookings_factories.CancelledBookingFactory(stock__beginningDatetime=event_date)

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

    def test_update_collective_booking_when_not_used_and_event_date_is_3_days_before(self, caplog):
        event_date = datetime.utcnow() - timedelta(days=3)
        educational_factories.CollectiveBookingFactory(collectiveStock__beginningDatetime=event_date)

        with caplog.at_level(logging.INFO):
            api.auto_mark_as_used_after_event()

        collectiveBooking = CollectiveBooking.query.first()
        assert collectiveBooking.status is CollectiveBookingStatus.USED
        assert collectiveBooking.dateUsed is not None
        assert caplog.records[0].message == "BookingUsed"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "bookingId": collectiveBooking.id,
            "stockId": collectiveBooking.collectiveStockId,
        }

    def test_create_finance_event_for_collective_booking(self):
        event_date = datetime.utcnow() - timedelta(days=3)
        booking = educational_factories.CollectiveBookingFactory(collectiveStock__beginningDatetime=event_date)

        api.auto_mark_as_used_after_event()

        event = finance_models.FinanceEvent.query.one()
        assert event.collectiveBooking == booking

    def test_does_not_update_collective_booking_when_event_date_is_only_1_day_before(self):
        event_date = datetime.utcnow() - timedelta(days=1)
        educational_factories.CollectiveBookingFactory(collectiveStock__beginningDatetime=event_date)

        api.auto_mark_as_used_after_event()

        collectiveBooking = CollectiveBooking.query.first()
        assert collectiveBooking.status is not CollectiveBookingStatus.USED
        assert collectiveBooking.dateUsed is None

    def test_does_not_update_collective_booking_when_cancelled(self):
        event_date = datetime.utcnow() - timedelta(days=3)
        educational_factories.CollectiveBookingFactory(
            collectiveStock__beginningDatetime=event_date, status=CollectiveBookingStatus.CANCELLED
        )

        api.auto_mark_as_used_after_event()

        collectiveBooking = CollectiveBooking.query.first()
        assert collectiveBooking.status is CollectiveBookingStatus.CANCELLED
        assert collectiveBooking.dateUsed is None

    @override_features(UPDATE_BOOKING_USED=False)
    def test_raise_if_feature_flag_is_deactivated(self):
        with pytest.raises(ValueError):
            api.auto_mark_as_used_after_event()


@pytest.mark.usefixtures("db_session")
class GetInvidualBookingsFromStockTest:
    def test_has_bookings(self):
        stock = offers_factories.StockFactory()
        bookings = bookings_factories.BookingFactory.create_batch(2, stock=stock)

        found_bookings = list(api.get_individual_bookings_from_stock(stock.id))

        found_booking_ids = {booking.id for booking in found_bookings}
        expected_booking_ids = {booking.id for booking in bookings}

        assert len(found_bookings) == len(bookings)
        assert found_booking_ids == expected_booking_ids

    def test_has_cancelled_bookings(self):
        stock = offers_factories.StockFactory()

        booking = bookings_factories.BookingFactory(stock=stock)
        bookings_factories.BookingFactory(stock=stock, status=BookingStatus.CANCELLED)

        found_bookings = list(api.get_individual_bookings_from_stock(stock.id))

        found_booking_ids = {b.id for b in found_bookings}
        expected_booking_ids = {booking.id}

        assert found_booking_ids == expected_booking_ids

    def test_has_no_bookings(self):
        stock = offers_factories.StockFactory()
        assert not list(api.get_individual_bookings_from_stock(stock.id))


class ArchiveOldBookingsTest:
    def test_old_activation_code_bookings_are_archived(self, db_session):
        # given
        now = datetime.utcnow()
        recent = now - timedelta(days=29, hours=23)
        old = now - timedelta(days=30, hours=1)
        offer = offers_factories.OfferFactory(url="http://example.com")
        stock = offers_factories.StockFactory(offer=offer)
        recent_booking = bookings_factories.BookingFactory(stock=stock, dateCreated=recent)
        old_booking = bookings_factories.BookingFactory(stock=stock, dateCreated=old)
        offers_factories.ActivationCodeFactory(booking=recent_booking, stock=stock)
        offers_factories.ActivationCodeFactory(booking=old_booking, stock=stock)

        # when
        api.archive_old_bookings()

        # then
        db_session.refresh(recent_booking)
        db_session.refresh(old_booking)
        assert not recent_booking.displayAsEnded
        assert old_booking.displayAsEnded

    @pytest.mark.parametrize(
        "subcategoryId",
        offers_models.Stock.AUTOMATICALLY_USED_SUBCATEGORIES,
    )
    def test_old_subcategories_bookings_are_archived(self, db_session, subcategoryId):
        # given
        now = datetime.utcnow()
        recent = now - timedelta(days=29, hours=23)
        old = now - timedelta(days=30, hours=1)
        stock_free = offers_factories.StockFactory(
            offer=offers_factories.OfferFactory(subcategoryId=subcategoryId), price=0
        )
        stock_not_free = offers_factories.StockFactory(
            offer=offers_factories.OfferFactory(subcategoryId=subcategoryId), price=10
        )
        recent_booking = bookings_factories.BookingFactory(stock=stock_free, dateCreated=recent)
        old_booking = bookings_factories.BookingFactory(stock=stock_free, dateCreated=old)
        old_not_free_booking = bookings_factories.BookingFactory(stock=stock_not_free, dateCreated=old)

        # when
        api.archive_old_bookings()

        # then
        db_session.refresh(recent_booking)
        db_session.refresh(old_booking)
        db_session.refresh(old_not_free_booking)
        assert not recent_booking.displayAsEnded
        assert not old_not_free_booking.displayAsEnded
        assert old_booking.displayAsEnded

    @pytest.mark.parametrize(
        "subcategoryId",
        offers_models.Stock.AUTOMATICALLY_USED_SUBCATEGORIES,
    )
    def test_old_subcategories_bookings_are_archived_is_no_longer_free(self, db_session, subcategoryId, client):
        # given
        now = datetime.utcnow()
        recent = now - timedelta(days=29, hours=23)
        old = now - timedelta(days=30, hours=1)
        offer = offers_factories.ThingOfferFactory(subcategoryId=subcategoryId)
        stock_free = offers_factories.StockFactory(offer=offer, price=0)
        offerer_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        recent_booking = bookings_factories.BookingFactory(stock=stock_free, dateCreated=recent)
        old_booking = bookings_factories.BookingFactory(stock=stock_free, dateCreated=old)
        stock_data = {
            "price": 10,
        }
        client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)

        # when
        api.archive_old_bookings()

        # then
        db_session.refresh(recent_booking)
        db_session.refresh(old_booking)
        assert not recent_booking.displayAsEnded
        assert old_booking.displayAsEnded


@pytest.mark.usefixtures("db_session")
class PopBarcodesFromQueueAndCancelWastedExternalBookingTest:
    def test_should_not_pop_and_not_try_to_cancel_external_booking_if_minimum_age_not_reached(self, app):
        queue.add_to_queue(
            "api:external_bookings:barcodes",
            {
                "barcode": "AAA-123456789",
                "venue_id": 12,
                "timestamp": datetime.utcnow().timestamp(),
                "booking_type": RedisExternalBookingType.CINEMA,
            },
        )

        cancel_unstored_external_bookings()

        assert app.redis_client.llen("api:external_bookings:barcodes") == 1

    @patch("pcapi.core.bookings.api.external_bookings_api.cancel_booking")
    def test_should_pop_and_cancel_only_external_booking_reached_minimum_age(
        self, mocked_cancel_external_booking, app, requests_mock
    ):
        now = datetime.utcnow()
        provider = providers_factories.ProviderFactory(
            bookingExternalUrl="http://example.com/book", cancelExternalUrl="http://example.com/cancel"
        )
        stock = offers_factories.StockFactory(
            offer__lastProvider=provider, idAtProviders="", dnBookedQuantity=10, quantity=50
        )
        queue.add_to_queue(
            "api:external_bookings:barcodes",
            {
                "barcode": "DDD-123456789",
                "venue_id": 15,
                "timestamp": now.timestamp() - 100,
                "booking_type": RedisExternalBookingType.EVENT,
                "cancel_event_info": {
                    "stock_id": stock.id,
                    "provider_id": provider.id,
                },
            },
        )
        queue.add_to_queue(
            "api:external_bookings:barcodes",
            {
                "barcode": "BBB-123456789",
                "venue_id": 13,
                "timestamp": now.timestamp() - 90,
                "booking_type": RedisExternalBookingType.CINEMA,
            },
        )
        queue.add_to_queue(
            "api:external_bookings:barcodes",
            {
                "barcode": "CCC-123456789",
                "venue_id": 14,
                "timestamp": now.timestamp() - 65,
                "booking_type": RedisExternalBookingType.CINEMA,
            },
        )
        queue.add_to_queue(
            "api:external_bookings:barcodes",
            {
                "barcode": "AAA-123456789",
                "venue_id": 12,
                "timestamp": now.timestamp(),
                "booking_type": RedisExternalBookingType.CINEMA,
            },
        )
        queue.add_to_queue(
            "api:external_bookings:barcodes",
            {"barcode": "AAA-123456789", "venue_id": 12, "timestamp": now.timestamp() + 10},
        )
        ExternalBookingFactory(barcode="BBB-123456789")

        requests_mock.post(
            "http://example.com/cancel",
            json={"remainingQuantity": 16},
            status_code=200,
        )

        cancel_unstored_external_bookings()

        mocked_cancel_external_booking.assert_called_once_with(14, ["CCC-123456789"])

        assert app.redis_client.llen("api:external_bookings:barcodes") == 2
        assert stock.quantity == 26
