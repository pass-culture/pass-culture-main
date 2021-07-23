from decimal import Decimal
from unittest import mock

from freezegun.api import freeze_time
import pytest
import requests_mock

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.categories import subcategories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import factories
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.offers.models import Offer
from pcapi.local_providers.provider_api import synchronize_provider_api


ISBNs = [
    "3010000101789",
    "3010000101797",
    "3010000103769",
    "3010000107163",
    "3010000108123",
    "3010000108124",
    "3010000108125",
    "3010000108126",
]
provider_responses = [
    {
        "total": len(ISBNs),
        "limit": 4,
        "offset": 0,
        "stocks": [
            {"ref": ISBNs[0], "available": 6, "price": 35.000},
            {"ref": ISBNs[1], "available": 4, "price": 30.000},
            {"ref": ISBNs[2], "available": 18, "price": 17.905},
            {"ref": ISBNs[3], "available": 12, "price": 26.989},
        ],
    },
    {
        "total": len(ISBNs),
        "limit": 4,
        "offset": 4,
        "stocks": [
            {"ref": ISBNs[4], "available": 17, "price": 23.989},
            {"ref": ISBNs[5], "available": 17, "price": 28.989},
            {"ref": ISBNs[6], "available": 17, "price": 28.989},
            {"ref": ISBNs[6], "available": 17, "price": 28.989},
            {"ref": ISBNs[7], "price": 28.989},
        ],
    },
    {"total": 3, "limit": 3, "offset": 4, "stocks": []},
]


def create_product(isbn, product_price, **kwargs):
    return factories.ProductFactory(
        idAtProviders=isbn,
        subcategoryId=subcategories.LIVRE_PAPIER.id,
        extraData={"prix_livre": product_price},
        **kwargs,
    )


def create_offer(isbn, siret, product_price):
    return factories.OfferFactory(
        product=create_product(isbn, product_price), idAtProviders=f"{isbn}@{siret}", idAtProvider=isbn
    )


def create_stock(isbn, siret, product_price, **kwargs):
    return factories.StockFactory(
        offer=create_offer(isbn, siret, product_price), idAtProviders=f"{isbn}@{siret}", **kwargs
    )


class ProviderAPICronTest:
    @pytest.mark.usefixtures("db_session")
    @freeze_time("2020-10-15 09:00:00")
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_execution(self, mocked_async_index_offer_ids):
        # Given
        provider = offerers_factories.APIProviderFactory(apiUrl="https://provider_url", authToken="fake_token")
        venue = VenueFactory(withdrawalDetails="Modalité de retrait")
        venue_provider = offerers_factories.VenueProviderFactory(
            isActive=True,
            provider=provider,
            venue=venue,
        )
        siret = venue_provider.venue.siret

        stock = create_stock(
            ISBNs[0],
            siret,
            quantity=20,
            product_price="5.01",
        )
        offer = create_offer(ISBNs[1], siret, product_price="5.02")
        product = create_product(ISBNs[2], product_price="8.01")
        create_product(ISBNs[4], product_price="10.02")
        create_product(ISBNs[6], isGcuCompatible=False, product_price="10.04")

        stock_with_booking = create_stock(ISBNs[5], siret, quantity=20, product_price="18.01")
        BookingFactory(stock=stock_with_booking)
        BookingFactory(stock=stock_with_booking, quantity=2)

        # When
        with requests_mock.Mocker() as request_mock:
            request_mock.get(
                f"https://provider_url/{siret}?limit=1000",
                [{"json": r, "headers": {"content-type": "application/json"}} for r in provider_responses],
                request_headers={
                    "Authorization": "Basic fake_token",
                },
            )
            synchronize_provider_api.synchronize_venue_provider(venue_provider)

        # Then
        # Test updates stock if already exists
        assert stock.quantity == 6
        assert stock.rawProviderQuantity == 6
        assert stock.lastProviderId == provider.id

        # Test creates stock if does not exist
        assert len(offer.stocks) == 1
        created_stock = offer.stocks[0]
        assert created_stock.quantity == 4
        assert created_stock.rawProviderQuantity == 4
        assert created_stock.lastProviderId == provider.id

        # Test creates offer if does not exist
        created_offer = Offer.query.filter_by(idAtProviders=f"{ISBNs[2]}@{siret}").one()
        assert created_offer.stocks[0].quantity == 18

        # Test doesn't create offer if product does not exist or not gcu compatible
        assert Offer.query.filter_by(idAtProviders=f"{ISBNs[3]}@{siret}").count() == 0
        assert Offer.query.filter_by(idAtProviders=f"{ISBNs[6]}@{siret}").count() == 0

        # Test second page is actually processed
        second_created_offer = Offer.query.filter_by(idAtProviders=f"{ISBNs[4]}@{siret}").one()
        assert second_created_offer.stocks[0].quantity == 17

        # Test existing bookings are added to quantity
        assert stock_with_booking.quantity == 17 + 1 + 2
        assert stock_with_booking.rawProviderQuantity == 17

        # Test fill stock attributes
        assert created_stock.price == Decimal("30")
        assert created_stock.idAtProviders == f"{ISBNs[1]}@{siret}"

        # Test override stock price attribute
        assert stock.price == Decimal("35")

        # Test fill offers attributes
        assert created_offer.bookingEmail == venue_provider.venue.bookingEmail
        assert created_offer.description == product.description
        assert created_offer.extraData == product.extraData
        assert created_offer.name == product.name
        assert created_offer.productId == product.id
        assert created_offer.venueId == venue_provider.venue.id
        assert created_offer.type == product.type
        assert created_offer.idAtProviders == f"{ISBNs[2]}@{siret}"
        assert created_offer.idAtProvider == ISBNs[2]
        assert created_offer.lastProviderId == provider.id
        assert created_offer.withdrawalDetails == venue_provider.venue.withdrawalDetails

        # Test update existing offers attributes
        assert stock.offer.lastProviderId == provider.id

        # Test it adds offer in redis
        assert mocked_async_index_offer_ids.mock_calls == [
            mock.call({offer.id, created_offer.id, stock.offer.id}),
            mock.call({stock_with_booking.offer.id, second_created_offer.id}),
        ]

        # Ensure next synchronisation is done with modifiedSince parameter
        with requests_mock.Mocker() as request_mock:
            request_mock.get(
                f"https://provider_url/{siret}?limit=1000&modifiedSince=2020-10-15T09%3A00%3A00Z",
                [{"json": r, "headers": {"content-type": "application/json"}} for r in provider_responses],
                request_headers={
                    "Authorization": "Basic fake_token",
                },
            )
            synchronize_provider_api.synchronize_venue_provider(venue_provider)

    @pytest.mark.usefixtures("db_session")
    class BuildStocksDetailsTest:
        def test_build_stock_details_from_raw_stocks(self):
            # Given
            raw_stocks = [
                {"ref": ISBNs[4], "available": 17, "price": 23.99},
                {"ref": ISBNs[5], "available": 17, "price": 28.99},
            ]

            # When
            provider = offerers_factories.ProviderFactory()
            result = synchronize_provider_api._build_stock_details_from_raw_stocks(raw_stocks, "siret", provider)

            # Then
            assert result == [
                {
                    "available_quantity": 17,
                    "offers_provider_reference": "3010000108123@siret",
                    "price": Decimal("23.99"),
                    "products_provider_reference": "3010000108123",
                    "stocks_provider_reference": "3010000108123@siret",
                },
                {
                    "available_quantity": 17,
                    "offers_provider_reference": "3010000108124@siret",
                    "price": Decimal("28.99"),
                    "products_provider_reference": "3010000108124",
                    "stocks_provider_reference": "3010000108124@siret",
                },
            ]

        def test_build_stock_details_from_raw_stocks_excludes_duplicates(self):
            # Given
            raw_stocks = [
                {"ref": ISBNs[4], "available": 17, "price": 23.99},
                {"ref": ISBNs[4], "available": 17, "price": 28.99},
            ]

            # When
            provider = offerers_factories.ProviderFactory()
            result = synchronize_provider_api._build_stock_details_from_raw_stocks(raw_stocks, "siret", provider)

            # Then
            assert result == [
                {
                    "available_quantity": 17,
                    "price": Decimal("28.99"),  # latest wins
                    "offers_provider_reference": "3010000108123@siret",
                    "products_provider_reference": "3010000108123",
                    "stocks_provider_reference": "3010000108123@siret",
                },
            ]

        def test_build_stock_details_with_euro_cents(self):
            # Given
            raw_stocks = [
                {"ref": ISBNs[4], "available": 17, "price": 1234},
                {"ref": ISBNs[4], "available": 17, "price": 1234},
            ]

            # When
            provider = offerers_factories.ProviderFactory(pricesInCents=True)
            result = synchronize_provider_api._build_stock_details_from_raw_stocks(raw_stocks, "siret", provider)

            # Then
            assert result == [
                {
                    "available_quantity": 17,
                    "price": Decimal("12.34"),  # latest wins
                    "offers_provider_reference": "3010000108123@siret",
                    "products_provider_reference": "3010000108123",
                    "stocks_provider_reference": "3010000108123@siret",
                },
            ]
