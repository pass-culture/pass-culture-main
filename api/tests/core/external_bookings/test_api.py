import datetime
import json
from unittest.mock import patch

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.utils import generate_hmac_signature
from pcapi.core.external_bookings.api import _get_external_bookings_client_api
from pcapi.core.external_bookings.api import book_event_ticket
from pcapi.core.external_bookings.api import get_active_cinema_venue_provider
from pcapi.core.external_bookings.cds.client import CineDigitalServiceAPI
import pcapi.core.external_bookings.exceptions as external_bookings_exceptions
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.exceptions as providers_exceptions
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.repository import get_provider_by_local_class
import pcapi.core.users.factories as user_factories


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
        with pytest.raises(providers_exceptions.InactiveProvider) as exc:
            get_active_cinema_venue_provider(venue_id)

        # Then
        assert str(exc.value) == f"No active cinema venue provider found for venue #{venue_id}"

    def test_should_raise_exception_if_inactive_cinema_venue_provider(self) -> None:
        cds_provider = get_provider_by_local_class("CDSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cds_provider, isActive=False)
        providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)

        venue_id = venue_provider.venueId
        with pytest.raises(providers_exceptions.InactiveProvider) as e:
            get_active_cinema_venue_provider(venue_id)

        assert str(e.value) == f"No active cinema venue provider found for venue #{venue_id}"


@pytest.mark.usefixtures("db_session")
class GetExternalBookingsClientApiTest:
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
        client_api = _get_external_bookings_client_api(venue_id)

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
            _get_external_bookings_client_api(venue_id)

        # Then
        assert str(e.value) == "No row was found when one was required"


@pytest.mark.usefixtures("db_session")
class BookEventTicketTest:

    @patch("pcapi.core.external_bookings.api.requests.post")
    def test_should_successfully_book_an_event_ticket(self, requests_post):
        booking_creation_date = datetime.datetime(2024, 5, 12)
        provider = providers_factories.PublicApiProviderFactory()
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
                "price_category_label": "Tarif unique",
                "stock_id": stock.id,
                "stock_id_at_provider": "roi_des_forêts!",
                "user_birth_date": user.dateOfBirth.strftime("%Y-%m-%d"),
                "user_email": user.email,
                "user_first_name": "Jean",
                "user_last_name": "Passedemeyeur",
                "user_phone": user.phoneNumber,
                "venue_address": "1 boulevard Poissonnière",
                "venue_department_code": "75",
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
        tickets, remaining_quantity = book_event_ticket(booking, stock, user, provider, None)

        # checks
        requests_post.assert_called_with(
            provider.bookingExternalUrl,
            json=expected_json_string,
            hmac=expected_hmac_signature,
            headers={"Content-Type": "application/json"},
        )
        assert remaining_quantity == 12
        assert [ticket.barcode for ticket in tickets] == ["1234567AJSQ", "1234567AJSA"]

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
            venueId=venue.id,
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
                "price_category_label": "Tarif unique",
                "stock_id": stock.id,
                "stock_id_at_provider": "roi_des_forêts!",
                "user_birth_date": user.dateOfBirth.strftime("%Y-%m-%d"),
                "user_email": user.email,
                "user_first_name": "Jean",
                "user_last_name": "Passedemeyeur",
                "user_phone": user.phoneNumber,
                "venue_address": "1 boulevard Poissonnière",
                "venue_department_code": "75",
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
        book_event_ticket(booking, stock, user, provider, venue_provider)

        # checks
        requests_post.assert_called_with(
            "https://coucou.com",
            json=expected_json_string,
            hmac=expected_hmac_signature,
            headers={"Content-Type": "application/json"},
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
            book_event_ticket(booking, stock, user, provider, None)

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
            book_event_ticket(booking, stock, user, provider, None)

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
            book_event_ticket(booking, stock, user, provider, None)

        assert str(error.value) == "External booking failed with status code 500 and message on est en carafe !!"
