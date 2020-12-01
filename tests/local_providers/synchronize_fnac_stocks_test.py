import pytest
import requests_mock

from pcapi.core.bookings.factories import BookingFactory
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import factories
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.offers.models import Offer
from pcapi.core.testing import override_settings
from pcapi.local_providers.fnac import synchronize_fnac_stocks
from pcapi.models import ThingType
from pcapi.models.product import Product


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
fnac_responses = [
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
            {"ref": ISBNs[7], "price": 28.989},
        ],
    },
    {"total": 3, "limit": 3, "offset": 4, "stocks": []},
]


def create_product(isbn, **kwargs):
    return factories.ProductFactory(idAtProviders=isbn, type=str(ThingType.LIVRE_EDITION), **kwargs)


def create_offer(isbn, siret):
    return factories.OfferFactory(product=create_product(isbn), idAtProviders=f"{isbn}@{siret}")


def create_stock(isbn, siret, **kwargs):
    return factories.StockFactory(offer=create_offer(isbn, siret), idAtProviders=f"{isbn}@{siret}", **kwargs)


class FnacCronTest:
    @pytest.mark.usefixtures("db_session")
    @override_settings(FNAC_API_URL="https://fnac_url", FNAC_API_TOKEN="fake_token")
    def test_execution(self):
        # Given
        venue_provider = offerers_factories.VenueProviderFactory(isActive=True)
        siret = venue_provider.venue.siret

        stock = create_stock(ISBNs[0], siret, quantity=20)
        offer = create_offer(ISBNs[1], siret)
        product = create_product(ISBNs[2])
        create_product(ISBNs[4])
        create_product(ISBNs[6], isGcuCompatible=False)

        stock_with_booking = create_stock(ISBNs[5], siret, quantity=20)
        BookingFactory(stock=stock_with_booking)
        BookingFactory(stock=stock_with_booking, quantity=2)

        # When
        with requests_mock.Mocker() as request_mock:
            request_mock.get(
                f"https://fnac_url/{siret}?limit=1000",
                [{"json": r, "headers": {"content-type": "application/json"}} for r in fnac_responses],
                request_headers={
                    "Authorization": "Basic fake_token",
                },
            )
            synchronize_fnac_stocks.synchronize_venue_stocks_from_fnac(venue_provider.venue)

        # Then
        # Test updates stock if already exists
        assert stock.quantity == 6

        # Test creates stock if does not exist
        assert len(offer.stocks) == 1
        created_stock = offer.stocks[0]
        assert created_stock.quantity == 4

        # Test creates offer if does not exist
        created_offer = Offer.query.filter_by(idAtProviders=f"{ISBNs[2]}@{siret}").one()
        assert created_offer.stocks[0].quantity == 18

        # Test doesn't create offer if product does not exist or not gcu compatible
        assert Offer.query.filter_by(idAtProviders=f"{ISBNs[3]}@{siret}").count() == 0
        assert Offer.query.filter_by(idAtProviders=f"{ISBNs[6]}@{siret}").count() == 0

        # Test second page is actually processed
        assert Offer.query.filter_by(idAtProviders=f"{ISBNs[4]}@{siret}").count() == 1

        # Test existing bookings are added to quantity
        assert stock_with_booking.quantity == 17 + 1 + 2

        # Test fill stock attributes
        assert created_stock.price == 30
        assert created_stock.idAtProviders == f"{ISBNs[1]}@{siret}"

        # Test override stock price attribute
        assert stock.price == 35

        # Test fill offers attributes
        assert created_offer.bookingEmail == venue_provider.venue.bookingEmail
        assert created_offer.description == product.description
        assert created_offer.extraData == product.extraData
        assert created_offer.name == product.name
        assert created_offer.productId == product.id
        assert created_offer.venueId == venue_provider.venue.id
        assert created_offer.type == product.type
        assert created_offer.idAtProviders == f"{ISBNs[2]}@{siret}"

    def test_build_stock_details_from_raw_stocks(self):
        # Given
        raw_stocks = [
            {"ref": ISBNs[4], "available": 17, "price": 23.989},
            {"ref": ISBNs[5], "available": 17, "price": 28.989},
        ]

        # When
        result = synchronize_fnac_stocks._build_stock_details_from_raw_stocks(raw_stocks, "siret")

        # Then
        assert result == [
            {
                "available_quantity": 17,
                "offers_fnac_reference": "3010000108123@siret",
                "price": 23.989,
                "products_fnac_reference": "3010000108123",
                "stocks_fnac_reference": "3010000108123@siret",
            },
            {
                "available_quantity": 17,
                "offers_fnac_reference": "3010000108124@siret",
                "price": 28.989,
                "products_fnac_reference": "3010000108124",
                "stocks_fnac_reference": "3010000108124@siret",
            },
        ]

    def test_build_new_offers_from_stock_details(self, db_session):
        # Given
        stock_details = [
            {
                "offers_fnac_reference": "offer_ref1",
            },
            {
                "available_quantity": 17,
                "offers_fnac_reference": "offer_ref_2",
                "price": 28.989,
                "products_fnac_reference": "product_ref",
                "stocks_fnac_reference": "stock_ref",
            },
        ]

        existing_offers_by_fnac_reference = {"offer_ref1"}
        venue = VenueFactory(bookingEmail="booking_email")
        product = Product(
            id=456, name="product_name", description="product_desc", extraData="extra", type="product_type"
        )
        products_by_fnac_reference = {"product_ref": product}

        # When
        new_offers = synchronize_fnac_stocks._build_new_offers_from_stock_details(
            stock_details, existing_offers_by_fnac_reference, products_by_fnac_reference, venue
        )

        # Then
        assert new_offers == [
            Offer(
                bookingEmail="booking_email",
                description="product_desc",
                extraData="extra",
                idAtProviders="offer_ref_2",
                name="product_name",
                productId=456,
                venueId=venue.id,
                type="product_type",
            )
        ]
