import datetime
import decimal
import json
from unittest.mock import patch

import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.external_bookings.exceptions as external_bookings_exceptions
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.exceptions as providers_exceptions
import pcapi.core.providers.factories as providers_factories
import pcapi.core.users.factories as user_factories
from pcapi.core.bookings.utils import generate_hmac_signature
from pcapi.core.external_bookings.api import EXTERNAL_BOOKINGS_TIMEOUT_IN_SECONDS
from pcapi.core.external_bookings.api import _instantiate_cinema_api_client
from pcapi.core.external_bookings.api import book_event_ticket
from pcapi.core.external_bookings.api import cancel_event_ticket
from pcapi.core.external_bookings.api import get_active_cinema_venue_provider
from pcapi.core.external_bookings.api import send_booking_notification_to_external_service
from pcapi.core.external_bookings.cds.client import CineDigitalServiceAPI
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.tasks.serialization.external_api_booking_notification_tasks import BookingAction


@pytest.mark.usefixtures("db_session")
class GetCinemaVenueProviderTest:
    def test_should_return_cinema_venue_provider_according_to_venue_id(self) -> None:
        # Given
        cds_provider = get_provider_by_local_class("CDSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cds_provider)
        providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)

        venue_id = venue_provider.venueId

        # When
        assert get_active_cinema_venue_provider(venue_id) == venue_provider

    def test_should_raise_exception_if_no_cinema_venue_provider(self) -> None:
        # Given
        venue_id = 0

        # When
        with pytest.raises(providers_exceptions.InactiveProvider):
            get_active_cinema_venue_provider(venue_id)

    def test_should_raise_exception_if_inactive_cinema_venue_provider(self) -> None:
        cds_provider = get_provider_by_local_class("CDSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cds_provider, isActive=False)
        providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)

        venue_id = venue_provider.venueId
        with pytest.raises(providers_exceptions.InactiveProvider):
            get_active_cinema_venue_provider(venue_id)


@pytest.mark.usefixtures("db_session")
class InstantiateCinemaApiClientTest:
    def test_should_return_client_api_according_to_name(self) -> None:
        # Given
        cds_provider = get_provider_by_local_class("CDSStocks")
        venue_provider = providers_factories.VenueProviderFactory(
            provider=cds_provider, venueIdAtOfferProvider="test_id"
        )
        cinema_provider_pivot = providers_factories.CDSCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        providers_factories.CDSCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, cinemaApiToken="test_token", accountId="test_account"
        )

        # When
        venue_id = venue_provider.venueId
        client_api = _instantiate_cinema_api_client(venue_id)

        # Then
        assert isinstance(client_api, CineDigitalServiceAPI)
        assert client_api.cinema_id == "test_id"
        assert client_api.token == "test_token"
        assert client_api.account_id == "test_account"
        assert client_api.api_url == "test_cds_url/vad/"

    def test_should_raise_an_exception_if_no_cds_details_provided_when_required(self) -> None:
        # Given
        cds_provider = get_provider_by_local_class("CDSStocks")
        venue_provider = providers_factories.VenueProviderFactory(
            provider=cds_provider, venueIdAtOfferProvider="test_id"
        )
        providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )

        # When
        venue_id = venue_provider.venueId
        with pytest.raises(Exception) as e:
            _instantiate_cinema_api_client(venue_id)

        # Then
        assert str(e.value) == "No row was found when one was required"


@pytest.mark.usefixtures("db_session")
class BookEventTicketTest:
    def test_should_raise_because_no_ticketing_system_set(self):
        provider = providers_factories.ProviderFactory()
        offer = offers_factories.EventOfferFactory(
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP, lastProviderId=provider.id
        )
        stock = offers_factories.EventStockFactory(offer=offer, idAtProviders="roi_des_forêts!")
        booking = bookings_factories.BookingFactory(stock=stock, dateCreated=datetime.datetime(2024, 5, 12), quantity=2)
        user = user_factories.BeneficiaryFactory(firstName="Jean", lastName="Passedemeyeur")

        with pytest.raises(external_bookings_exceptions.ExternalBookingException):
            book_event_ticket(booking, stock, user)

    def test_should_raise_because_provider_is_inactive(self):
        booking_creation_date = datetime.datetime(2024, 5, 12)
        provider = providers_factories.PublicApiProviderFactory(isActive=False)
        offer = offers_factories.EventOfferFactory(lastProviderId=provider.id)
        stock = offers_factories.EventStockFactory(offer=offer)
        booking = bookings_factories.BookingFactory(stock=stock, dateCreated=booking_creation_date, quantity=2)
        user = user_factories.BeneficiaryFactory()

        with pytest.raises(providers_exceptions.InactiveProvider):
            book_event_ticket(booking, stock, user)

    @patch("pcapi.core.external_bookings.api.requests.post")
    def test_should_successfully_book_an_event_ticket(self, requests_post):
        booking_creation_date = datetime.datetime(2024, 5, 12)
        provider = providers_factories.PublicApiProviderFactory(
            enabledForPro=False,  # should not have any impact
        )

        offer = offers_factories.EventOfferFactory(
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
            lastProviderId=provider.id,
            idAtProvider="oh_mon_bel_id",
            id=42,
            name="La fête aux acouphènes",
        )
        stock = offers_factories.EventStockFactory(offer=offer, idAtProviders="roi_des_forêts!")
        booking = bookings_factories.BookingFactory(stock=stock, dateCreated=booking_creation_date, quantity=2)
        user = user_factories.BeneficiaryFactory(
            firstName="Jean",
            lastName="Passedemeyeur",
        )

        # expected data
        expected_json_string = json.dumps(
            {
                "booking_confirmation_date": "2024-05-14T00:00:00",
                "booking_creation_date": "2024-05-12T00:00:00",
                "booking_quantity": 2,
                "offer_ean": None,
                "offer_id": offer.id,
                "offer_id_at_provider": "oh_mon_bel_id",
                "offer_name": "La fête aux acouphènes",
                "offer_price": 1010,
                "price_category_id": stock.priceCategoryId,
                "price_category_id_at_provider": None,
                "price_category_label": "Tarif unique",
                "stock_id": stock.id,
                "stock_id_at_provider": "roi_des_forêts!",
                "user_birth_date": user.dateOfBirth.strftime("%Y-%m-%d"),
                "user_email": user.email,
                "user_first_name": "Jean",
                "user_last_name": "Passedemeyeur",
                "user_phone": user.phoneNumber,
                "venue_address": offer.venue.offererAddress.address.street,
                "venue_department_code": offer.venue.offererAddress.address.departmentCode,
                "venue_id": offer.venue.id,
                "venue_name": offer.venue.name,
            }
        )
        expected_hmac_signature = generate_hmac_signature(provider.hmacKey, expected_json_string)

        # mocks
        requests_post.return_value.status_code = 200
        requests_post.return_value.json.return_value = {
            "remainingQuantity": 12,
            "tickets": [
                {"barcode": "1234567AJSQ", "seat": "A12"},
                {"barcode": "1234567AJSA", "seat": "A14"},
            ],
        }

        # book
        tickets, remaining_quantity = book_event_ticket(booking, stock, user)

        # checks
        requests_post.assert_called_with(
            provider.bookingExternalUrl,
            json=expected_json_string,
            hmac=expected_hmac_signature,
            headers={"Content-Type": "application/json"},
            timeout=EXTERNAL_BOOKINGS_TIMEOUT_IN_SECONDS,
            record_metrics=True,
            metric_name_suffix="external_booking_create",
        )
        assert remaining_quantity == 12
        assert [ticket.barcode for ticket in tickets] == ["1234567AJSQ", "1234567AJSA"]

    @patch("pcapi.core.external_bookings.api.requests.post")
    def test_should_successfully_book_an_event_ticket_with_null_remaining_quantity(self, requests_post):
        provider = providers_factories.PublicApiProviderFactory()
        booking = bookings_factories.BookingFactory(stock__offer__lastProviderId=provider.id, quantity=2)

        requests_post.return_value.status_code = 200
        requests_post.return_value.json.return_value = {
            "remainingQuantity": None,
            "tickets": [
                {"barcode": "1234567AJSQ", "seat": "A12"},
                {"barcode": "1234567AJSA", "seat": "A14"},
            ],
        }

        tickets, remaining_quantity = book_event_ticket(booking, booking.stock, booking.user)

        assert not remaining_quantity
        assert {ticket.barcode for ticket in tickets} == {"1234567AJSQ", "1234567AJSA"}

    @patch("pcapi.core.external_bookings.api.requests.post")
    def test_should_successfully_book_an_event_ticket_when_remaining_quantity_is_missing(self, requests_post):
        provider = providers_factories.PublicApiProviderFactory()
        booking = bookings_factories.BookingFactory(stock__offer__lastProviderId=provider.id, quantity=2)

        requests_post.return_value.status_code = 200
        requests_post.return_value.json.return_value = {
            "tickets": [
                {"barcode": "1234567AJSQ", "seat": "A12"},
                {"barcode": "1234567AJSA", "seat": "A14"},
            ],
        }

        tickets, remaining_quantity = book_event_ticket(booking, booking.stock, booking.user)

        assert not remaining_quantity
        assert {ticket.barcode for ticket in tickets} == {"1234567AJSQ", "1234567AJSA"}

    @patch("pcapi.core.external_bookings.api.requests.post")
    def test_should_raise_an_error_because_response_cant_be_parsed(self, requests_post):
        provider = providers_factories.PublicApiProviderFactory()
        booking = bookings_factories.BookingFactory(stock__offer__lastProviderId=provider.id, quantity=2)

        requests_post.return_value.status_code = 200
        requests_post.return_value.json.return_value = {
            "remainingQuantity": "unlimited",
            "tickets": [
                {"barcode": "1234567AJSQ", "seat": "A12"},
                {"barcode": "1234567AJSA", "seat": "A14"},
            ],
        }

        with pytest.raises(external_bookings_exceptions.ExternalBookingException):
            book_event_ticket(booking, booking.stock, booking.user)

    @patch("pcapi.core.external_bookings.api.requests.post")
    def test_should_successfully_book_an_event_ticket_using_venue_external_url(self, requests_post):
        booking_creation_date = datetime.datetime(2024, 5, 12)
        provider = providers_factories.PublicApiProviderFactory()
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(venue=venue, provider=provider)
        providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider, bookingExternalUrl="https://coucou.com", cancelExternalUrl="https://bye.co"
        )
        offer = offers_factories.EventOfferFactory(
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
            lastProviderId=provider.id,
            idAtProvider="oh_mon_bel_id",
            id=42,
            name="La fête aux acouphènes",
            venue=venue,
        )
        price_category = offers_factories.PriceCategoryFactory(
            offer=offer,
            price=decimal.Decimal("10.1"),
            idAtProvider="pause...",
        )
        stock = offers_factories.EventStockFactory(
            offer=offer, idAtProviders="roi_des_forêts!", priceCategory=price_category
        )
        booking = bookings_factories.BookingFactory(stock=stock, dateCreated=booking_creation_date, quantity=2)
        user = user_factories.BeneficiaryFactory(
            firstName="Jean",
            lastName="Passedemeyeur",
        )

        # expected data
        expected_json_string = json.dumps(
            {
                "booking_confirmation_date": "2024-05-14T00:00:00",
                "booking_creation_date": "2024-05-12T00:00:00",
                "booking_quantity": 2,
                "offer_ean": None,
                "offer_id": offer.id,
                "offer_id_at_provider": "oh_mon_bel_id",
                "offer_name": "La fête aux acouphènes",
                "offer_price": 1010,
                "price_category_id": stock.priceCategoryId,
                "price_category_id_at_provider": "pause...",
                "price_category_label": stock.priceCategory.label,
                "stock_id": stock.id,
                "stock_id_at_provider": "roi_des_forêts!",
                "user_birth_date": user.dateOfBirth.strftime("%Y-%m-%d"),
                "user_email": user.email,
                "user_first_name": "Jean",
                "user_last_name": "Passedemeyeur",
                "user_phone": user.phoneNumber,
                "venue_address": offer.venue.offererAddress.address.street,
                "venue_department_code": offer.venue.offererAddress.address.departmentCode,
                "venue_id": offer.venue.id,
                "venue_name": offer.venue.name,
            }
        )
        expected_hmac_signature = generate_hmac_signature(provider.hmacKey, expected_json_string)

        # mocks
        requests_post.return_value.status_code = 200
        requests_post.return_value.json.return_value = {
            "remainingQuantity": 12,
            "tickets": [
                {"barcode": "1234567AJSQ", "seat": "A12"},
                {"barcode": "1234567AJSA", "seat": "A14"},
            ],
        }

        # book
        book_event_ticket(booking, stock, user)

        # checks
        requests_post.assert_called_with(
            "https://coucou.com",
            json=expected_json_string,
            hmac=expected_hmac_signature,
            headers={"Content-Type": "application/json"},
            timeout=EXTERNAL_BOOKINGS_TIMEOUT_IN_SECONDS,
            record_metrics=True,
            metric_name_suffix="external_booking_create",
        )

    @patch("pcapi.core.external_bookings.api.requests.post")
    def test_raise_because_the_event_is_sold_out(self, requests_post):
        provider = providers_factories.PublicApiProviderFactory()
        offer = offers_factories.EventOfferFactory(
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
            lastProviderId=provider.id,
        )
        stock = offers_factories.EventStockFactory(offer=offer)
        booking = bookings_factories.BookingFactory(stock=stock, quantity=2)
        user = user_factories.BeneficiaryFactory()

        # mocks
        requests_post.return_value.status_code = 409
        requests_post.return_value.json.return_value = {
            "error": "sold_out",
            "remainingQuantity": 0,
        }

        # try to book
        with pytest.raises(external_bookings_exceptions.ExternalBookingSoldOutError):
            book_event_ticket(booking, stock, user)

    @patch("pcapi.core.external_bookings.api.requests.post")
    def test_raise_because_there_are_no_more_seats(self, requests_post):
        provider = providers_factories.PublicApiProviderFactory()
        offer = offers_factories.EventOfferFactory(
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
            lastProviderId=provider.id,
        )
        stock = offers_factories.EventStockFactory(offer=offer)
        booking = bookings_factories.BookingFactory(stock=stock, quantity=2)
        user = user_factories.BeneficiaryFactory()

        # mocks
        requests_post.return_value.status_code = 409
        requests_post.return_value.json.return_value = {
            "error": "not_enough_seats",
            "remainingQuantity": 1,
        }

        # try to book
        with pytest.raises(external_bookings_exceptions.ExternalBookingNotEnoughSeatsError):
            book_event_ticket(booking, stock, user)

    @patch("pcapi.core.external_bookings.api.requests.post")
    def test_raise_because_there_is_an_unexpected_error(self, requests_post):
        provider = providers_factories.PublicApiProviderFactory()
        offer = offers_factories.EventOfferFactory(
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
            lastProviderId=provider.id,
        )
        stock = offers_factories.EventStockFactory(offer=offer)
        booking = bookings_factories.BookingFactory(stock=stock, quantity=2)
        user = user_factories.BeneficiaryFactory()

        # mocks
        requests_post.return_value.status_code = 500
        requests_post.return_value.ok = False
        requests_post.return_value.json.return_value = {}
        requests_post.return_value.text = "on est en carafe !!"

        # try to book
        with pytest.raises(external_bookings_exceptions.ExternalBookingException) as error:
            book_event_ticket(booking, stock, user)

        assert str(error.value) == "External booking failed with status code 500 and message on est en carafe !!"

    @patch("pcapi.core.external_bookings.api.requests.post")
    def test_uses_offer_address_when_available(self, requests_post):
        requests_post.return_value.status_code = 200
        # The return value doesn't matter in this test, we just want the call to be successful
        requests_post.return_value.json.return_value = {
            "remainingQuantity": 12,
            "tickets": [
                {"barcode": "1234567AJSQ", "seat": "A12"},
                {"barcode": "1234567AJSA", "seat": "A14"},
            ],
        }
        provider = providers_factories.PublicApiProviderFactory()

        # 2 offers : one without address
        offer_without_address = offers_factories.EventOfferFactory(
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
            lastProviderId=provider.id,
            idAtProvider="oh_mon_bel_id",
            name="La fête aux acouphènes",
        )
        stock_of_the_offer_without_address = offers_factories.EventStockFactory(
            offer=offer_without_address, idAtProviders="stock_id"
        )

        # one with address
        offerer_address = offerers_factories.OffererAddressFactory()
        offer_with_address = offers_factories.EventOfferFactory(
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
            lastProviderId=provider.id,
            idAtProvider="autre_magnifik_id",
            name="Lecture de la Magnifique",
            offererAddress=offerer_address,
        )
        stock_of_the_offer_with_address = offers_factories.EventStockFactory(
            offer=offer_with_address, idAtProviders="autre_stock_id"
        )

        # Internal bookings
        booking_creation_date = datetime.datetime(2024, 5, 12)
        booking_of_the_offer_with_adress = bookings_factories.BookingFactory(
            stock=stock_of_the_offer_with_address, dateCreated=booking_creation_date, quantity=2
        )
        booking_of_the_offer_without_address = bookings_factories.BookingFactory(
            stock=stock_of_the_offer_without_address, dateCreated=booking_creation_date, quantity=2
        )
        user = user_factories.BeneficiaryFactory(firstName="Jean", lastName="Passedemeyeur")

        # book external tickets
        book_event_ticket(
            booking_of_the_offer_without_address,
            stock_of_the_offer_without_address,
            user,
        )
        external_call_body = json.loads(requests_post.call_args_list[0].kwargs["json"])
        assert external_call_body["venue_address"] == offer_without_address.venue.offererAddress.address.street
        assert external_call_body["venue_name"] == offer_without_address.venue.name
        assert (
            external_call_body["venue_department_code"]
            == offer_without_address.venue.offererAddress.address.departmentCode
        )

        book_event_ticket(
            booking_of_the_offer_with_adress,
            stock_of_the_offer_with_address,
            user,
        )
        external_call_body = json.loads(requests_post.call_args_list[1].kwargs["json"])

        assert external_call_body["venue_address"] == offerer_address.address.street
        assert external_call_body["venue_name"] == offerer_address.label
        assert external_call_body["venue_department_code"] == offerer_address.address.departmentCode


@pytest.mark.usefixtures("db_session")
class CancelEventTicketTest:
    def test_should_raise_an_error_because_there_is_no_ticketing_service_set(self):
        provider = providers_factories.ProviderFactory()
        offer = offers_factories.EventOfferFactory(
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP, lastProviderId=provider.id
        )
        stock = offers_factories.EventStockFactory(offer=offer)
        bookings_factories.BookingFactory(stock=stock, dateCreated=datetime.datetime(2024, 5, 12), quantity=2)

        # book
        with pytest.raises(external_bookings_exceptions.ExternalBookingException):
            cancel_event_ticket(
                barcodes=["ABCDEF"],
                provider=provider,
                stock=stock,
                is_booking_saved=True,
                venue_provider=None,
            )

    @patch("pcapi.core.external_bookings.api.requests.post")
    def test_should_successfully_cancel_an_event_ticket(self, requests_post):
        booking_creation_date = datetime.datetime(2024, 5, 12)
        provider = providers_factories.PublicApiProviderFactory()
        offer = offers_factories.EventOfferFactory(
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
            lastProviderId=provider.id,
        )
        stock = offers_factories.EventStockFactory(
            offer=offer,
        )
        bookings_factories.BookingFactory(stock=stock, dateCreated=booking_creation_date, quantity=2)

        # expected data
        expected_json_string = json.dumps({"barcodes": ["ABCDEF"]})
        expected_hmac_signature = generate_hmac_signature(provider.hmacKey, expected_json_string)

        # mocks
        requests_post.return_value.status_code = 200
        requests_post.return_value.json.return_value = {
            "remainingQuantity": 10,
        }

        # book
        cancel_event_ticket(
            barcodes=["ABCDEF"],
            provider=provider,
            stock=stock,
            is_booking_saved=True,
            venue_provider=None,
        )

        # checks
        requests_post.assert_called_with(
            provider.bookingExternalUrl,
            json=expected_json_string,
            hmac=expected_hmac_signature,
            headers={"Content-Type": "application/json"},
            timeout=EXTERNAL_BOOKINGS_TIMEOUT_IN_SECONDS,
            record_metrics=True,
            metric_name_suffix="external_booking_cancel",
        )

    @pytest.mark.parametrize("return_value", [{"remainingQuantity": 10}, {}])
    @patch("pcapi.core.external_bookings.api.requests.post")
    def test_should_successfully_cancel_an_event_ticket_using_venue_cancel_url(self, requests_post, return_value):
        booking_creation_date = datetime.datetime(2024, 5, 12)
        provider = providers_factories.PublicApiProviderFactory()
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(venue=venue, provider=provider)
        providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider, bookingExternalUrl="https://coucou.com", cancelExternalUrl="https://bye.co"
        )
        offer = offers_factories.EventOfferFactory(
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
            lastProviderId=provider.id,
            id=42,
            venueId=venue.id,
        )
        stock = offers_factories.EventStockFactory(
            offer=offer,
        )
        bookings_factories.BookingFactory(stock=stock, dateCreated=booking_creation_date, quantity=2)

        # expected data
        expected_json_string = json.dumps({"barcodes": ["ABCDEF"]})
        expected_hmac_signature = generate_hmac_signature(provider.hmacKey, expected_json_string)

        # mocks
        requests_post.return_value.status_code = 200
        requests_post.return_value.json.return_value = return_value

        # book
        cancel_event_ticket(
            barcodes=["ABCDEF"],
            provider=provider,
            stock=stock,
            is_booking_saved=True,
            venue_provider=venue_provider,
        )

        # checks
        requests_post.assert_called_with(
            "https://bye.co",
            json=expected_json_string,
            hmac=expected_hmac_signature,
            headers={"Content-Type": "application/json"},
            timeout=EXTERNAL_BOOKINGS_TIMEOUT_IN_SECONDS,
            record_metrics=True,
            metric_name_suffix="external_booking_cancel",
        )


@pytest.mark.usefixtures("db_session")
class SendBookingNotificationToExternalServiceTest:
    @patch("pcapi.tasks.external_api_booking_notification_tasks.external_api_booking_notification_task.delay")
    def test_should_do_nothing_because_notification_info_not_properly_set(self, mock_test):
        provider = providers_factories.ProviderFactory()
        offer = offers_factories.OfferFactory(lastProviderId=provider.id)
        stock = offers_factories.EventStockFactory(
            offer=offer,
        )
        booking = bookings_factories.BookingFactory(stock=stock, quantity=2)

        send_booking_notification_to_external_service(booking=booking, action=BookingAction.BOOK)
        mock_test.assert_not_called()

    @patch("pcapi.tasks.external_api_booking_notification_tasks.external_api_booking_notification_task.delay")
    def test_should_do_nothing_because_booking_linked_to_ticketing_system(self, mock_test):
        provider = providers_factories.PublicApiProviderFactory()
        offer = offers_factories.EventOfferFactory(
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
            lastProviderId=provider.id,
        )
        stock = offers_factories.EventStockFactory(
            offer=offer,
        )
        booking = bookings_factories.BookingFactory(stock=stock, quantity=2)

        send_booking_notification_to_external_service(booking=booking, action=BookingAction.BOOK)
        mock_test.assert_not_called()

    @patch("pcapi.tasks.external_api_booking_notification_tasks.external_api_booking_notification_task.delay")
    def test_should_send_notification_to_provider_notification_url(self, mocked_task):
        provider = providers_factories.PublicApiProviderFactory(notificationExternalUrl="https://myprovider.com/notif")
        booking_creation_date = datetime.datetime(2024, 5, 12)
        venue = offerers_factories.VenueFactory()
        offer = offers_factories.OfferFactory(
            venue=venue,
            lastProviderId=provider.id,
            idAtProvider="une_offre_de_grand_malade",
            id=42,
            name="Moins 50 pour cent sur tous les Marc Lévy !",
            ean="1234567890123",
        )
        stock = offers_factories.StockFactory(
            offer=offer, idAtProviders="bro_si_ty_vas_pas_direct_ça_va_te_passer_sous_nez_c_marc_lévy_qd_meme"
        )
        user = user_factories.BeneficiaryFactory(
            firstName="Jean",
            lastName="Potte",
        )
        booking = bookings_factories.BookingFactory(
            user=user, stock=stock, dateCreated=booking_creation_date, quantity=1
        )

        send_booking_notification_to_external_service(booking=booking, action=BookingAction.BOOK)

        mocked_task.assert_called()
        assert mocked_task.call_count == 1

        payload = mocked_task.call_args.args[0].data
        notificationUrl = mocked_task.call_args.args[0].notificationUrl

        # Payload data
        assert payload.booking_creation_date == booking.dateCreated
        assert payload.booking_quantity == 1
        assert payload.offer_ean == "1234567890123"
        assert payload.offer_id == 42
        assert payload.offer_id_at_provider == "une_offre_de_grand_malade"
        assert payload.offer_name == "Moins 50 pour cent sur tous les Marc Lévy !"
        assert payload.offer_price == 1010
        assert payload.price_category_id == None
        assert payload.price_category_label == None
        assert payload.stock_id == stock.id
        assert payload.stock_id_at_provider == "bro_si_ty_vas_pas_direct_ça_va_te_passer_sous_nez_c_marc_lévy_qd_meme"
        assert payload.user_birth_date == user.dateOfBirth.date()
        assert payload.user_email == user.email
        assert payload.user_first_name == "Jean"
        assert payload.user_last_name == "Potte"
        assert payload.user_phone == user.phoneNumber
        assert payload.venue_address == venue.offererAddress.address.street
        assert payload.venue_department_code == venue.offererAddress.address.departmentCode
        assert payload.venue_id == venue.id
        assert payload.venue_name == venue.name
        assert payload.action == BookingAction.BOOK

        # Notification Url
        assert notificationUrl == "https://myprovider.com/notif"

    @patch("pcapi.tasks.external_api_booking_notification_tasks.external_api_booking_notification_task.delay")
    def test_should_send_notification_to_venue_provider_notification_url(self, mocked_task):
        provider = providers_factories.PublicApiProviderFactory(notificationExternalUrl="https://myprovider.com/notif")
        booking_creation_date = datetime.datetime(2024, 5, 12)
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(venue=venue, provider=provider)
        providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider, notificationExternalUrl="https://myvenue.com/notif"
        )
        offer = offers_factories.OfferFactory(venue=venue, lastProviderId=provider.id)
        stock = offers_factories.StockFactory(offer=offer)
        booking = bookings_factories.BookingFactory(stock=stock, dateCreated=booking_creation_date, quantity=1)

        send_booking_notification_to_external_service(booking=booking, action=BookingAction.BOOK)

        mocked_task.assert_called()
        assert mocked_task.call_count == 1

        # Notification Url
        notificationUrl = mocked_task.call_args.args[0].notificationUrl
        assert notificationUrl == "https://myvenue.com/notif"
